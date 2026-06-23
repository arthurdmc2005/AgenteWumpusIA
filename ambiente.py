import numpy as np
import random

class Ambiente:
    """
    Representa o ambiente do Mundo de Wumpus.
    Mantém a matriz do tabuleiro, posições dos perigos (Wumpus, poços),
    posição do ouro e do agente, gerando as percepções de forma dinâmica.
    """
    def __init__(self, n, num_pocos=None, wumpus_movel=True):
        self.n = n
        if num_pocos is None:
            self.num_pocos = max(1, int((n * n) / 8))
        else:
            self.num_pocos = num_pocos
        self.wumpus_movel = wumpus_movel
        
        # Posições dos elementos do jogo
        self.wumpus_pos = None
        self.ouro_pos = None
        self.pocos = set()
        self.agente_pos = (0, 0)
        
        # Matriz para visualização / representação numérica
        # 0: Vazio, 1: Poço, 2: Wumpus, 3: Ouro, 4: Agente
        self.grid = np.zeros((self.n, self.n), dtype=int)
        
        self.gerar_tabuleiro()

    def gerar_tabuleiro(self):
        """
        Gera o tabuleiro aleatoriamente respeitando as restrições:
        - (0, 0) é a posição inicial segura do agente.
        - Os vizinhos diretos de (0, 0), ou seja, (0, 1) e (1, 0),
          idealmente não devem conter poços ou Wumpus para evitar morte imediata ou riscos diretos inevitáveis.
        """
        todas_posicoes = [(r, c) for r in range(self.n) for c in range(self.n)]
        
        # Zonas de segurança na largada
        pos_iniciais_seguras = {(0, 0), (0, 1), (1, 0)}
        
        # Candidatos para Wumpus e Ouro (fora da zona de largada segura)
        candidatos = [p for p in todas_posicoes if p not in pos_iniciais_seguras]
        
        # Caso o tabuleiro seja muito pequeno ou com muitos elementos e faltar espaço,
        # reduzimos a restrição de segurança apenas para (0, 0).
        if len(candidatos) < self.num_pocos + 2:
            pos_iniciais_seguras = {(0, 0)}
            candidatos = [p for p in todas_posicoes if p not in pos_iniciais_seguras]

        # Escolhe a posição do Wumpus
        self.wumpus_pos = random.choice(candidatos)
        candidatos.remove(self.wumpus_pos)
        
        # Escolhe a posição do Ouro
        self.ouro_pos = random.choice(candidatos)
        candidatos.remove(self.ouro_pos)
        
        # Escolhe as posições dos Poços
        num_pocos_a_gerar = min(self.num_pocos, len(candidatos))
        pocos_pos = random.sample(candidatos, num_pocos_a_gerar)
        self.pocos = set(pocos_pos)
        
        self.atualizar_grid()

    def atualizar_grid(self):
        """
        Atualiza a representação matricial do tabuleiro.
        """
        self.grid.fill(0)
        for (r, c) in self.pocos:
            self.grid[r, c] = 1
        
        wr, wc = self.wumpus_pos
        self.grid[wr, wc] = 2
        
        or_pos, oc_pos = self.ouro_pos
        self.grid[or_pos, oc_pos] = 3
        
        ar, ac = self.agente_pos
        self.grid[ar, ac] = 4

    def vizinhos(self, pos):
        """
        Retorna os vizinhos válidos (adjacentes ortogonais) de uma posição.
        """
        r, c = pos
        candidatos = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        return [(nr, nc) for (nr, nc) in candidatos if 0 <= nr < self.n and 0 <= nc < self.n]

    def get_percepcoes(self, pos):
        """
        Retorna as percepções do agente na célula atual:
        - brisa: se houver poço adjacente
        - cheiro: se o Wumpus estiver adjacente
        - brilho: se o ouro estiver na célula
        """
        brisa = False
        cheiro = False
        brilho = (pos == self.ouro_pos)
        
        for viz in self.vizinhos(pos):
            if viz in self.pocos:
                brisa = True
            if viz == self.wumpus_pos:
                cheiro = True
                
        return {
            "brisa": brisa,
            "cheiro": cheiro,
            "brilho": brilho
        }

    def mover_wumpus(self):
        """
        Move o Wumpus de forma aleatória para um vizinho ortogonal válido.
        O Wumpus não pode se mover para (0, 0) para evitar encurralar o agente na saída.
        Também evita cair em poços para manter o jogo consistente.
        """
        if not self.wumpus_movel:
            return
            
        vizinhos_validos = self.vizinhos(self.wumpus_pos)
        # Filtra vizinhos para evitar (0, 0) e poços
        opcoes = [v for v in vizinhos_validos if v != (0, 0) and v not in self.pocos]
        
        if not opcoes:
            # Se não houver opções seguras para o Wumpus se mover, ele tenta qualquer vizinho fora de (0, 0)
            opcoes = [v for v in vizinhos_validos if v != (0, 0)]
            
        if opcoes:
            self.wumpus_pos = random.choice(opcoes)
            self.atualizar_grid()
            return True
        return False
