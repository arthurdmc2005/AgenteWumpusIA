from conhecimento import BaseConhecimento
from busca import a_estrela, heuristica
from qlearning import AgenteQLearning


ACOES_Q_LEARNING = [
    "MOVER",
    "GIRAR_ESQUERDA",
    "GIRAR_DIREITA",
    "PEGAR_OURO",
    "ATIRAR",
]

Q_RECOMPENSAS = {
    "passo": -1.0,
    "celula_nova": 4.0,
    "aproximar_ouro": 1.0,
    "afastar_ouro": -0.5,
    "ouro": 80.0,
    "vitoria": 300.0,
    "morte": -250.0,
    "acao_invalida": -12.0,
    "atirar_wumpus": 50.0,
    "errar_tiro": -15.0,
}


class Agente:
    """
    Controla o estado do agente e sua tomada de decisao.
    """

    def __init__(self, n, wumpus_movel=True):
        self.n = n
        self.wumpus_movel = wumpus_movel

        self.pos = (0, 0)
        self.direcao = "RIGHT"
        self.has_gold = False
        self.has_arrow = True
        self.alive = True
        self.vitorioso = False
        self.passos = 0

        self.historico = [(0, 0)]
        self.caminho_atual = []
        self.modo_jogo = "humano"
        self.tipo_agente = "regras"
        self.treinamento_q = True
        self.modo_q_learning = "demonstracao"

        self.q_learning = AgenteQLearning(ACOES_Q_LEARNING)
        self.ultima_acao = "-"
        self.ultima_recompensa = 0.0
        self.ultimo_valor_q = 0.0
        self.ultima_fase_acao = "explorando"
        self.episodios = 1
        self.passos_episodio = 0
        self.logs_ativos = True

        self.kb = BaseConhecimento(n, wumpus_movel)
        self.log = [
            "Simulacao iniciada.",
            "Agente posicionado em (0,0).",
            "Modo de controle: MANUAL (Teclado)",
        ]

    @property
    def modo_ia(self):
        return self.modo_jogo == "agente"

    @modo_ia.setter
    def modo_ia(self, ativo):
        self.modo_jogo = "agente" if ativo else "humano"

    def adicionar_log(self, mensagem):
        if not self.logs_ativos:
            return
        self.log.append(mensagem)
        if len(self.log) > 20:
            self.log.pop(0)

    def configurar_modo_jogo(self, modo):
        if modo not in ("humano", "agente"):
            return
        self.modo_jogo = modo
        if modo == "humano":
            self.caminho_atual = []
        self.adicionar_log(f"Modo de jogo: {'Agente automatico' if self.modo_ia else 'Humano'}")

    def configurar_tipo_agente(self, tipo):
        if tipo not in ("regras", "q_learning"):
            return
        self.tipo_agente = tipo
        self.caminho_atual = []
        nome = "Q-Learning" if tipo == "q_learning" else "Baseado em regras"
        self.adicionar_log(f"Tipo de agente: {nome}")

    def alternar_treinamento_q(self):
        self.treinamento_q = not self.treinamento_q
        modo = "treino" if self.treinamento_q else "execucao"
        self.adicionar_log(f"Q-Learning em modo de {modo}.")

    def configurar_modo_q_learning(self, modo):
        if modo not in ("treino_rapido", "demonstracao", "passo_a_passo"):
            return
        self.modo_q_learning = modo
        nomes = {
            "treino_rapido": "treino rapido",
            "demonstracao": "demonstracao visual",
            "passo_a_passo": "passo a passo",
        }
        self.adicionar_log(f"Modo Q-Learning: {nomes[modo]}.")

    def reiniciar_treinamento_q(self):
        self.q_learning.reiniciar_treinamento()
        self.episodios = 1
        self.passos_episodio = 0
        self.ultima_acao = "-"
        self.ultima_recompensa = 0.0
        self.ultimo_valor_q = 0.0
        self.ultima_fase_acao = "explorando"
        self.adicionar_log("Treinamento Q-Learning reiniciado.")

    def herdar_aprendizado_de(self, outro_agente):
        self.modo_jogo = outro_agente.modo_jogo
        self.tipo_agente = outro_agente.tipo_agente
        self.treinamento_q = outro_agente.treinamento_q
        self.modo_q_learning = outro_agente.modo_q_learning
        self.q_learning = outro_agente.q_learning
        self.episodios = outro_agente.episodios
        self.ultima_acao = outro_agente.ultima_acao
        self.ultima_recompensa = outro_agente.ultima_recompensa
        self.ultimo_valor_q = outro_agente.ultimo_valor_q
        self.ultima_fase_acao = outro_agente.ultima_fase_acao

    def simbolo_direcao(self):
        simbolos = {
            "UP": "^",
            "DOWN": "v",
            "LEFT": "<",
            "RIGHT": ">",
        }
        return simbolos[self.direcao]

    def atualizar_direcao(self, origem, destino):
        dr = destino[0] - origem[0]
        dc = destino[1] - origem[1]
        if dr == -1:
            self.direcao = "UP"
        elif dr == 1:
            self.direcao = "DOWN"
        elif dc == -1:
            self.direcao = "LEFT"
        elif dc == 1:
            self.direcao = "RIGHT"

    def girar_para(self, direcao):
        if self.direcao != direcao:
            self.direcao = direcao
            nomes = {
                "UP": "Cima ^",
                "DOWN": "Baixo v",
                "LEFT": "Esquerda <",
                "RIGHT": "Direita >",
            }
            self.adicionar_log(f"Agente virou para {nomes[self.direcao]}")
            return True
        return False

    def wumpus_moveu(self):
        self.kb.wumpus_moveu()
        self.adicionar_log("Wumpus se moveu! Atualizando mapa de risco...")

        if self.caminho_atual:
            caminho_seguro = True
            for celula in self.caminho_atual:
                if celula != self.caminho_atual[-1] and not self.kb.eh_segura(celula):
                    caminho_seguro = False
                    break

            if not caminho_seguro:
                self.caminho_atual = []
                self.adicionar_log("Caminho cancelado: risco detectado devido a movimentacao do Wumpus.")

    def atirar_flecha(self, ambiente):
        if not self.alive or self.vitorioso:
            return False
        if not self.has_arrow:
            self.adicionar_log("Flecha indisponivel: o agente ja atirou.")
            return False

        self.has_arrow = False
        self.adicionar_log(f"Flecha disparada na direcao {self.simbolo_direcao()}.")

        acertou = ambiente.atirar_flecha(self.pos, self.direcao)
        if acertou:
            self.kb.matar_wumpus()
            self.caminho_atual = []
            self.adicionar_log("Acerto! O Wumpus foi abatido.")
        else:
            self.adicionar_log("A flecha nao atingiu o Wumpus.")
        return acertou

    def registrar_percepcao_atual(self, percepcao, registrar_log=True):
        self.kb.registrar_percepcao(self.pos, percepcao)
        if not registrar_log:
            return

        percs_str = []
        if percepcao["brisa"]:
            percs_str.append("Brisa")
        if percepcao["cheiro"]:
            percs_str.append("Cheiro")
        if percepcao["brilho"]:
            percs_str.append("Brilho")

        if percs_str:
            self.adicionar_log(f"Percepcao em {self.pos}: " + ", ".join(percs_str))
        else:
            self.adicionar_log(f"Percepcao em {self.pos}: Nenhuma")

    def estado_q_learning(self, percepcao, ambiente=None):
        direcoes = {"UP": 0, "RIGHT": 1, "DOWN": 2, "LEFT": 3}
        frente = self.proxima_posicao_frente()
        esquerda = self.posicao_na_direcao(self.direcao_esquerda())
        direita = self.posicao_na_direcao(self.direcao_direita())
        ouro_relativo = self.direcao_relativa_ouro(ambiente) if ambiente is not None else 0
        return (
            self.pos[0],
            self.pos[1],
            direcoes[self.direcao],
            int(percepcao["brisa"]),
            int(percepcao["cheiro"]),
            int(percepcao["brilho"]),
            int(self.has_gold),
            int(self.has_arrow),
            int(self.kb.wumpus_vivo),
            int(not self.posicao_valida(frente)),
            int(not self.posicao_valida(esquerda)),
            int(not self.posicao_valida(direita)),
            int(frente in self.kb.visited),
            self.contar_vizinhos_visitados(),
            ouro_relativo,
        )

    def passo_q_learning(self, ambiente, treinamento=None, registrar_log=True, finalizar_episodio=True):
        if not self.alive or self.vitorioso:
            return None

        if treinamento is None:
            treinamento = self.treinamento_q

        percepcao = ambiente.get_percepcoes(self.pos)
        self.registrar_percepcao_atual(percepcao, registrar_log=registrar_log)
        estado = self.estado_q_learning(percepcao, ambiente)
        acao, explorando = self.q_learning.escolher_acao(estado, treinamento=treinamento)

        recompensa, terminou, resultado = self.executar_acao_q_learning(acao, ambiente, registrar_log=registrar_log)

        proxima_percepcao = ambiente.get_percepcoes(self.pos) if self.alive else percepcao
        if self.alive and not self.vitorioso:
            self.registrar_percepcao_atual(proxima_percepcao, registrar_log=registrar_log)
        proximo_estado = self.estado_q_learning(proxima_percepcao, ambiente)

        if treinamento:
            self.q_learning.atualizar(estado, acao, recompensa, proximo_estado, terminou)

        self.ultima_acao = acao
        self.ultima_recompensa = recompensa
        self.ultimo_valor_q = self.q_learning.ultimo_valor_q
        self.ultima_fase_acao = "explorando" if explorando else "politica aprendida"
        self.q_learning.registrar_passo(recompensa)
        self.passos_episodio += 1
        if terminou and finalizar_episodio:
            self.q_learning.finalizar_episodio(resultado, aplicar_decay=treinamento)
            self.episodios = self.q_learning.episodio_atual
            self.passos_episodio = self.q_learning.passo_atual
        if registrar_log:
            self.adicionar_log(f"Q-Learning: acao={acao}, recompensa={recompensa:.1f}")
        return {
            "estado": estado,
            "acao": acao,
            "recompensa": recompensa,
            "proximo_estado": proximo_estado,
            "terminou": terminou,
            "resultado": resultado,
            "explorando": explorando,
        }

    def executar_acao_q_learning(self, acao, ambiente, registrar_log=True):
        recompensa = Q_RECOMPENSAS["passo"]
        terminou = False
        resultado = "em_andamento"

        if acao == "MOVER":
            destino = self.proxima_posicao_frente()
            if not self.posicao_valida(destino):
                recompensa += Q_RECOMPENSAS["acao_invalida"]
                self.passos += 1
                if registrar_log:
                    self.adicionar_log("Q-Learning tentou mover para fora do mapa.")
            else:
                destino_novo = destino not in self.kb.visited
                distancia_antes = self.distancia_ate_ouro(ambiente)
                self.mover_para(destino)
                ambiente.agente_pos = destino
                ambiente.atualizar_grid()
                if destino_novo:
                    recompensa += Q_RECOMPENSAS["celula_nova"]
                distancia_depois = self.distancia_ate_ouro(ambiente)
                if distancia_antes is not None and distancia_depois is not None:
                    if distancia_depois < distancia_antes:
                        recompensa += Q_RECOMPENSAS["aproximar_ouro"]
                    elif distancia_depois > distancia_antes:
                        recompensa += Q_RECOMPENSAS["afastar_ouro"]

                if self.pos in ambiente.pocos:
                    self.alive = False
                    recompensa += Q_RECOMPENSAS["morte"]
                    terminou = True
                    resultado = "morte"
                    if registrar_log:
                        self.adicionar_log("Morte: Agente caiu em um poco profundo!")
                elif self.pos == ambiente.wumpus_pos:
                    self.alive = False
                    recompensa += Q_RECOMPENSAS["morte"]
                    terminou = True
                    resultado = "morte"
                    if registrar_log:
                        self.adicionar_log("Morte: Agente foi devorado pelo Wumpus!")

        elif acao == "GIRAR_ESQUERDA":
            self.direcao = self.direcao_esquerda()
            self.passos += 1
            if registrar_log:
                self.adicionar_log(f"Q-Learning virou para {self.simbolo_direcao()}.")

        elif acao == "GIRAR_DIREITA":
            self.direcao = self.direcao_direita()
            self.passos += 1
            if registrar_log:
                self.adicionar_log(f"Q-Learning virou para {self.simbolo_direcao()}.")

        elif acao == "PEGAR_OURO":
            self.passos += 1
            if self.pos == ambiente.ouro_pos and not self.has_gold:
                self.has_gold = True
                recompensa += Q_RECOMPENSAS["ouro"]
                if registrar_log:
                    self.adicionar_log("Ouro coletado pelo Q-Learning!")
            else:
                recompensa += Q_RECOMPENSAS["acao_invalida"]
                if registrar_log:
                    self.adicionar_log("Q-Learning tentou pegar ouro onde nao havia ouro.")

        elif acao == "ATIRAR":
            self.passos += 1
            if not self.has_arrow:
                recompensa += Q_RECOMPENSAS["acao_invalida"]
                if registrar_log:
                    self.adicionar_log("Q-Learning tentou atirar sem flecha.")
            else:
                acertou = self.atirar_flecha(ambiente)
                recompensa += Q_RECOMPENSAS["atirar_wumpus"] if acertou else Q_RECOMPENSAS["errar_tiro"]

        if self.pos == (0, 0) and self.has_gold:
            self.vitorioso = True
            recompensa += Q_RECOMPENSAS["vitoria"]
            terminou = True
            resultado = "vitoria"
            if registrar_log:
                self.adicionar_log("Agente escalou para fora com o ouro! VITORIA!")

        return recompensa, terminou, resultado

    def proxima_posicao_frente(self):
        return self.posicao_na_direcao(self.direcao)

    def posicao_na_direcao(self, direcao):
        deltas = {
            "UP": (-1, 0),
            "DOWN": (1, 0),
            "LEFT": (0, -1),
            "RIGHT": (0, 1),
        }
        dr, dc = deltas[direcao]
        return self.pos[0] + dr, self.pos[1] + dc

    def posicao_valida(self, pos):
        return 0 <= pos[0] < self.n and 0 <= pos[1] < self.n

    def contar_vizinhos_visitados(self):
        r, c = self.pos
        vizinhos = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        return sum(1 for pos in vizinhos if pos in self.kb.visited)

    def distancia_ate_ouro(self, ambiente):
        if ambiente is None or ambiente.ouro_pos is None or self.has_gold:
            return None
        return heuristica(self.pos, ambiente.ouro_pos)

    def direcao_relativa_ouro(self, ambiente):
        if ambiente is None or ambiente.ouro_pos is None:
            return 0
        if self.has_gold:
            alvo = (0, 0)
        else:
            alvo = ambiente.ouro_pos
        dr = alvo[0] - self.pos[0]
        dc = alvo[1] - self.pos[1]
        if abs(dr) > abs(dc):
            direcao_alvo = "DOWN" if dr > 0 else "UP"
        elif dc != 0:
            direcao_alvo = "RIGHT" if dc > 0 else "LEFT"
        else:
            return 0
        if direcao_alvo == self.direcao:
            return 1
        if direcao_alvo == self.direcao_esquerda():
            return 2
        if direcao_alvo == self.direcao_direita():
            return 3
        return 4

    def direcao_esquerda(self):
        ordem = ["UP", "LEFT", "DOWN", "RIGHT"]
        return ordem[(ordem.index(self.direcao) + 1) % len(ordem)]

    def direcao_direita(self):
        ordem = ["UP", "RIGHT", "DOWN", "LEFT"]
        return ordem[(ordem.index(self.direcao) + 1) % len(ordem)]

    def agir(self, percepcao):
        if not self.alive or self.vitorioso:
            return

        self.registrar_percepcao_atual(percepcao)

        if percepcao["brilho"] and not self.has_gold:
            self.has_gold = True
            self.adicionar_log("Ouro coletado! Planejando retorno a saida (0,0)...")
            self.caminho_atual = []

        if self.pos == (0, 0) and self.has_gold:
            self.vitorioso = True
            self.adicionar_log("Agente escalou para fora com o ouro! VITORIA!")
            return

        if not self.modo_ia:
            return

        if not self.caminho_atual:
            self.planejar_rota()

        if self.caminho_atual:
            proxima_pos = self.caminho_atual.pop(0)
            self.mover_para(proxima_pos)
        else:
            self.adicionar_log("Erro: Agente sem caminhos possiveis para explorar!")

    def mover_para(self, destino):
        origem = self.pos
        self.atualizar_direcao(origem, destino)
        self.pos = destino
        self.passos += 1
        self.historico.append(destino)

        nomes = {
            "UP": "Cima ^",
            "DOWN": "Baixo v",
            "LEFT": "Esquerda <",
            "RIGHT": "Direita >",
        }
        self.adicionar_log(f"Moveu-se para {destino} ({nomes[self.direcao]})")

    def planejar_rota(self):
        celulas_seguras = self.kb.get_celulas_seguras()

        if self.has_gold:
            caminho = a_estrela(self.pos, (0, 0), celulas_seguras, self.n)
            if caminho:
                self.caminho_atual = caminho
                self.adicionar_log("Caminho de volta seguro planejado.")
                return
            self.adicionar_log("Caminho de volta seguro bloqueado! Forcando rota com risco calculado.")
            self.planejar_caminho_risco((0, 0))
            return

        seguras_nao_visitadas = celulas_seguras - self.kb.visited
        if seguras_nao_visitadas:
            candidatas_ordenadas = sorted(list(seguras_nao_visitadas), key=lambda c: heuristica(self.pos, c))
            for cand in candidatas_ordenadas:
                caminho = a_estrela(self.pos, cand, celulas_seguras, self.n)
                if caminho:
                    self.caminho_atual = caminho
                    self.adicionar_log(f"Planejando exploracao de celula segura em {cand}")
                    return

        fronteira = set()
        for v in self.kb.visited:
            for viz in self.kb.vizinhos(v):
                if viz not in self.kb.visited:
                    fronteira.add(viz)

        if fronteira:
            candidatas_risco = []
            for c in fronteira:
                prob_risco = self.kb.calcular_probabilidade_risco(c)
                candidatas_risco.append((prob_risco, heuristica(self.pos, c), c))

            candidatas_risco.sort()
            melhor_risco, _, melhor_celula = candidatas_risco[0]

            self.adicionar_log("Nenhuma celula 100% segura disponivel.")
            self.adicionar_log(f"Melhor escolha de risco: {melhor_celula} com risco de {melhor_risco:.1%}")
            self.planejar_caminho_risco(melhor_celula)
        else:
            self.adicionar_log("Sem opcoes de fronteira! Agente encurralado.")

    def planejar_caminho_risco(self, destino):
        celulas_seguras = self.kb.get_celulas_seguras()
        caminho = a_estrela(self.pos, destino, celulas_seguras, self.n)
        if caminho:
            self.caminho_atual = caminho
        else:
            self.caminho_atual = self.busca_custo_risco(self.pos, destino)

    def busca_custo_risco(self, inicio, fim):
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
                    if tentative_g < g_score.get(viz, float("inf")):
                        veio_de[viz] = atual
                        g_score[viz] = tentative_g
                        heapq.heappush(open_set, (tentative_g + heuristica(viz, fim), viz))
        return []
