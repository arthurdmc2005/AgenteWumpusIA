class BaseConhecimento:
    """
    Base de conhecimento e motor de inferencia do agente.
    """

    def __init__(self, n, wumpus_movel=True):
        self.n = n
        self.wumpus_movel = wumpus_movel
        self.wumpus_vivo = True

        self.visited = set()
        self.percepcoes = {}

        self.sem_poco = {(0, 0)}
        self.pocos_confirmados = set()

        self.possiveis_posicoes_wumpus = {
            (r, c) for r in range(n) for c in range(n) if (r, c) != (0, 0)
        }
        self.sem_wumpus = {(0, 0)}
        self.wumpus_confirmado = None

    def vizinhos(self, pos):
        r, c = pos
        candidatos = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        return [(nr, nc) for nr, nc in candidatos if 0 <= nr < self.n and 0 <= nc < self.n]

    def registrar_percepcao(self, pos, perc):
        self.visited.add(pos)
        self.percepcoes[pos] = perc

        self.sem_poco.add((0, 0))
        if not self.wumpus_movel:
            self.sem_wumpus.add((0, 0))

        self.atualizar_inferencias(pos, perc)

    def atualizar_inferencias(self, pos, perc):
        if not perc["brisa"]:
            for viz in self.vizinhos(pos):
                self.sem_poco.add(viz)
        else:
            vizinhos = self.vizinhos(pos)
            vizinhos_suspeitos = [v for v in vizinhos if v not in self.sem_poco]
            if len(vizinhos_suspeitos) == 1:
                self.pocos_confirmados.add(vizinhos_suspeitos[0])

        self.propagar_logica_pocos()

        if not self.wumpus_vivo:
            return

        if self.wumpus_movel:
            if pos in self.possiveis_posicoes_wumpus:
                self.possiveis_posicoes_wumpus.remove(pos)

            vizinhos = self.vizinhos(pos)
            if not perc["cheiro"]:
                for viz in vizinhos:
                    self.possiveis_posicoes_wumpus.discard(viz)
            else:
                self.possiveis_posicoes_wumpus = self.possiveis_posicoes_wumpus.intersection(set(vizinhos))
        else:
            if not perc["cheiro"]:
                for viz in self.vizinhos(pos):
                    self.sem_wumpus.add(viz)
            else:
                vizinhos = self.vizinhos(pos)
                vizinhos_suspeitos = [v for v in vizinhos if v not in self.sem_wumpus]
                if len(vizinhos_suspeitos) == 1:
                    self.wumpus_confirmado = vizinhos_suspeitos[0]

            self.propagar_logica_wumpus_estatico()

    def propagar_logica_pocos(self):
        mudou = True
        while mudou:
            mudou = False
            for v in self.visited:
                if self.percepcoes[v]["brisa"]:
                    vizinhos = self.vizinhos(v)
                    vizinhos_desconhecidos = [n for n in vizinhos if n not in self.sem_poco]
                    if len(vizinhos_desconhecidos) == 1:
                        poco_inferred = vizinhos_desconhecidos[0]
                        if poco_inferred not in self.pocos_confirmados:
                            self.pocos_confirmados.add(poco_inferred)
                            mudou = True

    def propagar_logica_wumpus_estatico(self):
        if self.wumpus_movel or not self.wumpus_vivo or self.wumpus_confirmado is not None:
            return

        mudou = True
        while mudou and self.wumpus_confirmado is None:
            mudou = False
            for v in self.visited:
                if self.percepcoes[v]["cheiro"]:
                    vizinhos = self.vizinhos(v)
                    vizinhos_desconhecidos = [n for n in vizinhos if n not in self.sem_wumpus]
                    if len(vizinhos_desconhecidos) == 1:
                        self.wumpus_confirmado = vizinhos_desconhecidos[0]
                        mudou = True
                        break

    def wumpus_moveu(self):
        if not self.wumpus_movel or not self.wumpus_vivo:
            return

        novas_possibilidades = set()
        for pos in self.possiveis_posicoes_wumpus:
            for viz in self.vizinhos(pos):
                if viz != (0, 0):
                    novas_possibilidades.add(viz)

        self.possiveis_posicoes_wumpus = novas_possibilidades

    def matar_wumpus(self):
        self.wumpus_vivo = False
        if self.wumpus_movel:
            self.possiveis_posicoes_wumpus = set()
        else:
            self.wumpus_confirmado = None
            self.sem_wumpus = {(r, c) for r in range(self.n) for c in range(self.n)}

    def eh_segura(self, pos):
        if pos not in self.sem_poco or pos in self.pocos_confirmados:
            return False

        if not self.wumpus_vivo:
            return True

        if self.wumpus_movel:
            return pos not in self.possiveis_posicoes_wumpus

        if self.wumpus_confirmado is not None:
            return pos != self.wumpus_confirmado
        return pos in self.sem_wumpus

    def get_celulas_seguras(self):
        seguras = set()
        for r in range(self.n):
            for c in range(self.n):
                pos = (r, c)
                if self.eh_segura(pos):
                    seguras.add(pos)
        return seguras.union(self.visited)

    def calcular_probabilidade_risco(self, pos):
        if self.eh_segura(pos):
            return 0.0

        if pos in self.pocos_confirmados:
            return 1.0
        if self.wumpus_vivo and not self.wumpus_movel and pos == self.wumpus_confirmado:
            return 1.0

        vizinhos_visitados = [v for v in self.vizinhos(pos) if v in self.visited]
        if any(not self.percepcoes[v]["brisa"] for v in vizinhos_visitados):
            p_poco = 0.0
        else:
            fatores = []
            for v in vizinhos_visitados:
                if self.percepcoes[v]["brisa"]:
                    vizinhos_v = self.vizinhos(v)
                    desconhecidos = [n for n in vizinhos_v if n not in self.sem_poco]
                    if desconhecidos:
                        fatores.append(1.0 / len(desconhecidos))

            if fatores:
                p_poco = 1.0
                for f in fatores:
                    p_poco *= (1.0 - f)
                p_poco = 1.0 - p_poco
            else:
                p_poco = 0.2

        if not self.wumpus_vivo:
            p_wumpus = 0.0
        elif self.wumpus_movel:
            if pos in self.possiveis_posicoes_wumpus:
                p_wumpus = 1.0 / max(1, len(self.possiveis_posicoes_wumpus))
            else:
                p_wumpus = 0.0
        else:
            if any(not self.percepcoes[v]["cheiro"] for v in vizinhos_visitados):
                p_wumpus = 0.0
            else:
                fatores = []
                for v in vizinhos_visitados:
                    if self.percepcoes[v]["cheiro"]:
                        vizinhos_v = self.vizinhos(v)
                        desconhecidos = [n for n in vizinhos_v if n not in self.sem_wumpus]
                        if desconhecidos:
                            fatores.append(1.0 / len(desconhecidos))
                if fatores:
                    p_wumpus = 1.0
                    for f in fatores:
                        p_wumpus *= (1.0 - f)
                    p_wumpus = 1.0 - p_wumpus
                else:
                    p_wumpus = 1.0 / (self.n * self.n - 1)

        return 1.0 - (1.0 - p_poco) * (1.0 - p_wumpus)
