from conhecimento import BaseConhecimento
from busca import a_estrela, heuristica

class Agente:
    """
    Controla o estado do agente, sua base de conhecimento, histórico de ações e
    lógica de decisão (baseada em inferências lógicas, busca A* e risco probabilístico).
    """
    def __init__(self, n, wumpus_movel=True):
        self.n = n
        self.wumpus_movel = wumpus_movel
        
        self.pos = (0, 0)
        self.has_gold = False
        self.alive = True
        self.vitorioso = False
        self.passos = 0
        
        # Histórico de posições visitadas na ordem atual
        self.historico = [(0, 0)]
        
        # Fila de movimentos planejados: lista de tuplas (r, c)
        self.caminho_atual = []
        
        # Modo de controle do agente: True = IA, False = Manual/Usuário
        self.modo_ia = False
        
        # Instancia a Base de Conhecimento
        self.kb = BaseConhecimento(n, wumpus_movel)
        
        # Log textual de ações (exibido na interface gráfica)
        self.log = ["Simulação iniciada.", "Agente posicionado em (0,0).", "Modo de controle: MANUAL (Teclado)"]

    def adicionar_log(self, mensagem):
        """
        Adiciona uma mensagem de log e limita o tamanho da lista para exibição na UI.
        """
        self.log.append(mensagem)
        if len(self.log) > 20:
            self.log.pop(0)

    def wumpus_moveu(self):
        """
        Notifica o agente e sua base de conhecimento de que o Wumpus se moveu.
        Garante o replanejamento caso o caminho traçado passe por áreas agora arriscadas.
        """
        self.kb.wumpus_moveu()
        self.adicionar_log("Wumpus se moveu! Atualizando mapa de risco...")
        
        # Verifica se o caminho planejado anteriormente ainda é seguro
        if self.caminho_atual:
            caminho_seguro = True
            for celula in self.caminho_atual:
                # O destino final pode ser uma célula sob risco, mas as intermediárias devem ser seguras
                if celula != self.caminho_atual[-1] and not self.kb.eh_segura(celula):
                    caminho_seguro = False
                    break
                    
            if not caminho_seguro:
                self.caminho_atual = []
                self.adicionar_log("Caminho cancelado: risco detectado devido à movimentação do Wumpus.")

    def agir(self, percepcao):
        """
        Executa um turno de ação do agente:
        1. Registra e atualiza a base de conhecimento.
        2. Verifica vitória ou morte.
        3. Decide o próximo movimento (reaproveitando caminho ou replanejando).
        """
        if not self.alive or self.vitorioso:
            return
            
        # Registra percepção da célula atual
        self.kb.registrar_percepcao(self.pos, percepcao)
        
        # Mensagem informativa sobre percepções na célula
        percs_str = []
        if percepcao["brisa"]: percs_str.append("Brisa")
        if percepcao["cheiro"]: percs_str.append("Cheiro")
        if percepcao["brilho"]: percs_str.append("Brilho")
        
        if percs_str:
            self.adicionar_log(f"Percepção em {self.pos}: " + ", ".join(percs_str))
        else:
            self.adicionar_log(f"Percepção em {self.pos}: Nenhuma")

        # Verifica Ouro
        if percepcao["brilho"] and not self.has_gold:
            self.has_gold = True
            self.adicionar_log("Ouro coletado! Planejando retorno à saída (0,0)...")
            self.caminho_atual = [] # Limpa planos anteriores

        # Se já tem o ouro e está em (0,0), ganha o jogo
        if self.pos == (0, 0) and self.has_gold:
            self.vitorioso = True
            self.adicionar_log("Agente escalou para fora com o ouro! VITÓRIA!")
            return

        # Se estiver em modo manual (controlado pelo usuário), não planeja rota nem se move sozinho
        if not self.modo_ia:
            return

        # Verifica se precisamos recalcular ou iniciar planejamento
        if not self.caminho_atual:
            self.planejar_rota()

        # Executa o próximo movimento da fila planejada
        if self.caminho_atual:
            proxima_pos = self.caminho_atual.pop(0)
            self.mover_para(proxima_pos)
        else:
            self.adicionar_log("Erro: Agente sem caminhos possíveis para explorar!")

    def mover_para(self, destino):
        """
        Efetivamente atualiza a posição do agente no tabuleiro.
        """
        origem = self.pos
        self.pos = destino
        self.passos += 1
        self.historico.append(destino)
        
        # Calcula direção do movimento
        dr = destino[0] - origem[0]
        dc = destino[1] - origem[1]
        
        direcao = ""
        if dr == -1: direcao = "Cima ↑"
        elif dr == 1: direcao = "Baixo ↓"
        elif dc == -1: direcao = "Esquerda ←"
        elif dc == 1: direcao = "Direita →"
        
        self.adicionar_log(f"Moveu-se para {destino} ({direcao})")

    def planejar_rota(self):
        """
        Determina a estratégia de destino do agente e planeja a rota até lá usando A*:
        1. Se tem ouro: volta para (0, 0).
        2. Se não tem ouro: procura a célula segura e não visitada mais próxima.
        3. Se não há célula segura não visitada: toma uma decisão sob risco escolhendo a de menor probabilidade.
        """
        celulas_seguras = self.kb.get_celulas_seguras()

        # Caso 1: Retornar para (0, 0) com o Ouro
        if self.has_gold:
            caminho = a_estrela(self.pos, (0, 0), celulas_seguras, self.n)
            if caminho:
                self.caminho_atual = caminho
                self.adicionar_log("Caminho de volta seguro planejado.")
                return
            else:
                # Se não há caminho 100% seguro (por causa de Wumpus móvel bloqueando),
                # tenta traçar o melhor caminho de menor risco até (0, 0)
                self.adicionar_log("Caminho de volta seguro bloqueado! Forçando rota com risco calculado.")
                self.planejar_caminho_risco((0, 0))
                return

        # Caso 2: Explorar Células Seguras Não Visitadas
        seguras_nao_visitadas = celulas_seguras - self.kb.visited
        
        if seguras_nao_visitadas:
            # Encontra a célula segura não visitada mais próxima (distância de Manhattan + A*)
            candidatas_ordenadas = sorted(list(seguras_nao_visitadas), key=lambda c: heuristica(self.pos, c))
            
            for cand in candidatas_ordenadas:
                caminho = a_estrela(self.pos, cand, celulas_seguras, self.n)
                if caminho:
                    self.caminho_atual = caminho
                    self.adicionar_log(f"Planejando exploração de célula segura em {cand}")
                    return
        
        # Caso 3: Nenhuma Célula Segura não visitada é alcançável -> Decisão sob Risco!
        # Encontra a "fronteira exploratória": células não visitadas adjacentes a células visitadas
        fronteira = set()
        for v in self.kb.visited:
            for viz in self.kb.vizinhos(v):
                if viz not in self.kb.visited:
                    fronteira.add(viz)
                    
        if fronteira:
            # Calcula probabilidade de risco para cada uma delas
            candidatas_risco = []
            for c in fronteira:
                prob_risco = self.kb.calcular_probabilidade_risco(c)
                candidatas_risco.append((prob_risco, heuristica(self.pos, c), c))
                
            # Ordena pelo menor risco, e depois pela menor distância física
            candidatas_risco.sort()
            
            melhor_risco, _, melhor_celula = candidatas_risco[0]
            
            self.adicionar_log(f"Nenhuma célula 100% segura disponível.")
            self.adicionar_log(f"Melhor escolha de risco: {melhor_celula} com risco de {melhor_risco:.1%}")
            
            # Planeja rota até um vizinho visitado dessa célula de menor risco, depois entra nela
            self.planejar_caminho_risco(melhor_celula)
        else:
            self.adicionar_log("Sem opções de fronteira! Agente encurralado.")

    def planejar_caminho_risco(self, destino):
        """
        Planeja um caminho até a célula 'destino' que passa por células seguras até
        o último passo (onde entra no risco).
        """
        celulas_seguras = self.kb.get_celulas_seguras()
        # Executa o A* que aceita que a última célula ('destino') não seja necessariamente segura.
        caminho = a_estrela(self.pos, destino, celulas_seguras, self.n)
        if caminho:
            self.caminho_atual = caminho
        else:
            # Em caso extremo onde nem os vizinhos são seguros de alcançar
            # (ex: Wumpus trancou o agente numa ilha de células perigosas)
            # Planeja uma busca A* direta ignorando as restrições de segurança
            # e escolhendo o caminho de menor risco acumulado.
            # Implementamos um fallback A* com custos baseados em risco.
            self.caminho_atual = self.busca_custo_risco(self.pos, destino)

    def busca_custo_risco(self, inicio, fim):
        """
        Busca fallback que encontra um caminho de risco mínimo até o destino.
        Cada célula tem custo 1.0 + risco * 100.
        """
        import heapq
        open_set = []
        heapq.heappush(open_set, (0, inicio))
        veio_de = {}
        g_score = {inicio: 0}
        
        while open_set:
            _, atual = heapq.heappop(open_set)
            if atual == fim:
                caminho = []
                curr = atual
                while curr in veio_de:
                    caminho.append(curr)
                    curr = veio_de[curr]
                caminho.reverse()
                return caminho
                
            r, c = atual
            vizinhos = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
            for viz in vizinhos:
                nr, nc = viz
                if 0 <= nr < self.n and 0 <= nc < self.n:
                    risco = self.kb.calcular_probabilidade_risco(viz)
                    custo_mov = 1.0 + risco * 100.0
                    tentative_g = g_score[atual] + custo_mov
                    if tentative_g < g_score.get(viz, float('inf')):
                        veio_de[viz] = atual
                        g_score[viz] = tentative_g
                        heapq.heappush(open_set, (tentative_g + heuristica(viz, fim), viz))
        return []
