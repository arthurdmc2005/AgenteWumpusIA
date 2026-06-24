import json
import random
import time
from collections import defaultdict, deque


class AgenteQLearning:
    """
    Q-Learning tabular com configuracao, persistencia e telemetria agregada.
    """

    def __init__(
        self,
        acoes,
        alpha=0.30,
        gamma=0.92,
        epsilon=0.80,
        epsilon_min=0.03,
        epsilon_decay=0.992,
        janela_metricas=50,
    ):
        self.acoes = list(acoes)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon_inicial = epsilon
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.q_table = defaultdict(self._linha_q_padrao)
        self.janela_metricas = janela_metricas
        self.resetar_metricas()

    def _linha_q_padrao(self):
        return {acao: 0.0 for acao in self.acoes}

    def resetar_metricas(self):
        self.episodio_atual = 1
        self.passo_atual = 0
        self.recompensa_episodio = 0.0
        self.melhor_recompensa = float("-inf")
        self.ultima_recompensa = 0.0
        self.ultima_acao = "-"
        self.ultimo_valor_q = 0.0
        self.ultimo_resultado = "em_andamento"
        self.vitorias = 0
        self.mortes = 0
        self.timeouts = 0
        self.total_episodios_finalizados = 0
        self.recompensas_recentes = deque(maxlen=self.janela_metricas)
        self.vitorias_recentes = deque(maxlen=self.janela_metricas)
        self.mortes_recentes = deque(maxlen=self.janela_metricas)
        self.passos_recentes = deque(maxlen=self.janela_metricas)
        self.epsilon_historico = deque(maxlen=self.janela_metricas)
        self.episodios_por_segundo = 0.0
        self.ultimo_lote_episodios = 0
        self.ultimo_lote_segundos = 0.0
        self._inicio_lote = time.perf_counter()

    def escolher_acao(self, estado, treinamento=True):
        explorando = treinamento and random.random() < self.epsilon
        if explorando:
            acao = random.choice(self.acoes)
        else:
            acao = self.melhor_acao(estado)

        self.ultima_acao = acao
        self.ultimo_valor_q = self.q_table[estado][acao]
        return acao, explorando

    def melhor_acao(self, estado):
        valores = self.q_table[estado]
        maior_valor = max(valores.values())
        melhores_acoes = [acao for acao, valor in valores.items() if valor == maior_valor]
        return random.choice(melhores_acoes)

    def atualizar(self, estado, acao, recompensa, proximo_estado, terminou):
        valor_atual = self.q_table[estado][acao]
        melhor_futuro = 0.0 if terminou else max(self.q_table[proximo_estado].values())
        alvo = recompensa + self.gamma * melhor_futuro
        novo_valor = valor_atual + self.alpha * (alvo - valor_atual)
        self.q_table[estado][acao] = novo_valor
        self.ultimo_valor_q = novo_valor

    def registrar_passo(self, recompensa):
        self.passo_atual += 1
        self.ultima_recompensa = recompensa
        self.recompensa_episodio += recompensa

    def finalizar_episodio(self, resultado, aplicar_decay=True):
        self.ultimo_resultado = resultado
        self.total_episodios_finalizados += 1

        if resultado == "vitoria":
            self.vitorias += 1
        elif resultado == "morte":
            self.mortes += 1
        elif resultado == "limite_passos":
            self.timeouts += 1

        self.melhor_recompensa = max(self.melhor_recompensa, self.recompensa_episodio)
        self.recompensas_recentes.append(self.recompensa_episodio)
        self.vitorias_recentes.append(1 if resultado == "vitoria" else 0)
        self.mortes_recentes.append(1 if resultado == "morte" else 0)
        self.passos_recentes.append(self.passo_atual)
        self.epsilon_historico.append(self.epsilon)
        if aplicar_decay:
            self.decair_epsilon()
        self.episodio_atual += 1
        self.passo_atual = 0
        self.recompensa_episodio = 0.0

    def decair_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def iniciar_lote(self):
        self._inicio_lote = time.perf_counter()
        self.ultimo_lote_episodios = 0
        self.ultimo_lote_segundos = 0.0

    def finalizar_lote(self, episodios):
        self.ultimo_lote_episodios = episodios
        self.ultimo_lote_segundos = max(0.0001, time.perf_counter() - self._inicio_lote)
        self.episodios_por_segundo = episodios / self.ultimo_lote_segundos

    def reiniciar_treinamento(self):
        self.q_table.clear()
        self.epsilon = self.epsilon_inicial
        self.resetar_metricas()

    def tamanho_tabela(self):
        return len(self.q_table)

    def media_recompensa_recente(self):
        if not self.recompensas_recentes:
            return 0.0
        return sum(self.recompensas_recentes) / len(self.recompensas_recentes)

    def taxa_sucesso(self):
        total = max(1, self.total_episodios_finalizados)
        return self.vitorias / total

    def taxa_sucesso_recente(self):
        if not self.vitorias_recentes:
            return 0.0
        return sum(self.vitorias_recentes) / len(self.vitorias_recentes)

    def taxa_sobrevivencia_recente(self):
        if not self.mortes_recentes:
            return 0.0
        return 1.0 - (sum(self.mortes_recentes) / len(self.mortes_recentes))

    def fase_comportamento(self):
        sucesso = self.taxa_sucesso_recente()
        if self.epsilon > 0.35:
            return "explorando"
        if sucesso < 0.25:
            return "aprendendo"
        return "mais estavel"

    def resumo_metricas(self):
        melhor = 0.0 if self.melhor_recompensa == float("-inf") else self.melhor_recompensa
        return {
            "episodio": self.episodio_atual,
            "passo": self.passo_atual,
            "epsilon": self.epsilon,
            "alpha": self.alpha,
            "gamma": self.gamma,
            "ultima_acao": self.ultima_acao,
            "ultimo_valor_q": self.ultimo_valor_q,
            "ultima_recompensa": self.ultima_recompensa,
            "recompensa_episodio": self.recompensa_episodio,
            "melhor_recompensa": melhor,
            "media_recente": self.media_recompensa_recente(),
            "vitorias": self.vitorias,
            "mortes": self.mortes,
            "timeouts": self.timeouts,
            "taxa_sucesso": self.taxa_sucesso(),
            "taxa_sucesso_recente": self.taxa_sucesso_recente(),
            "taxa_sobrevivencia_recente": self.taxa_sobrevivencia_recente(),
            "q_table": self.tamanho_tabela(),
            "fase": self.fase_comportamento(),
            "eps_por_seg": self.episodios_por_segundo,
            "ultimo_lote": self.ultimo_lote_episodios,
        }

    def salvar(self, caminho):
        dados = {
            "acoes": self.acoes,
            "alpha": self.alpha,
            "gamma": self.gamma,
            "epsilon": self.epsilon,
            "epsilon_inicial": self.epsilon_inicial,
            "epsilon_min": self.epsilon_min,
            "epsilon_decay": self.epsilon_decay,
            "metricas": self.resumo_metricas(),
            "q_table": [
                {"estado": list(estado), "valores": valores}
                for estado, valores in self.q_table.items()
            ],
        }
        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, indent=2)

    def carregar(self, caminho):
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        self.alpha = dados.get("alpha", self.alpha)
        self.gamma = dados.get("gamma", self.gamma)
        self.epsilon = dados.get("epsilon", self.epsilon)
        self.epsilon_inicial = dados.get("epsilon_inicial", self.epsilon_inicial)
        self.epsilon_min = dados.get("epsilon_min", self.epsilon_min)
        self.epsilon_decay = dados.get("epsilon_decay", self.epsilon_decay)

        self.q_table = defaultdict(self._linha_q_padrao)
        for item in dados.get("q_table", []):
            estado = tuple(item["estado"])
            valores = self._linha_q_padrao()
            valores.update(item.get("valores", {}))
            self.q_table[estado] = valores
