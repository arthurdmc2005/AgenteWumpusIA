import heapq

def heuristica(a, b):
    """
    Calcula a distância de Manhattan entre duas coordenadas.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_estrela(inicio, fim, celulas_seguras, n):
    """
    Implementa o algoritmo A* para encontrar o caminho mais curto de 'inicio' até 'fim'.
    Apenas se move por células contidas em 'celulas_seguras' (com exceção do destino final 'fim',
    que pode ser uma célula desconhecida/arriscada que o agente decidiu explorar).
    
    Parâmetros:
    - inicio: tupla (r, c)
    - fim: tupla (r, c)
    - celulas_seguras: conjunto de tuplas (r, c) de células consideradas seguras/visitadas
    - n: dimensão do tabuleiro N
    
    Retorna:
    - Lista de passos [(r1, c1), (r2, c2), ...] incluindo o fim (mas sem o inicio),
      ou None se não houver caminho possível.
    """
    if inicio == fim:
        return []
        
    # Células pelas quais o agente está autorizado a caminhar:
    # Células seguras/visitadas + a célula destino (que pode ser uma célula desconhecida a ser explorada)
    celulas_permitidas = set(celulas_seguras)
    celulas_permitidas.add(fim)
    celulas_permitidas.add(inicio) # Garante que o início está contido
    
    # Fila de prioridade: armazena (f_score, pos)
    open_set = []
    heapq.heappush(open_set, (heuristica(inicio, fim), inicio))
    
    veio_de = {}
    
    g_score = {inicio: 0}
    f_score = {inicio: heuristica(inicio, fim)}
    
    open_set_hash = {inicio}
    
    while open_set:
        _, atual = heapq.heappop(open_set)
        if atual in open_set_hash:
            open_set_hash.remove(atual)
            
        if atual == fim:
            # Reconstrói o caminho
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
            if 0 <= nr < n and 0 <= nc < n:
                if viz in celulas_permitidas:
                    tentative_g_score = g_score[atual] + 1
                    if tentative_g_score < g_score.get(viz, float('inf')):
                        veio_de[viz] = atual
                        g_score[viz] = tentative_g_score
                        f_score[viz] = tentative_g_score + heuristica(viz, fim)
                        if viz not in open_set_hash:
                            heapq.heappush(open_set, (f_score[viz], viz))
                            open_set_hash.add(viz)
                            
    return None # Sem caminho possível
