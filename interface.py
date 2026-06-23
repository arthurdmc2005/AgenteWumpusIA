import pygame
import sys
import numpy as np

class InterfaceGrafica:
    """
    Interface gráfica em Pygame para o simulador do Mundo de Wumpus.
    Exibe a grade, posições reais dos elementos, crenças do agente, logs em tempo real
    e estatísticas do jogo.
    """
    def __init__(self, n, largura_grade=800, largura_painel=350):
        pygame.init()
        self.n = n
        self.largura_grade = largura_grade
        self.largura_painel = largura_painel
        self.largura_total = largura_grade + largura_painel
        self.altura = largura_grade
        
        self.tela = pygame.display.set_mode((self.largura_total, self.altura))
        pygame.display.set_caption("Mundo de Wumpus - Inteligência Artificial")
        
        self.clock = pygame.time.Clock()
        self.cell_size = largura_grade // n
        
        # Paleta de cores premium (Aesthetics)
        self.COR_BG_GRID = (18, 18, 20)          # Grafite escuro
        self.COR_CEL_VISITADA = (43, 44, 53)     # Azul acinzentado escuro
        self.COR_CEL_NAO_VISITADA = (28, 28, 30) # Grafite mais escuro
        self.COR_LINHA = (50, 50, 55)            # Linhas da grade
        self.COR_PAINEL = (22, 22, 26)           # Fundo do painel lateral
        self.COR_PAINEL_LINHA = (40, 40, 45)     # Separador de painel
        
        # Cores de feedback/status
        self.COR_TEXTO = (240, 240, 245)
        self.COR_TEXTO_MUTED = (140, 140, 150)
        self.COR_VERDE_SEG = (46, 204, 113)      # Verde esmeralda (Célula Segura)
        self.COR_VERMELHO_PER = (231, 76, 60)    # Vermelho (Célula Perigosa)
        self.COR_OURO = (241, 196, 15)           # Amarelo Ouro
        self.COR_AGENTE = (52, 152, 219)         # Azul brilhante
        self.COR_WUMPUS = (155, 89, 182)         # Roxo Wumpus
        self.COR_POCO = (20, 20, 20)             # Preto profundo
        
        # Fontes
        self.fonte_titulo = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.fonte_normal = pygame.font.SysFont("Segoe UI", 16)
        self.fonte_pequena = pygame.font.SysFont("Segoe UI", 12)
        self.fonte_micro = pygame.font.SysFont("Consolas", 11)

    def processar_eventos(self, modo_ia):
        """
        Lida com eventos de teclado e janela do Pygame.
        Retorna uma string com o comando detectado para o loop principal.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return "PAUSAR"
                elif event.key == pygame.K_r:
                    return "REINICIAR"
                elif event.key == pygame.K_m:
                    return "MODO_WUMPUS"
                elif event.key == pygame.K_c:
                    return "TOGGLE_IA"
                elif event.key == pygame.K_s:
                    if not modo_ia:
                        return "DIR_DOWN"
                    return "PASSO"
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    return "DIR_UP"
                elif event.key == pygame.K_DOWN:
                    return "DIR_DOWN"
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    return "DIR_LEFT"
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    return "DIR_RIGHT"
                elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS or event.key == pygame.K_EQUALS:
                    return "VEL_MAIS"
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    return "VEL_MENOS"
        return None

    def desenhar(self, ambiente, agente, em_pausa, fps):
        """
        Renderiza o tabuleiro e o painel lateral.
        """
        self.tela.fill(self.COR_BG_GRID)
        
        # 1. Desenhar a Grade
        for r in range(self.n):
            for c in range(self.n):
                rect = pygame.Rect(c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size)
                pos = (r, c)
                
                # Fundo da célula baseado em ter sido visitada ou não
                if pos in agente.kb.visited:
                    pygame.draw.rect(self.tela, self.COR_CEL_VISITADA, rect)
                else:
                    pygame.draw.rect(self.tela, self.COR_CEL_NAO_VISITADA, rect)
                
                # Desenhar bordas
                pygame.draw.rect(self.tela, self.COR_LINHA, rect, 1)
                
                # Sobrepor destaques de segurança / perigo da Base de Conhecimento
                if pos in agente.kb.visited:
                    # Mostrar percepções registradas
                    percepcao = agente.kb.percepcoes[pos]
                    self.desenhar_percepcoes_na_celula(percepcao, rect)
                else:
                    # Célula não visitada: mostrar se o agente já a deduziu como segura ou perigosa
                    if agente.kb.eh_segura(pos):
                        # Preenchimento verde sutil translúcido
                        s = pygame.Surface((rect.width - 2, rect.height - 2))
                        s.set_alpha(35)
                        s.fill((46, 204, 113))
                        self.tela.blit(s, (rect.x + 1, rect.y + 1))
                        # Borda verde sutil para seguro
                        pygame.draw.rect(self.tela, self.COR_VERDE_SEG, rect, 2)
                    elif pos in agente.kb.pocos_confirmados or (not agente.kb.wumpus_movel and pos == agente.kb.wumpus_confirmado):
                        # Preenchimento vermelho sutil translúcido
                        s = pygame.Surface((rect.width - 2, rect.height - 2))
                        s.set_alpha(35)
                        s.fill((231, 76, 60))
                        self.tela.blit(s, (rect.x + 1, rect.y + 1))
                        # Borda vermelha para perigo absoluto
                        pygame.draw.rect(self.tela, self.COR_VERMELHO_PER, rect, 2)
                        
                        # Desenha o triângulo de perigo
                        self.desenhar_simbolo_perigo(rect)
                    else:
                        # Se for desconhecido e não 100% seguro/perigoso, exibe a probabilidade de risco
                        risco = agente.kb.calcular_probabilidade_risco(pos)
                        if risco > 0.0:
                            self.desenhar_texto_risco(risco, rect)
                
                # Mostrar posições REAIS dos elementos ocultos no mapa (modo observador para avaliação)
                self.desenhar_elementos_reais(ambiente, pos, rect)

        # 2. Desenhar o Agente (sempre visível por cima)
        agente_rect = pygame.Rect(agente.pos[1] * self.cell_size, agente.pos[0] * self.cell_size, self.cell_size, self.cell_size)
        self.desenhar_agente_icon(agente_rect, agente.has_gold)
        
        # 3. Desenhar Painel Lateral
        self.desenhar_painel_lateral(ambiente, agente, em_pausa, fps)
        
        pygame.display.flip()
        self.clock.tick(60)

    def desenhar_percepcoes_na_celula(self, percepcao, rect):
        """
        Desenha representações gráficas detalhadas das percepções registradas.
        """
        offset_y = 5
        # Brisa (Vento - linhas curvas de vento azul ciano)
        if percepcao["brisa"]:
            pygame.draw.arc(self.tela, (135, 206, 250), (rect.x + 4, rect.y + rect.height // 5, rect.width - 8, rect.height // 5), 0.5, 2.5, 2)
            pygame.draw.arc(self.tela, (135, 206, 250), (rect.x + 4, rect.y + 2 * rect.height // 5, rect.width - 8, rect.height // 5), 0.5, 2.5, 2)
            txt = self.fonte_pequena.render("Brisa (Vento)", True, (135, 206, 250))
            self.tela.blit(txt, (rect.x + 5, rect.y + offset_y))
            offset_y += 13
            
        # Cheiro (Odor - ondas de gás verde-limão)
        if percepcao["cheiro"]:
            # Desenha 3 pequenas ondas verticais
            x_start = rect.x + rect.width - 25
            for i in range(3):
                cx = x_start + i * 6
                pygame.draw.arc(self.tela, (46, 204, 113), (cx, rect.y + rect.height // 2, 6, 12), 0, 3.14, 2)
                pygame.draw.arc(self.tela, (46, 204, 113), (cx, rect.y + rect.height // 2 + 6, 6, 12), 3.14, 6.28, 2)
            txt = self.fonte_pequena.render("Cheiro (Odor)", True, (155, 89, 182))
            self.tela.blit(txt, (rect.x + 5, rect.y + offset_y))
            offset_y += 13
            
        # Brilho (Ouro na célula - fundo amarelo e estrelas brilhando)
        if percepcao["brilho"]:
            # Preenche o fundo levemente com amarelo translúcido
            s = pygame.Surface((rect.width - 2, rect.height - 2))
            s.set_alpha(50)
            s.fill(self.COR_OURO)
            self.tela.blit(s, (rect.x + 1, rect.y + 1))
            txt = self.fonte_pequena.render("Brilho (Ouro!)", True, self.COR_OURO)
            self.tela.blit(txt, (rect.x + 5, rect.y + offset_y))

    def desenhar_simbolo_perigo(self, rect):
        """
        Desenha um triângulo de advertência detalhado para perigo inferido.
        """
        centro = rect.center
        sz = rect.width // 4
        # Desenha triângulo amarelo com borda vermelha e "!" preto no meio
        pontos = [
            (centro[0], centro[1] - sz),
            (centro[0] + sz, centro[1] + sz),
            (centro[0] - sz, centro[1] + sz)
        ]
        pygame.draw.polygon(self.tela, (241, 196, 15), pontos)
        pygame.draw.polygon(self.tela, (231, 76, 60), pontos, 2)
        
        # Exclamação !
        txt = self.fonte_normal.render("!", True, (0, 0, 0))
        txt_rect = txt.get_rect(center=(centro[0], centro[1] + sz // 3))
        self.tela.blit(txt, txt_rect)

    def desenhar_texto_risco(self, risco, rect):
        """
        Exibe a taxa de risco (probabilidade) no canto inferior da célula.
        """
        if self.cell_size > 45:
            cor = (230, 126, 34) if risco < 0.5 else self.COR_VERMELHO_PER
            # Desenha um pequeno badge retangular escuro por trás da porcentagem
            txt_prob = self.fonte_pequena.render(f"Risco:{risco:.0%}", True, cor)
            txt_rect = txt_prob.get_rect(bottomleft=(rect.x + 4, rect.y + rect.height - 4))
            
            badge_rect = pygame.Rect(txt_rect.x - 2, txt_rect.y - 1, txt_rect.width + 4, txt_rect.height + 2)
            pygame.draw.rect(self.tela, (15, 15, 18), badge_rect)
            pygame.draw.rect(self.tela, self.COR_LINHA, badge_rect, 1)
            
            self.tela.blit(txt_prob, txt_rect)

    def desenhar_elementos_reais(self, ambiente, pos, rect):
        """
        Desenha os elementos reais ocultos no mapa (modo observador para avaliação).
        """
        if pos in ambiente.pocos:
            self.desenhar_poco_icon(rect)
        if pos == ambiente.ouro_pos:
            self.desenhar_ouro_icon(rect)
        if pos == ambiente.wumpus_pos:
            self.desenhar_wumpus_icon(rect)

    def desenhar_poco_icon(self, rect):
        """
        Desenha um poço com efeito tridimensional de espiral profunda.
        """
        # Desenha borda rochosa retangular
        pygame.draw.rect(self.tela, (110, 85, 70), rect, 2)
        
        centro = rect.center
        raio_max = rect.width // 3
        # Círculos concêntricos sombreados
        for r in range(raio_max, 0, -3):
            ratio = r / raio_max
            tom = int(60 * ratio)
            pygame.draw.circle(self.tela, (tom, tom, tom), centro, r)
        # Centro do buraco totalmente escuro
        pygame.draw.circle(self.tela, (0, 0, 0), centro, 3)

    def desenhar_ouro_icon(self, rect):
        """
        Desenha um baú de tesouro de madeira com fechos dourados e estrelas de brilho.
        """
        centro = rect.center
        w = rect.width // 3
        h = rect.height // 4
        x = centro[0] - w // 2
        y = centro[1] - h // 2
        
        # Corpo de madeira do baú (marrom)
        pygame.draw.rect(self.tela, (139, 69, 19), (x, y, w, h))
        pygame.draw.rect(self.tela, (80, 40, 10), (x, y, w, h), 2)
        
        # Tampa do baú
        pygame.draw.ellipse(self.tela, (160, 82, 45), (x, y - h // 2, w, h))
        pygame.draw.ellipse(self.tela, (80, 40, 10), (x, y - h // 2, w, h), 2)
        
        # Fechadura de ouro
        pygame.draw.rect(self.tela, self.COR_OURO, (centro[0] - 3, y + 2, 6, 8))
        pygame.draw.circle(self.tela, (0, 0, 0), (centro[0], y + 6), 2)
        
        # Linhas de brilho ao redor
        pontos_brilho = [(x - 4, y - 4), (x + w + 4, y - 4), (centro[0], y - h - 3)]
        for px, py in pontos_brilho:
            pygame.draw.line(self.tela, self.COR_OURO, (px - 2, py), (px + 2, py), 1)
            pygame.draw.line(self.tela, self.COR_OURO, (px, py - 2), (px, py + 2), 1)

    def desenhar_wumpus_icon(self, rect):
        """
        Desenha um Wumpus peludo roxo detalhado (corpo redondo, chifres, olhos vermelhos, dentes).
        """
        centro = rect.center
        raio = rect.width // 4
        
        # Pelos espetados ao redor do corpo
        import math
        for i in range(12):
            angulo = i * (2 * math.pi / 12)
            px = int(centro[0] + (raio + 4) * math.cos(angulo))
            py = int(centro[1] + (raio + 4) * math.sin(angulo))
            pygame.draw.line(self.tela, (120, 50, 140), centro, (px, py), 2)
            
        # Corpo principal roxo
        pygame.draw.circle(self.tela, self.COR_WUMPUS, centro, raio)
        pygame.draw.circle(self.tela, (80, 30, 95), centro, raio, 2)
        
        # Chifres cinzas
        chifre_l = [
            (centro[0] - raio + 3, centro[1] - raio + 3),
            (centro[0] - raio - 4, centro[1] - raio - 4),
            (centro[0] - raio + 8, centro[1] - raio - 2)
        ]
        chifre_r = [
            (centro[0] + raio - 3, centro[1] - raio + 3),
            (centro[0] + raio + 4, centro[1] - raio - 4),
            (centro[0] + raio - 8, centro[1] - raio - 2)
        ]
        pygame.draw.polygon(self.tela, (140, 150, 155), chifre_l)
        pygame.draw.polygon(self.tela, (140, 150, 155), chifre_r)
        
        # Olhos vermelhos malévolos
        pygame.draw.circle(self.tela, (255, 0, 0), (centro[0] - 5, centro[1] - 3), 3)
        pygame.draw.circle(self.tela, (255, 0, 0), (centro[0] + 5, centro[1] - 3), 3)
        # Pupilas brancas
        pygame.draw.circle(self.tela, (255, 255, 255), (centro[0] - 5, centro[1] - 3), 1)
        pygame.draw.circle(self.tela, (255, 255, 255), (centro[0] + 5, centro[1] - 3), 1)
        
        # Boca aberta com dois dentes triangulares brancos
        pygame.draw.arc(self.tela, (255, 255, 255), (centro[0] - 6, centro[1], 12, 6), 3.14, 6.28, 2)
        pygame.draw.polygon(self.tela, (255, 255, 255), [(centro[0] - 4, centro[1] + 1), (centro[0] - 3, centro[1] + 4), (centro[0] - 2, centro[1] + 1)])
        pygame.draw.polygon(self.tela, (255, 255, 255), [(centro[0] + 2, centro[1] + 1), (centro[0] + 3, centro[1] + 4), (centro[0] + 4, centro[1] + 1)])

    def desenhar_agente_icon(self, rect, tem_ouro):
        """
        Desenha o explorador com chapéu de aventura e uma tocha flamejante na mão.
        """
        centro = rect.center
        raio = rect.width // 4
        
        # Cabeça do explorador
        pygame.draw.circle(self.tela, (244, 208, 111), centro, raio)
        pygame.draw.circle(self.tela, (110, 80, 50), centro, raio, 2)
        
        # Chapéu fedora marrom
        # Aba
        pygame.draw.ellipse(self.tela, (101, 67, 33), (centro[0] - raio - 4, centro[1] - raio + 2, raio * 2 + 8, 5))
        pygame.draw.ellipse(self.tela, (65, 40, 20), (centro[0] - raio - 4, centro[1] - raio + 2, raio * 2 + 8, 5), 1)
        # Copa
        pygame.draw.rect(self.tela, (101, 67, 33), (centro[0] - raio + 2, centro[1] - raio - 7, raio * 2 - 4, 9))
        pygame.draw.rect(self.tela, (65, 40, 20), (centro[0] - raio + 2, centro[1] - raio - 7, raio * 2 - 4, 9), 1)
        # Faixa preta
        pygame.draw.rect(self.tela, (0, 0, 0), (centro[0] - raio + 2, centro[1] - raio - 1, raio * 2 - 4, 3))
        
        # Olhos
        pygame.draw.circle(self.tela, (255, 255, 255), (centro[0] - 4, centro[1] + 2), 3)
        pygame.draw.circle(self.tela, (255, 255, 255), (centro[0] + 4, centro[1] + 2), 3)
        pygame.draw.circle(self.tela, (0, 0, 0), (centro[0] - 4, centro[1] + 2), 1.5)
        pygame.draw.circle(self.tela, (0, 0, 0), (centro[0] + 4, centro[1] + 2), 1.5)
        
        # Tocha flamejante
        tx = centro[0] - raio - 3
        ty = centro[1] + 3
        # Haste de madeira
        pygame.draw.line(self.tela, (139, 69, 19), (tx, ty), (tx, ty + 8), 3)
        # Chama laranja externa
        pygame.draw.circle(self.tela, (230, 126, 34), (tx, ty - 2), 4)
        # Chama amarela interna
        pygame.draw.circle(self.tela, (241, 196, 15), (tx, ty - 2), 2)
        
        # Sacola de moedas (ouro coletado)
        if tem_ouro:
            sx = centro[0] + raio + 3
            sy = centro[1] + 5
            # Sacola amarela
            pygame.draw.circle(self.tela, self.COR_OURO, (sx, sy), 5)
            # Laço
            pygame.draw.line(self.tela, (170, 130, 10), (sx - 2, sy - 5), (sx + 2, sy - 5), 2)
            # Sinal de cifrão
            txt_s = self.fonte_pequena.render("$", True, (0, 0, 0))
            self.tela.blit(txt_s, (sx - 3, sy - 6))

    def desenhar_painel_lateral(self, ambiente, agente, em_pausa, fps):
        """
        Desenha as estatísticas, logs e status do simulador no painel lateral.
        """
        x_painel = self.largura_grade
        rect_painel = pygame.Rect(x_painel, 0, self.largura_painel, self.altura)
        
        # Fundo do painel
        pygame.draw.rect(self.tela, self.COR_PAINEL, rect_painel)
        pygame.draw.line(self.tela, self.COR_PAINEL_LINHA, (x_painel, 0), (x_painel, self.altura), 2)
        
        # Título
        y = 20
        titulo = self.fonte_titulo.render("WUMPUS WORLD AI", True, self.COR_TEXTO)
        self.tela.blit(titulo, (x_painel + 20, y))
        y += 40
        
        # Status do Jogo
        status_txt = "EXPLORANDO"
        cor_status = self.COR_AGENTE
        
        if not agente.alive:
            status_txt = "AGENTE MORREU"
            # Identifica a causa da morte
            if agente.pos in ambiente.pocos:
                status_txt += " (POÇO)"
            elif agente.pos == ambiente.wumpus_pos:
                status_txt += " (WUMPUS)"
            cor_status = self.COR_VERMELHO_PER
        elif agente.vitorioso:
            status_txt = "VITÓRIA!"
            cor_status = self.COR_VERDE_SEG
        elif agente.has_gold:
            status_txt = "RETORNANDO COM OURO"
            cor_status = self.COR_OURO
        elif em_pausa:
            status_txt = "PAUSADO"
            cor_status = self.COR_TEXTO_MUTED
            
        lbl_status = self.fonte_normal.render("Status:", True, self.COR_TEXTO_MUTED)
        self.tela.blit(lbl_status, (x_painel + 20, y))
        val_status = self.fonte_titulo.render(status_txt, True, cor_status)
        self.tela.blit(val_status, (x_painel + 80, y - 5))
        y += 40
        
        # Estatísticas
        estatisticas = [
            ("Controle:", "IA (Automático)" if agente.modo_ia else "MANUAL (Teclado)"),
            ("Dimensão:", f"{ambiente.n} x {ambiente.n}"),
            ("Passos dados:", f"{agente.passos}"),
            ("Visitadas:", f"{len(agente.kb.visited)} / {ambiente.n * ambiente.n}"),
            ("Ouro Coletado:", "Sim" if agente.has_gold else "Não"),
            ("Wumpus Móvel:", "Ativo" if ambiente.wumpus_movel else "Inativo"),
            ("Velocidade IA:", f"{fps} Hz (passos/s)"),
        ]
        
        for rotulo, valor in estatisticas:
            lbl = self.fonte_normal.render(rotulo, True, self.COR_TEXTO_MUTED)
            val = self.fonte_normal.render(valor, True, self.COR_TEXTO)
            # Se for controle manual, destaca a cor
            if rotulo == "Controle:" and not agente.modo_ia:
                val = self.fonte_normal.render(valor, True, self.COR_OURO)
            self.tela.blit(lbl, (x_painel + 20, y))
            self.tela.blit(val, (x_painel + 150, y))
            y += 24
            
        y += 15
        
        # Caixa de logs (Console simulado)
        lbl_log = self.fonte_normal.render("Log de Ações do Agente:", True, self.COR_TEXTO_MUTED)
        self.tela.blit(lbl_log, (x_painel + 20, y))
        y += 25
        
        rect_log = pygame.Rect(x_painel + 15, y, self.largura_painel - 30, 310)
        pygame.draw.rect(self.tela, (14, 14, 16), rect_log)
        pygame.draw.rect(self.tela, self.COR_PAINEL_LINHA, rect_log, 1)
        
        log_y = y + 10
        for entrada in agente.log[-17:]:  # Exibe os últimos 17 logs
            # Colore de acordo com palavras chave no log
            cor_log = self.COR_TEXTO
            if "VITÓRIA" in entrada: cor_log = self.COR_VERDE_SEG
            elif "MORREU" in entrada or "Morte" in entrada: cor_log = self.COR_VERMELHO_PER
            elif "Ouro" in entrada or "ouro" in entrada: cor_log = self.COR_OURO
            elif "risco" in entrada: cor_log = (230, 126, 34)
            elif "Wumpus" in entrada: cor_log = self.COR_WUMPUS
            elif "Controle" in entrada: cor_log = (52, 152, 219)
            
            txt_log = self.fonte_micro.render(entrada, True, cor_log)
            self.tela.blit(txt_log, (x_painel + 22, log_y))
            log_y += 17
            
        y += 325
        
        # Painel de atalhos de controle
        lbl_ctrl = self.fonte_pequena.render("Controles do Simulador:", True, self.COR_TEXTO_MUTED)
        self.tela.blit(lbl_ctrl, (x_painel + 20, y))
        y += 15
        
        controles_texto1 = "[C] Alternar IA/Manual | [P] Pausar | [R] Reiniciar"
        controles_texto2 = "[M] Wumpus Móvel | [S] Passo IA | [Setas / WASD] Mover"
        
        txt_ctrl1 = self.fonte_pequena.render(controles_texto1, True, self.COR_TEXTO)
        txt_ctrl2 = self.fonte_pequena.render(controles_texto2, True, self.COR_TEXTO)
        self.tela.blit(txt_ctrl1, (x_painel + 20, y))
        self.tela.blit(txt_ctrl2, (x_painel + 20, y + 16))
