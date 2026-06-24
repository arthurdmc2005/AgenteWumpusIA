import numpy as np
import random


class Ambiente:
    """
    Representa o ambiente do Mundo de Wumpus.
    """

    def __init__(self, n, num_pocos=None, wumpus_movel=True, densidade_pocos=0.125):
        self.n = n
        self.densidade_pocos = densidade_pocos
        self.num_pocos = self.calcular_num_pocos() if num_pocos is None else num_pocos
        self.wumpus_movel = wumpus_movel

        self.wumpus_pos = None
        self.wumpus_vivo = True
        self.ouro_pos = None
        self.pocos = set()
        self.agente_pos = (0, 0)

        self.grid = np.zeros((self.n, self.n), dtype=int)
        self.gerar_tabuleiro()

    def calcular_num_pocos(self):
        """
        Define a quantidade de pocos proporcional ao tamanho do mapa.
        """
        total_casas = self.n * self.n
        return max(1, round(total_casas * self.densidade_pocos))

    def gerar_tabuleiro(self):
        """
        Gera o tabuleiro aleatoriamente, mantendo a saida segura.
        """
        todas_posicoes = [(r, c) for r in range(self.n) for c in range(self.n)]
        pos_iniciais_seguras = {(0, 0), (0, 1), (1, 0)}
        candidatos = [p for p in todas_posicoes if p not in pos_iniciais_seguras]

        if len(candidatos) < self.num_pocos + 2:
            pos_iniciais_seguras = {(0, 0)}
            candidatos = [p for p in todas_posicoes if p not in pos_iniciais_seguras]

        self.wumpus_vivo = True
        self.wumpus_pos = random.choice(candidatos)
        candidatos.remove(self.wumpus_pos)

        self.ouro_pos = random.choice(candidatos)
        candidatos.remove(self.ouro_pos)

        num_pocos_a_gerar = min(self.num_pocos, len(candidatos))
        self.pocos = set(random.sample(candidatos, num_pocos_a_gerar))

        self.atualizar_grid()

    def atualizar_grid(self):
        """
        Atualiza a representacao matricial do tabuleiro.
        """
        self.grid.fill(0)
        for r, c in self.pocos:
            self.grid[r, c] = 1

        if self.wumpus_vivo and self.wumpus_pos is not None:
            wr, wc = self.wumpus_pos
            self.grid[wr, wc] = 2

        or_pos, oc_pos = self.ouro_pos
        self.grid[or_pos, oc_pos] = 3

        ar, ac = self.agente_pos
        self.grid[ar, ac] = 4

    def vizinhos(self, pos):
        """
        Retorna os vizinhos ortogonais validos.
        """
        r, c = pos
        candidatos = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        return [(nr, nc) for nr, nc in candidatos if 0 <= nr < self.n and 0 <= nc < self.n]

    def get_percepcoes(self, pos):
        """
        Retorna as percepcoes do agente na celula atual.
        """
        brisa = False
        cheiro = False
        brilho = pos == self.ouro_pos

        for viz in self.vizinhos(pos):
            if viz in self.pocos:
                brisa = True
            if self.wumpus_vivo and viz == self.wumpus_pos:
                cheiro = True

        return {
            "brisa": brisa,
            "cheiro": cheiro,
            "brilho": brilho,
        }

    def mover_wumpus(self):
        """
        Move o Wumpus de forma aleatoria para um vizinho ortogonal valido.
        """
        if not self.wumpus_movel or not self.wumpus_vivo or self.wumpus_pos is None:
            return False

        vizinhos_validos = self.vizinhos(self.wumpus_pos)
        opcoes = [v for v in vizinhos_validos if v != (0, 0) and v not in self.pocos]

        if not opcoes:
            opcoes = [v for v in vizinhos_validos if v != (0, 0)]

        if opcoes:
            self.wumpus_pos = random.choice(opcoes)
            self.atualizar_grid()
            return True
        return False

    def atirar_flecha(self, origem, direcao):
        """
        Dispara uma flecha em linha reta ate sair do mapa.
        """
        if not self.wumpus_vivo or self.wumpus_pos is None:
            return False

        deltas = {
            "UP": (-1, 0),
            "DOWN": (1, 0),
            "LEFT": (0, -1),
            "RIGHT": (0, 1),
        }
        dr, dc = deltas[direcao]
        r, c = origem

        while True:
            r += dr
            c += dc
            if not (0 <= r < self.n and 0 <= c < self.n):
                return False
            if (r, c) == self.wumpus_pos:
                self.wumpus_vivo = False
                self.wumpus_pos = None
                self.atualizar_grid()
                return True
