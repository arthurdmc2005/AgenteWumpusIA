class BaseConhecimento:
    """
    Base de Conhecimento e Motor de Inferência do Agente.
    Armazena células visitadas, percepções e realiza inferência lógica
    (para poços e Wumpus estático) e probabilística (quando não há caminhos 100% seguros).
    
    Também gerencia a crença de localização do Wumpus caso ele seja móvel.
    """
    def __init__(self, n, wumpus_movel=True):
        self.n = n
        self.wumpus_movel = wumpus_movel
        
        # Células visitadas pelo agente
        self.visited = set()
        
        # Percepções registradas em cada célula visitada: (r, c) -> {"brisa": bool, "cheiro": bool, "brilho": bool}
        self.percepcoes = {}
        
        # Inferências lógicas permanentes para poços (poços não se movem)
        self.sem_poco = {(0, 0)} # (0,0) é garantido sem poço
        self.pocos_confirmados = set()
        
        # Inferências para Wumpus
        if self.wumpus_movel:
            # Conjunto de todas as células possíveis onde o Wumpus pode estar
            # Inicialmente pode estar em qualquer lugar exceto (0,0)
            self.possiveis_posicoes_wumpus = {(r, c) for r in range(n) for c in range(n) if (r, c) != (0, 0)}
        else:
            self.sem_wumpus = {(0, 0)}
            self.wumpus_confirmado = None

    def vizinhos(self, pos):
        """
        Retorna vizinhos ortogonais válidos dentro do tabuleiro NxN.
        """
        r, c = pos
        candidatos = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        return [(nr, nc) for (nr, nc) in candidatos if 0 <= nr < self.n and 0 <= nc < self.n]

    def registrar_percepcao(self, pos, perc):
        """
        Registra a percepção da célula atual e adiciona a célula à lista de visitadas.
        """
        self.visited.add(pos)
        self.percepcoes[pos] = perc
        
        # (0,0) é sempre seguro de tudo
        self.sem_poco.add((0, 0))
        if not self.wumpus_movel:
            self.sem_wumpus.add((0, 0))
            
        self.atualizar_inferencias(pos, perc)

    def atualizar_inferencias(self, pos, perc):
        """
        Atualiza as inferências lógicas com base nas novas percepções.
        """
        # --- Inferência para Poços ---
        if not perc["brisa"]:
            # Se não há brisa, NENHUM vizinho tem poço
            for viz in self.vizinhos(pos):
                self.sem_poco.add(viz)
        else:
            # Se há brisa, pelo menos um vizinho desconhecido tem poço
            # Se todos os vizinhos exceto um são conhecidos como sem poço, o restante é poço
            vizinhos = self.vizinhos(pos)
            vizinhos_suspeitos = [v for v in vizinhos if v not in self.sem_poco]
            if len(vizinhos_suspeitos) == 1:
                self.pocos_confirmados.add(vizinhos_suspeitos[0])
                
        # Propagação recursiva simplificada
        # Se um poço é confirmado em 'p', ele não pode estar em células marcadas como sem poço.
        # Também, se um vizinho de um local com brisa é confirmado como poço, isso satisfaz a brisa,
        # mas não garante que outros vizinhos não tenham poço. No entanto, se descobrimos novos 'sem_poco',
        # podemos deduzir outros poços.
        self.propagar_lógica_pocos()

        # --- Inferência para Wumpus ---
        if self.wumpus_movel:
            # Atualiza o modelo de crença sobre o Wumpus móvel
            # Se o agente está em 'pos':
            # 1. O Wumpus não está em 'pos' (pois o agente está vivo)
            if pos in self.possiveis_posicoes_wumpus:
                self.possiveis_posicoes_wumpus.remove(pos)
                
            vizinhos = self.vizinhos(pos)
            if not perc["cheiro"]:
                # Se não há cheiro na célula atual, o Wumpus não está em nenhum vizinho
                for viz in vizinhos:
                    if viz in self.possiveis_posicoes_wumpus:
                        self.possiveis_posicoes_wumpus.remove(viz)
            else:
                # Se há cheiro na célula atual, o Wumpus deve estar em um dos vizinhos
                self.possiveis_posicoes_wumpus = self.possiveis_posicoes_wumpus.intersection(set(vizinhos))
        else:
            # Wumpus Estático
            if not perc["cheiro"]:
                # Se não há cheiro, nenhum vizinho tem Wumpus
                for viz in self.vizinhos(pos):
                    self.sem_wumpus.add(viz)
            else:
                # Se há cheiro, pelo menos um vizinho tem Wumpus
                vizinhos = self.vizinhos(pos)
                vizinhos_suspeitos = [v for v in vizinhos if v not in self.sem_wumpus]
                if len(vizinhos_suspeitos) == 1:
                    self.wumpus_confirmado = vizinhos_suspeitos[0]
            
            self.propagar_lógica_wumpus_estatico()

    def propagar_lógica_pocos(self):
        """
        Raciocínio lógico proposicional iterativo para poços.
        """
        mudou = True
        while mudou:
            mudou = False
            # Regra: se uma célula 'v' tem brisa e todos os seus vizinhos exceto um são 'sem_poco',
            # então esse vizinho restante é um poço confirmado.
            for v in self.visited:
                if self.percepcoes[v]["brisa"]:
                    vizinhos = self.vizinhos(v)
                    vizinhos_desconhecidos = [n for n in vizinhos if n not in self.sem_poco]
                    if len(vizinhos_desconhecidos) == 1:
                        poco_inferred = vizinhos_desconhecidos[0]
                        if poco_inferred not in self.pocos_confirmados:
                            self.pocos_confirmados.add(poco_inferred)
                            mudou = True
            
            # Regra: se uma célula 'p' é um poço confirmado, ela não pode ser segura.
            # (Ajuda na consistência, embora poucos_confirmados e sem_poco sejam disjuntos por definição).

    def propagar_lógica_wumpus_estatico(self):
        """
        Raciocínio lógico proposicional iterativo para Wumpus estático.
        """
        if self.wumpus_movel or self.wumpus_confirmado is not None:
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
        """
        Notifica a base de conhecimento de que o Wumpus se moveu.
        Propaga as possíveis localizações para os vizinhos das posições anteriores.
        """
        if not self.wumpus_movel:
            return
            
        novas_possibilidades = set()
        for pos in self.possiveis_posicoes_wumpus:
            # O Wumpus se move para uma célula vizinha
            for viz in self.vizinhos(pos):
                if viz != (0, 0): # O Wumpus não se move para (0, 0)
                    novas_possibilidades.add(viz)
                    
        self.possiveis_posicoes_wumpus = novas_possibilidades

    def eh_segura(self, pos):
        """
        Retorna se a célula é 100% segura com base na lógica.
        Uma célula é segura se:
        1. É sabido que não tem poço (sem_poco).
        2. É sabido que não tem Wumpus.
           - Se Wumpus estático: contida em sem_wumpus ou se o Wumpus foi confirmado em outro lugar.
           - Se Wumpus móvel: não está no conjunto de possíveis posições do Wumpus na rodada atual.
        """
        # Célula deve estar livre de poço
        if pos not in self.sem_poco or pos in self.pocos_confirmados:
            return False
            
        # Célula deve estar livre de Wumpus
        if self.wumpus_movel:
            # É 100% segura se não houver chance nenhuma do Wumpus estar lá
            return pos not in self.possiveis_posicoes_wumpus
        else:
            if self.wumpus_confirmado is not None:
                return pos != self.wumpus_confirmado
            return pos in self.sem_wumpus

    def get_celulas_seguras(self):
        """
        Retorna o conjunto de todas as células que o agente provou logicamente serem seguras.
        """
        seguras = set()
        for r in range(self.n):
            for c in range(self.n):
                pos = (r, c)
                if self.eh_segura(pos):
                    seguras.add(pos)
        # Células já visitadas são seguras por definição (o agente passou por elas e está vivo)
        return seguras.union(self.visited)

    def calcular_probabilidade_risco(self, pos):
        """
        Calcula a probabilidade estimada de risco (poço + Wumpus) para uma célula desconhecida 'pos'.
        Usado para tomada de decisão em situações de risco (bônus).
        """
        # Se a célula é conhecida como segura, risco é 0
        if self.eh_segura(pos):
            return 0.0
            
        # Se é um poço confirmado ou Wumpus confirmado, risco é 1.0
        if pos in self.pocos_confirmados:
            return 1.0
        if not self.wumpus_movel and pos == self.wumpus_confirmado:
            return 1.0

        # --- Probabilidade de Poço (P_poco) ---
        # Se é vizinho de uma célula visitada que NÃO tem brisa, a probabilidade é 0
        vizinhos_visitados = [v for v in self.vizinhos(pos) if v in self.visited]
        if any(not self.percepcoes[v]["brisa"] for v in vizinhos_visitados):
            p_poco = 0.0
        else:
            # Para cada vizinho visitado que tem brisa, ele contribui para o risco
            fatores = []
            for v in vizinhos_visitados:
                if self.percepcoes[v]["brisa"]:
                    # Quantos vizinhos não-seguros essa brisa tem?
                    vizinhos_v = self.vizinhos(v)
                    desconhecidos = [n for n in vizinhos_v if n not in self.sem_poco]
                    if len(desconhecidos) > 0:
                        fatores.append(1.0 / len(desconhecidos))
            
            if fatores:
                # Combinação das fontes de brisa (se múltiplas células com brisa apontam para 'pos')
                # P(poço) = 1 - produto(1 - p_i)
                p_poco = 1.0
                for f in fatores:
                    p_poco *= (1.0 - f)
                p_poco = 1.0 - p_poco
            else:
                # Prior geral se não há vizinhos com brisa que justifiquem
                p_poco = 0.2

        # --- Probabilidade de Wumpus (P_wumpus) ---
        if self.wumpus_movel:
            # Probabilidade baseada no conjunto de crença
            if pos in self.possiveis_posicoes_wumpus:
                p_wumpus = 1.0 / max(1, len(self.possiveis_posicoes_wumpus))
            else:
                p_wumpus = 0.0
        else:
            # Wumpus estático
            if any(not self.percepcoes[v]["cheiro"] for v in vizinhos_visitados):
                p_wumpus = 0.0
            else:
                fatores = []
                for v in vizinhos_visitados:
                    if self.percepcoes[v]["cheiro"]:
                        vizinhos_v = self.vizinhos(v)
                        desconhecidos = [n for n in vizinhos_v if n not in self.sem_wumpus]
                        if len(desconhecidos) > 0:
                            fatores.append(1.0 / len(desconhecidos))
                if fatores:
                    p_wumpus = 1.0
                    for f in fatores:
                        p_wumpus *= (1.0 - f)
                    p_wumpus = 1.0 - p_wumpus
                else:
                    # Prior se Wumpus não está localizado
                    p_wumpus = 1.0 / (self.n * self.n - 1)

        # Risco combinado: probabilidade de pelo menos um ser verdadeiro
        # Risco = 1 - (1 - P_poco) * (1 - P_wumpus)
        risco = 1.0 - (1.0 - p_poco) * (1.0 - p_wumpus)
        return risco
