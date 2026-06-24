import math
import os
import pygame
import sys


class InterfaceGrafica:
    """
    Interface grafica em Pygame para o simulador do Mundo de Wumpus.
    Exibe apenas o conhecimento percebido ou inferido pelo agente.
    """

    def __init__(self, n, largura_grade=800, largura_painel=400, densidade_pocos="normal"):
        pygame.init()
        self.n = n
        self.largura_grade = largura_grade
        self.largura_painel = largura_painel
        self.largura_total = largura_grade + largura_painel
        self.altura = largura_grade
        self.cell_size = largura_grade // n

        self.tela = pygame.display.set_mode((self.largura_total, self.altura))
        pygame.display.set_caption("Wumpus World - Interface Tatica")
        self.clock = pygame.time.Clock()

        self._configurar_design_system()

        self.modo_visualizacao = "agente"
        self.densidade_pocos = densidade_pocos
        self.hover_pos = (-1, -1)
        self.sidebar_scroll = 0
        self.sidebar_max_scroll = 0

        self.secoes = {
            "configuracao": {"titulo": "Configuracao", "aberta": True, "rect": pygame.Rect(0, 0, 0, 0)},
            "telemetria": {"titulo": "Telemetria", "aberta": True, "rect": pygame.Rect(0, 0, 0, 0)},
            "registro": {"titulo": "Registro do Agente", "aberta": True, "rect": pygame.Rect(0, 0, 0, 0)},
            "comandos": {"titulo": "Comandos", "aberta": False, "rect": pygame.Rect(0, 0, 0, 0)},
        }

        self.botao_visao_agente = pygame.Rect(0, 0, 0, 0)
        self.botao_visao_completa = pygame.Rect(0, 0, 0, 0)
        self.botao_modo_humano = pygame.Rect(0, 0, 0, 0)
        self.botao_modo_agente = pygame.Rect(0, 0, 0, 0)
        self.botao_agente_regras = pygame.Rect(0, 0, 0, 0)
        self.botao_agente_qlearning = pygame.Rect(0, 0, 0, 0)
        self.botao_q_treino = pygame.Rect(0, 0, 0, 0)
        self.botao_q_demo = pygame.Rect(0, 0, 0, 0)
        self.botao_q_passo = pygame.Rect(0, 0, 0, 0)
        self.botao_q_reset = pygame.Rect(0, 0, 0, 0)
        self.botao_q_salvar = pygame.Rect(0, 0, 0, 0)
        self.botao_q_carregar = pygame.Rect(0, 0, 0, 0)
        self.botao_agente_regras = pygame.Rect(0, 0, 0, 0)
        self.botao_agente_qlearning = pygame.Rect(0, 0, 0, 0)
        self.botao_visao_agente = pygame.Rect(0, 0, 0, 0)
        self.botao_visao_completa = pygame.Rect(0, 0, 0, 0)
        self.botao_diminuir_mapa = pygame.Rect(0, 0, 0, 0)
        self.botao_aumentar_mapa = pygame.Rect(0, 0, 0, 0)
        self.botao_densidade_leve = pygame.Rect(0, 0, 0, 0)
        self.botao_densidade_normal = pygame.Rect(0, 0, 0, 0)
        self.botao_densidade_denso = pygame.Rect(0, 0, 0, 0)
        self.botao_diminuir_mapa = pygame.Rect(0, 0, 0, 0)
        self.botao_aumentar_mapa = pygame.Rect(0, 0, 0, 0)
        self.botao_densidade_leve = pygame.Rect(0, 0, 0, 0)
        self.botao_densidade_normal = pygame.Rect(0, 0, 0, 0)
        self.botao_densidade_denso = pygame.Rect(0, 0, 0, 0)

        self.sprite_agente_original = self._carregar_sprite_agente()
        self.sprite_wumpus_original = self._carregar_sprite_wumpus()

    def _configurar_design_system(self):
        self.COR_BG = (8, 11, 17)
        self.COR_BG_ACCENT_A = (17, 38, 63)
        self.COR_BG_ACCENT_B = (39, 28, 68)
        self.COR_PANEL = (11, 15, 24)
        self.COR_CARD = (18, 24, 36)
        self.COR_CARD_ALT = (23, 31, 46)
        self.COR_CARD_DEEP = (10, 14, 21)
        self.COR_CARD_HOVER = (28, 38, 56)
        self.COR_STROKE = (56, 78, 106)
        self.COR_STROKE_SOFT = (38, 51, 69)
        self.COR_GRID_BASE = (16, 22, 31)
        self.COR_GRID_VISITED = (45, 61, 82)
        self.COR_GRID_FOG = (23, 28, 36)
        self.COR_TEXTO = (239, 242, 247)
        self.COR_TEXTO_MUTED = (147, 158, 176)
        self.COR_DESTAQUE = (72, 184, 255)
        self.COR_DESTAQUE_SOFT = (55, 104, 151)
        self.COR_VERDE = (78, 201, 140)
        self.COR_VERMELHO = (247, 104, 104)
        self.COR_OURO = (244, 196, 66)
        self.COR_WUMPUS = (209, 96, 255)
        self.COR_ALERTA = (255, 158, 74)

        self.SPACE_OUTER = 16
        self.SPACE_SECTION = 10
        self.SPACE_CARD_PAD = 12
        self.SPACE_LABEL_GAP = 5
        self.SPACE_CONTROL_GAP = 8
        self.SPACE_ROW = 22

        self.HEADER_H = 62
        self.SECTION_HEADER_H = 28
        self.CONTROL_H = 28
        self.SMALL_BTN_W = 34
        self.LOG_MAX_H = 170
        self.LOG_MIN_H = 104
        self.TELEMETRY_VALUE_W = 118

        self.fonte_titulo = pygame.font.SysFont("Trebuchet MS", 19, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("Trebuchet MS", 15, bold=True)
        self.fonte_normal = pygame.font.SysFont("Trebuchet MS", 15)
        self.fonte_pequena = pygame.font.SysFont("Trebuchet MS", 12)
        self.fonte_micro = pygame.font.SysFont("Consolas", 11)

    def _carregar_sprite_agente(self):
        caminho = os.path.join(os.path.dirname(__file__), "fotoagente.jpg")
        try:
            return pygame.image.load(caminho).convert()
        except pygame.error:
            return None

    def _carregar_sprite_wumpus(self):
        caminho = os.path.join(os.path.dirname(__file__), "fotoWumpus.jpeg")
        try:
            return pygame.image.load(caminho).convert()
        except pygame.error:
            return None

    def processar_eventos(self, agente):
        self.hover_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                self.hover_pos = event.pos
            elif event.type == pygame.MOUSEWHEEL:
                if self.hover_pos[0] >= self.largura_grade:
                    self.sidebar_scroll = max(0, min(self.sidebar_max_scroll, self.sidebar_scroll - event.y * 28))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._clicou_secao(event.pos):
                    return None
                if self.botao_modo_humano.collidepoint(event.pos) and agente.modo_jogo != "humano":
                    return "MODO_HUMANO"
                if self.botao_modo_agente.collidepoint(event.pos) and agente.modo_jogo != "agente":
                    return "MODO_AGENTE"
                if self.botao_agente_regras.collidepoint(event.pos) and agente.tipo_agente != "regras":
                    return "TIPO_REGRAS"
                if self.botao_agente_qlearning.collidepoint(event.pos) and agente.tipo_agente != "q_learning":
                    return "TIPO_Q_LEARNING"
                if self.botao_q_treino.collidepoint(event.pos):
                    return "Q_TREINO_RAPIDO"
                if self.botao_q_demo.collidepoint(event.pos):
                    return "Q_DEMONSTRACAO"
                if self.botao_q_passo.collidepoint(event.pos):
                    return "Q_PASSO_A_PASSO"
                if self.botao_q_reset.collidepoint(event.pos):
                    return "RESET_Q_LEARNING"
                if self.botao_q_salvar.collidepoint(event.pos):
                    return "SALVAR_Q"
                if self.botao_q_carregar.collidepoint(event.pos):
                    return "CARREGAR_Q"
                if self.botao_visao_agente.collidepoint(event.pos) and self.modo_visualizacao != "agente":
                    self.modo_visualizacao = "agente"
                    return "VISAO_AGENTE"
                if self.botao_visao_completa.collidepoint(event.pos) and self.modo_visualizacao != "completa":
                    self.modo_visualizacao = "completa"
                    return "VISAO_COMPLETA"
                if self.botao_diminuir_mapa.collidepoint(event.pos):
                    return "MAPA_MENOS"
                if self.botao_aumentar_mapa.collidepoint(event.pos):
                    return "MAPA_MAIS"
                if self.botao_densidade_leve.collidepoint(event.pos) and self.densidade_pocos != "leve":
                    self.densidade_pocos = "leve"
                    return "DENSIDADE_LEVE"
                if self.botao_densidade_normal.collidepoint(event.pos) and self.densidade_pocos != "normal":
                    self.densidade_pocos = "normal"
                    return "DENSIDADE_NORMAL"
                if self.botao_densidade_denso.collidepoint(event.pos) and self.densidade_pocos != "denso":
                    self.densidade_pocos = "denso"
                    return "DENSIDADE_DENSO"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return "PAUSAR"
                elif event.key == pygame.K_r:
                    return "REINICIAR"
                elif event.key == pygame.K_m:
                    return "MODO_WUMPUS"
                elif event.key == pygame.K_c:
                    return "TOGGLE_IA"
                elif event.key == pygame.K_q:
                    return "TOGGLE_TIPO_AGENTE"
                elif event.key == pygame.K_F1:
                    return "Q_TREINO_RAPIDO"
                elif event.key == pygame.K_F2:
                    return "Q_DEMONSTRACAO"
                elif event.key == pygame.K_F3:
                    return "Q_PASSO_A_PASSO"
                elif event.key == pygame.K_t:
                    return "TOGGLE_TREINAMENTO_Q"
                elif event.key == pygame.K_x:
                    return "RESET_Q_LEARNING"
                elif event.key == pygame.K_F5:
                    return "SALVAR_Q"
                elif event.key == pygame.K_F9:
                    return "CARREGAR_Q"
                elif event.key == pygame.K_s:
                    if not agente.modo_ia:
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
                elif event.key == pygame.K_SPACE:
                    return "ATIRAR"
        return None

    def _clicou_secao(self, pos):
        for secao in self.secoes.values():
            if secao["rect"].collidepoint(pos):
                secao["aberta"] = not secao["aberta"]
                return True
        return False

    def desenhar(self, ambiente, agente, em_pausa, fps):
        self.hover_pos = pygame.mouse.get_pos()
        self.tela.fill(self.COR_BG)
        self._desenhar_fundo_global()

        for r in range(self.n):
            for c in range(self.n):
                rect = pygame.Rect(c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size)
                pos = (r, c)
                self._desenhar_celula_base(rect, pos in agente.kb.visited)

                if pos == (0, 0):
                    self._desenhar_marcador_inicial(rect)

                if pos in agente.kb.visited:
                    self._desenhar_percepcoes_na_celula(agente.kb.percepcoes[pos], rect)
                else:
                    if agente.kb.eh_segura(pos):
                        self._desenhar_destaque_seguro(rect)
                    elif pos in agente.kb.pocos_confirmados or (
                        not agente.kb.wumpus_movel and pos == agente.kb.wumpus_confirmado
                    ):
                        self._desenhar_destaque_perigo(rect)
                    else:
                        risco = agente.kb.calcular_probabilidade_risco(pos)
                        if risco > 0.0:
                            self._desenhar_badge_risco(risco, rect)

                if self.modo_visualizacao == "completa":
                    self._desenhar_elementos_reais(ambiente, pos, rect)

        agente_rect = pygame.Rect(
            agente.pos[1] * self.cell_size,
            agente.pos[0] * self.cell_size,
            self.cell_size,
            self.cell_size,
        )
        self._desenhar_agente(agente_rect, agente.has_gold, agente.simbolo_direcao(), agente.has_arrow)
        self._desenhar_sidebar(ambiente, agente, em_pausa, fps)

        pygame.display.flip()
        self.clock.tick(60)

    def _desenhar_fundo_global(self):
        pygame.draw.circle(self.tela, self.COR_BG_ACCENT_A, (160, 120), 180)
        pygame.draw.circle(self.tela, (20, 28, 52), (620, 760), 240)
        pygame.draw.circle(self.tela, self.COR_BG_ACCENT_B, (1110, 170), 190)

    def _desenhar_celula_base(self, rect, visitada):
        inner = rect.inflate(-4, -4)
        cor_inner = self.COR_GRID_VISITED if visitada else self.COR_GRID_FOG
        pygame.draw.rect(self.tela, self.COR_GRID_BASE, rect, border_radius=10)
        pygame.draw.rect(self.tela, cor_inner, inner, border_radius=8)
        pygame.draw.rect(self.tela, self.COR_STROKE_SOFT, rect, 1, border_radius=10)
        brilho = pygame.Surface((inner.width, inner.height), pygame.SRCALPHA)
        pygame.draw.rect(brilho, (255, 255, 255, 10 if visitada else 4), brilho.get_rect(), border_radius=8)
        self.tela.blit(brilho, inner.topleft)

    def _desenhar_marcador_inicial(self, rect):
        texto = self.fonte_micro.render("INICIAL", True, self.COR_DESTAQUE)
        badge = pygame.Rect(rect.x + 8, rect.y + 8, texto.get_width() + 10, 14)
        pygame.draw.rect(self.tela, self.COR_CARD_DEEP, badge, border_radius=7)
        pygame.draw.rect(self.tela, self.COR_DESTAQUE, badge, 1, border_radius=7)
        self.tela.blit(texto, (badge.x + 5, badge.y + 1))

    def _desenhar_percepcoes_na_celula(self, percepcao, rect):
        y = rect.y + 26 if rect.topleft == (0, 0) else rect.y + 8
        x = rect.x + 8
        if percepcao["brisa"]:
            self._desenhar_chip(rect, y, "BRISA", (118, 196, 255))
            self._desenhar_vento(rect)
            y += 18
        if percepcao["cheiro"]:
            self._desenhar_chip(rect, y, "CHEIRO", (197, 116, 255))
            self._desenhar_cheiro(rect)
            y += 18
        if percepcao["brilho"]:
            flare = pygame.Surface((rect.width - 10, rect.height - 10), pygame.SRCALPHA)
            pygame.draw.rect(flare, (244, 196, 66, 66), flare.get_rect(), border_radius=10)
            self.tela.blit(flare, (rect.x + 5, rect.y + 5))
            self._desenhar_chip(rect, y, "OURO", self.COR_OURO)
            self._desenhar_estrela((x + 18, rect.centery + 10), 8, self.COR_OURO)

    def _desenhar_chip(self, rect, y, texto, cor):
        txt = self.fonte_micro.render(texto, True, cor)
        badge = pygame.Rect(rect.x + 8, y, txt.get_width() + 10, 14)
        pygame.draw.rect(self.tela, self.COR_CARD_DEEP, badge, border_radius=7)
        pygame.draw.rect(self.tela, cor, badge, 1, border_radius=7)
        self.tela.blit(txt, (badge.x + 5, badge.y + 1))

    def _desenhar_vento(self, rect):
        base_y = rect.centery
        for idx in range(2):
            area = (rect.x + 8, base_y - 10 + idx * 10, rect.width - 16, 10)
            pygame.draw.arc(self.tela, (118, 196, 255), area, 0.25, 2.8, 2)

    def _desenhar_cheiro(self, rect):
        x = rect.right - 22
        for idx in range(3):
            pygame.draw.arc(self.tela, (197, 116, 255), (x + idx * 5, rect.centery - 2, 6, 14), 0, math.pi, 2)

    def _desenhar_estrela(self, centro, raio, cor):
        pontos = []
        for i in range(10):
            ang = math.pi / 2 + i * math.pi / 5
            r = raio if i % 2 == 0 else raio // 2
            pontos.append((centro[0] + math.cos(ang) * r, centro[1] - math.sin(ang) * r))
        pygame.draw.polygon(self.tela, cor, pontos)

    def _desenhar_destaque_seguro(self, rect):
        inner = rect.inflate(-8, -8)
        glow = pygame.Surface((inner.width, inner.height), pygame.SRCALPHA)
        pygame.draw.rect(glow, (78, 201, 140, 54), glow.get_rect(), border_radius=8)
        self.tela.blit(glow, inner.topleft)
        pygame.draw.rect(self.tela, self.COR_VERDE, inner, 2, border_radius=8)

    def _desenhar_destaque_perigo(self, rect):
        inner = rect.inflate(-8, -8)
        glow = pygame.Surface((inner.width, inner.height), pygame.SRCALPHA)
        pygame.draw.rect(glow, (247, 104, 104, 54), glow.get_rect(), border_radius=8)
        self.tela.blit(glow, inner.topleft)
        pygame.draw.rect(self.tela, self.COR_VERMELHO, inner, 2, border_radius=8)
        self._desenhar_simbolo_perigo(inner)

    def _desenhar_simbolo_perigo(self, rect):
        centro = rect.center
        sz = rect.width // 5
        pontos = [
            (centro[0], centro[1] - sz),
            (centro[0] + sz, centro[1] + sz),
            (centro[0] - sz, centro[1] + sz),
        ]
        pygame.draw.polygon(self.tela, self.COR_OURO, pontos)
        pygame.draw.polygon(self.tela, self.COR_VERMELHO, pontos, 2)
        txt = self.fonte_pequena.render("!", True, (0, 0, 0))
        self.tela.blit(txt, txt.get_rect(center=(centro[0], centro[1] + sz // 3)))

    def _desenhar_badge_risco(self, risco, rect):
        if self.cell_size <= 45:
            return
        cor = self.COR_ALERTA if risco < 0.5 else self.COR_VERMELHO
        txt = self.fonte_micro.render(f"{risco:.0%}", True, cor)
        badge = pygame.Rect(rect.x + 7, rect.bottom - 18, txt.get_width() + 10, 13)
        pygame.draw.rect(self.tela, self.COR_CARD_DEEP, badge, border_radius=6)
        pygame.draw.rect(self.tela, cor, badge, 1, border_radius=6)
        self.tela.blit(txt, (badge.x + 5, badge.y + 1))

    def _desenhar_elementos_reais(self, ambiente, pos, rect):
        if pos in ambiente.pocos:
            self._desenhar_poco(rect)
        if pos == ambiente.ouro_pos:
            self._desenhar_ouro(rect)
        if pos == ambiente.wumpus_pos:
            self._desenhar_wumpus(rect)

    def _desenhar_poco(self, rect):
        centro = rect.center
        for raio in range(rect.width // 3, 2, -3):
            tom = 18 + raio * 3
            pygame.draw.circle(self.tela, (tom, tom, tom), centro, raio)
        pygame.draw.circle(self.tela, (6, 8, 12), centro, 6)
        pygame.draw.circle(self.tela, (112, 90, 75), centro, rect.width // 3, 2)

    def _desenhar_ouro(self, rect):
        centro = rect.center
        corpo = pygame.Rect(centro[0] - 14, centro[1] - 2, 28, 16)
        tampa = pygame.Rect(centro[0] - 14, centro[1] - 12, 28, 14)
        pygame.draw.rect(self.tela, (132, 74, 25), corpo, border_radius=4)
        pygame.draw.rect(self.tela, (92, 46, 14), corpo, 2, border_radius=4)
        pygame.draw.ellipse(self.tela, (171, 100, 41), tampa)
        pygame.draw.ellipse(self.tela, (92, 46, 14), tampa, 2)
        pygame.draw.rect(self.tela, self.COR_OURO, (centro[0] - 3, centro[1] + 1, 6, 8), border_radius=2)
        self._desenhar_estrela((centro[0] + 18, centro[1] - 12), 6, self.COR_OURO)

    def _desenhar_wumpus(self, rect):
        frame_tamanho = max(26, int(rect.width * 0.6))
        frame = pygame.Rect(0, 0, frame_tamanho, frame_tamanho)
        frame.center = rect.center

        # Brilho roxo ao redor
        glow = pygame.Surface((frame.width + 18, frame.height + 18), pygame.SRCALPHA)
        pygame.draw.circle(glow, (209, 96, 255, 50), (glow.get_width() // 2, glow.get_height() // 2), frame.width // 2 + 6)
        self.tela.blit(glow, (frame.x - 9, frame.y - 9))

        # Fundo circular
        pygame.draw.ellipse(self.tela, self.COR_CARD_DEEP, frame)
        pygame.draw.ellipse(self.tela, self.COR_WUMPUS, frame, 2)

        # Renderizar sprite com mascara circular
        if self.sprite_wumpus_original is not None:
            tamanho = max(frame.width, frame.height)
            sprite = pygame.transform.smoothscale(self.sprite_wumpus_original, (tamanho, tamanho))
            recorte = pygame.Rect(
                (sprite.get_width() - frame.width) // 2,
                (sprite.get_height() - frame.height) // 3,
                frame.width,
                frame.height,
            )
            sprite_crop = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
            sprite_crop.blit(sprite, (0, 0), recorte)
            mascara = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
            pygame.draw.ellipse(mascara, (255, 255, 255, 255), mascara.get_rect())
            sprite_crop.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.tela.blit(sprite_crop, frame.topleft)
            # Leve brilho
            brilho = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
            pygame.draw.ellipse(brilho, (209, 96, 255, 20), brilho.get_rect())
            self.tela.blit(brilho, frame.topleft)
        else:
            # Fallback: desenho simples se a imagem nao carregar
            centro = rect.center
            raio = rect.width // 4
            pygame.draw.circle(self.tela, self.COR_WUMPUS, centro, raio + 2)
            pygame.draw.circle(self.tela, (78, 32, 104), centro, raio + 2, 2)
            pygame.draw.circle(self.tela, (255, 88, 112), (centro[0] - 6, centro[1] - 4), 3)
            pygame.draw.circle(self.tela, (255, 88, 112), (centro[0] + 6, centro[1] - 4), 3)

    def _desenhar_agente(self, rect, tem_ouro, simbolo_direcao, tem_flecha):
        frame_tamanho = max(26, int(rect.width * 0.54))
        frame = pygame.Rect(0, 0, frame_tamanho, frame_tamanho)
        frame.centerx = rect.centerx
        frame.centery = rect.centery + max(0, rect.height // 16)

        glow = pygame.Surface((frame.width + 18, frame.height + 18), pygame.SRCALPHA)
        pygame.draw.circle(glow, (79, 172, 254, 42), (glow.get_width() // 2, glow.get_height() // 2), frame.width // 2 + 4)
        self.tela.blit(glow, (frame.x - 9, frame.y - 9))

        pygame.draw.ellipse(self.tela, self.COR_CARD_DEEP, frame)
        pygame.draw.ellipse(self.tela, self.COR_DESTAQUE, frame, 2)
        self._desenhar_sprite_agente(frame)

        if tem_ouro:
            bolsa = pygame.Rect(frame.right - 14, frame.bottom - 14, 12, 12)
            pygame.draw.circle(self.tela, self.COR_OURO, bolsa.center, 6)
            pygame.draw.line(self.tela, (145, 110, 28), (bolsa.centerx - 3, bolsa.y + 2), (bolsa.centerx + 3, bolsa.y + 2), 2)

        if tem_flecha:
            self._desenhar_flecha_no_peito(frame)

        self._desenhar_indicador_direcao_inferior(rect, simbolo_direcao)

    def _desenhar_sprite_agente(self, frame):
        if self.sprite_agente_original is None:
            pygame.draw.ellipse(self.tela, (214, 174, 108), frame)
            return
        tamanho = max(frame.width, frame.height)
        sprite = pygame.transform.smoothscale(self.sprite_agente_original, (tamanho, tamanho))
        recorte = pygame.Rect((sprite.get_width() - frame.width) // 2, (sprite.get_height() - frame.height) // 3, frame.width, frame.height)
        sprite_crop = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
        sprite_crop.blit(sprite, (0, 0), recorte)
        mascara = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
        pygame.draw.ellipse(mascara, (255, 255, 255, 255), mascara.get_rect())
        sprite_crop.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.tela.blit(sprite_crop, frame.topleft)
        brilho = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
        pygame.draw.ellipse(brilho, (255, 255, 255, 16), brilho.get_rect())
        self.tela.blit(brilho, frame.topleft)

    def _desenhar_flecha_no_peito(self, frame):
        base = (frame.x + 6, frame.bottom - 12)
        ponta = (base[0] + 11, base[1] - 4)
        pygame.draw.line(self.tela, (196, 146, 83), base, ponta, 2)
        pygame.draw.polygon(self.tela, (230, 230, 235), [ponta, (ponta[0] - 4, ponta[1] - 2), (ponta[0] - 3, ponta[1] + 3)])
        pygame.draw.line(self.tela, (230, 94, 94), base, (base[0] + 4, base[1] - 5), 2)

    def _desenhar_indicador_direcao_inferior(self, rect, simbolo_direcao):
        badge = pygame.Rect(0, 0, max(34, rect.width // 2), 18)
        badge.centerx = rect.centerx
        badge.y = rect.bottom - 16
        pygame.draw.rect(self.tela, self.COR_CARD_DEEP, badge, border_radius=10)
        pygame.draw.rect(self.tela, self.COR_DESTAQUE, badge, 2, border_radius=10)

        cx, cy = badge.center
        cor = (244, 248, 255)
        corpo = 8
        asa = 5
        if simbolo_direcao == ">":
            pygame.draw.line(self.tela, cor, (cx - corpo, cy), (cx + corpo, cy), 3)
            pygame.draw.line(self.tela, cor, (cx + corpo, cy), (cx + corpo - asa, cy - asa), 3)
            pygame.draw.line(self.tela, cor, (cx + corpo, cy), (cx + corpo - asa, cy + asa), 3)
        elif simbolo_direcao == "<":
            pygame.draw.line(self.tela, cor, (cx + corpo, cy), (cx - corpo, cy), 3)
            pygame.draw.line(self.tela, cor, (cx - corpo, cy), (cx - corpo + asa, cy - asa), 3)
            pygame.draw.line(self.tela, cor, (cx - corpo, cy), (cx - corpo + asa, cy + asa), 3)
        elif simbolo_direcao == "^":
            pygame.draw.line(self.tela, cor, (cx, cy + corpo - 1), (cx, cy - corpo + 1), 3)
            pygame.draw.line(self.tela, cor, (cx, cy - corpo + 1), (cx - asa, cy - corpo + asa), 3)
            pygame.draw.line(self.tela, cor, (cx, cy - corpo + 1), (cx + asa, cy - corpo + asa), 3)
        else:
            pygame.draw.line(self.tela, cor, (cx, cy - corpo + 1), (cx, cy + corpo - 1), 3)
            pygame.draw.line(self.tela, cor, (cx, cy + corpo - 1), (cx - asa, cy + corpo - asa), 3)
            pygame.draw.line(self.tela, cor, (cx, cy + corpo - 1), (cx + asa, cy + corpo - asa), 3)

    def _desenhar_sidebar(self, ambiente, agente, em_pausa, fps):
        x0 = self.largura_grade
        painel = pygame.Rect(x0, 0, self.largura_painel, self.altura)
        pygame.draw.rect(self.tela, self.COR_PANEL, painel)
        pygame.draw.line(self.tela, self.COR_STROKE, (x0, 0), (x0, self.altura), 2)

        largura_card = self.largura_painel - self.SPACE_OUTER * 2
        x = x0 + self.SPACE_OUTER
        y = self.SPACE_OUTER

        header_rect = pygame.Rect(x, y, largura_card, self.HEADER_H)
        self._draw_section_card(header_rect)
        self._desenhar_header_compacto(header_rect, ambiente, agente, em_pausa)
        topo_secoes = header_rect.bottom + self.SPACE_SECTION

        layout, conteudo_total = self._layout_sidebar_sections(topo_secoes, agente)

        # Calcular scroll maximo
        self.sidebar_max_scroll = max(0, conteudo_total - (self.altura - self.SPACE_OUTER))
        self.sidebar_scroll = max(0, min(self.sidebar_scroll, self.sidebar_max_scroll))

        # Clipping para a area abaixo do header
        clip_prev = self.tela.get_clip()
        sidebar_clip = pygame.Rect(x0, topo_secoes, self.largura_painel, self.altura - topo_secoes)
        self.tela.set_clip(sidebar_clip)

        # Aplicar scroll offset a cada secao
        for chave in ["configuracao", "telemetria", "registro", "comandos"]:
            r = layout[chave]
            scrolled = pygame.Rect(r.x, r.y - self.sidebar_scroll, r.width, r.height)
            # Pular se totalmente fora da tela
            if scrolled.bottom < topo_secoes or scrolled.top > self.altura:
                continue
            self._draw_section_card(scrolled)
            if chave == "configuracao":
                self._desenhar_secao_configuracao(scrolled, ambiente.n, agente)
            elif chave == "telemetria":
                self._desenhar_secao_telemetria(scrolled, ambiente, agente, fps)
            elif chave == "registro":
                self._desenhar_secao_registro(scrolled, agente)
            elif chave == "comandos":
                self._desenhar_secao_comandos(scrolled, agente)

        self.tela.set_clip(clip_prev)

        # Indicador de scroll
        if self.sidebar_max_scroll > 0:
            self._desenhar_scrollbar(x0, topo_secoes, self.altura - topo_secoes)

    def _desenhar_scrollbar(self, x0, topo, altura_visivel):
        if self.sidebar_max_scroll <= 0:
            return
        total_conteudo = altura_visivel + self.sidebar_max_scroll
        thumb_h = max(20, int(altura_visivel * altura_visivel / total_conteudo))
        thumb_y = topo + int(self.sidebar_scroll / self.sidebar_max_scroll * (altura_visivel - thumb_h))
        bar_x = x0 + self.largura_painel - 6
        pygame.draw.rect(self.tela, self.COR_STROKE_SOFT, (bar_x, thumb_y, 4, thumb_h), border_radius=2)

    def _calcular_config_body_h(self, agente):
        """Calcula a altura exata do corpo da secao Configuracao."""
        h = 0
        # Modo de jogo: label(16) + botao(28) + gap(8)
        h += 16 + self.CONTROL_H + 8

        if agente.modo_ia:
            # Tipo de agente: label(16) + botao(28) + gap(8)
            h += 16 + self.CONTROL_H + 8

        if agente.modo_ia and agente.tipo_agente == "q_learning":
            # Operacao Q-Learning: label(16) + botao(28) + gap(8)
            h += 16 + self.CONTROL_H + 8
            # Reset/Salvar/Carregar: botao(28) + gap(8)
            h += self.CONTROL_H + 8

        if not (agente.modo_ia and agente.tipo_agente == "q_learning"):
            # Visualizacao: label(16) + botao(28) + gap(8)
            h += 16 + self.CONTROL_H + 8
            # Escala do mundo: label(16) + botao(28) + gap(8)
            h += 16 + self.CONTROL_H + 8
            # Densidade de pocos: label(16) + botao(28)
            h += 16 + self.CONTROL_H

        return h

    def _calcular_telemetria_body_h(self, agente):
        """Calcula a altura exata do corpo da secao Telemetria."""
        if not agente.modo_ia:
            return 7 * self.SPACE_ROW + 4
        if agente.tipo_agente == "regras":
            return 9 * self.SPACE_ROW + 4
        # Q-Learning: 17 linhas de telemetria + grafico
        return 17 * min(self.SPACE_ROW, 18) + 80

    def _layout_sidebar_sections(self, topo, agente):
        x = self.largura_grade + self.SPACE_OUTER
        largura = self.largura_painel - self.SPACE_OUTER * 2
        gap = self.SPACE_SECTION
        header_pad = self.SECTION_HEADER_H + 16  # header + padding

        # Calcular alturas reais do corpo de cada secao
        config_body_h = self._calcular_config_body_h(agente) if self.secoes["configuracao"]["aberta"] else 0
        tele_body_h = self._calcular_telemetria_body_h(agente) if self.secoes["telemetria"]["aberta"] else 0
        cmd_body_h = 76 if self.secoes["comandos"]["aberta"] else 0
        logs_body_h = self.LOG_MAX_H if self.secoes["registro"]["aberta"] else 0

        config_h = header_pad + config_body_h
        tele_h = header_pad + tele_body_h
        logs_h = header_pad + logs_body_h
        cmd_h = header_pad + cmd_body_h

        rects = {}
        y = topo
        for chave, h in [
            ("configuracao", config_h),
            ("telemetria", tele_h),
            ("registro", logs_h),
            ("comandos", cmd_h),
        ]:
            rects[chave] = pygame.Rect(x, y, largura, h)
            y += h + gap

        conteudo_total = y - gap  # ultimo gap nao conta
        return rects, conteudo_total

    def _desenhar_header_compacto(self, rect, ambiente, agente, em_pausa):
        self.tela.blit(self.fonte_titulo.render("WUMPUS WORLD", True, self.COR_TEXTO), (rect.x + 12, rect.y + 8))
        self.tela.blit(
            self.fonte_micro.render("Painel lateral modular", True, self.COR_TEXTO_MUTED),
            (rect.x + 12, rect.y + 28),
        )

        status = "EXPLORANDO"
        cor = self.COR_DESTAQUE
        if not agente.alive:
            status = "FORA DE COMBATE"
            cor = self.COR_VERMELHO
            if agente.pos in ambiente.pocos:
                status = "PERDIDO NO POCO"
            elif agente.pos == ambiente.wumpus_pos:
                status = "ABATIDO PELO WUMPUS"
        elif agente.vitorioso:
            status = "MISSAO CONCLUIDA"
            cor = self.COR_VERDE
        elif agente.has_gold:
            status = "RETORNO COM OURO"
            cor = self.COR_OURO
        elif em_pausa:
            status = "PAUSADO"
            cor = self.COR_TEXTO_MUTED

        badge = pygame.Rect(rect.x + 12, rect.bottom - 20, 142, 14)
        pygame.draw.rect(self.tela, self.COR_CARD_DEEP, badge, border_radius=7)
        pygame.draw.rect(self.tela, cor, badge, 1, border_radius=7)
        txt = self.fonte_micro.render(status, True, cor)
        self.tela.blit(txt, txt.get_rect(center=badge.center))

    def _desenhar_secao_configuracao(self, rect, tamanho_atual, agente):
        body = self._draw_collapsible_header("configuracao", rect)
        if not self.secoes["configuracao"]["aberta"]:
            return

        x = body.x
        y = body.y
        largura = body.width
        self.botao_q_treino = pygame.Rect(0, 0, 0, 0)
        self.botao_q_demo = pygame.Rect(0, 0, 0, 0)
        self.botao_q_passo = pygame.Rect(0, 0, 0, 0)
        self.botao_q_reset = pygame.Rect(0, 0, 0, 0)
        self.botao_q_salvar = pygame.Rect(0, 0, 0, 0)
        self.botao_q_carregar = pygame.Rect(0, 0, 0, 0)
        self.botao_diminuir_mapa = pygame.Rect(0, 0, 0, 0)
        self.botao_aumentar_mapa = pygame.Rect(0, 0, 0, 0)
        self.botao_densidade_leve = pygame.Rect(0, 0, 0, 0)
        self.botao_densidade_normal = pygame.Rect(0, 0, 0, 0)
        self.botao_densidade_denso = pygame.Rect(0, 0, 0, 0)

        self.tela.blit(self.fonte_pequena.render("Modo de jogo", True, self.COR_TEXTO_MUTED), (x, y))
        y += 16
        largura_botao = (largura - self.SPACE_CONTROL_GAP) // 2
        self.botao_modo_humano = pygame.Rect(x, y, largura_botao, self.CONTROL_H)
        self.botao_modo_agente = pygame.Rect(x + largura_botao + self.SPACE_CONTROL_GAP, y, largura_botao, self.CONTROL_H)
        self._draw_button_group([
            (self.botao_modo_humano, "Humano", agente.modo_jogo == "humano"),
            (self.botao_modo_agente, "Agente automatico", agente.modo_jogo == "agente"),
        ])

        if agente.modo_ia:
            y += self.CONTROL_H + 8
            self.tela.blit(self.fonte_pequena.render("Tipo de agente", True, self.COR_TEXTO_MUTED), (x, y))
            y += 16
            self.botao_agente_regras = pygame.Rect(x, y, largura_botao, self.CONTROL_H)
            self.botao_agente_qlearning = pygame.Rect(x + largura_botao + self.SPACE_CONTROL_GAP, y, largura_botao, self.CONTROL_H)
            self._draw_button_group([
                (self.botao_agente_regras, "Regras", agente.tipo_agente == "regras"),
                (self.botao_agente_qlearning, "Q-Learning", agente.tipo_agente == "q_learning"),
            ])

        if agente.modo_ia and agente.tipo_agente == "q_learning":
            y += self.CONTROL_H + 8
            self.tela.blit(self.fonte_pequena.render("Operacao Q-Learning", True, self.COR_TEXTO_MUTED), (x, y))
            y += 16
            largura_q = (largura - self.SPACE_CONTROL_GAP * 2) // 3
            self.botao_q_treino = pygame.Rect(x, y, largura_q, self.CONTROL_H)
            self.botao_q_demo = pygame.Rect(x + largura_q + self.SPACE_CONTROL_GAP, y, largura_q, self.CONTROL_H)
            self.botao_q_passo = pygame.Rect(x + (largura_q + self.SPACE_CONTROL_GAP) * 2, y, largura_q, self.CONTROL_H)
            self._draw_button_group([
                (self.botao_q_treino, "Treino", agente.modo_q_learning == "treino_rapido"),
                (self.botao_q_demo, "Demo", agente.modo_q_learning == "demonstracao"),
                (self.botao_q_passo, "Passo", agente.modo_q_learning == "passo_a_passo"),
            ])

            y += self.CONTROL_H + 8
            largura_q = (largura - self.SPACE_CONTROL_GAP * 2) // 3
            self.botao_q_reset = pygame.Rect(x, y, largura_q, self.CONTROL_H)
            self.botao_q_salvar = pygame.Rect(x + largura_q + self.SPACE_CONTROL_GAP, y, largura_q, self.CONTROL_H)
            self.botao_q_carregar = pygame.Rect(x + (largura_q + self.SPACE_CONTROL_GAP) * 2, y, largura_q, self.CONTROL_H)
            self._draw_button_group([
                (self.botao_q_reset, "Reset", False),
                (self.botao_q_salvar, "Salvar", False),
                (self.botao_q_carregar, "Carregar", False),
            ])

        if not (agente.modo_ia and agente.tipo_agente == "q_learning"):
            y += self.CONTROL_H + 8
            self.tela.blit(self.fonte_pequena.render("Visualizacao", True, self.COR_TEXTO_MUTED), (x, y))
            y += 16
            largura_botao = (largura - self.SPACE_CONTROL_GAP) // 2
            self.botao_visao_agente = pygame.Rect(x, y, largura_botao, self.CONTROL_H)
            self.botao_visao_completa = pygame.Rect(x + largura_botao + self.SPACE_CONTROL_GAP, y, largura_botao, self.CONTROL_H)
            self._draw_button_group([
                (self.botao_visao_agente, "Visao do agente", self.modo_visualizacao == "agente"),
                (self.botao_visao_completa, "Visao completa", self.modo_visualizacao == "completa"),
            ])

        if not (agente.modo_ia and agente.tipo_agente == "q_learning"):
            y += self.CONTROL_H + 8
            self.tela.blit(self.fonte_pequena.render("Escala do mundo", True, self.COR_TEXTO_MUTED), (x, y))
            y += 16
            self.botao_diminuir_mapa = pygame.Rect(x, y, self.SMALL_BTN_W, self.CONTROL_H)
            self.botao_aumentar_mapa = pygame.Rect(x + largura - self.SMALL_BTN_W, y, self.SMALL_BTN_W, self.CONTROL_H)
            display = pygame.Rect(x + self.SMALL_BTN_W + self.SPACE_CONTROL_GAP, y, largura - (self.SMALL_BTN_W * 2) - (self.SPACE_CONTROL_GAP * 2), self.CONTROL_H)
            self._desenhar_botao_acao(self.botao_diminuir_mapa, "-")
            self._desenhar_botao_acao(self.botao_aumentar_mapa, "+")
            pygame.draw.rect(self.tela, self.COR_CARD_ALT, display, border_radius=10)
            pygame.draw.rect(self.tela, self.COR_STROKE_SOFT, display, 1, border_radius=10)
            txt = self.fonte_normal.render(f"{tamanho_atual} x {tamanho_atual}", True, self.COR_TEXTO)
            self.tela.blit(txt, txt.get_rect(center=display.center))

            y += self.CONTROL_H + 8
            self.tela.blit(self.fonte_pequena.render("Densidade de pocos", True, self.COR_TEXTO_MUTED), (x, y))
            y += 16
            largura_botao = (largura - self.SPACE_CONTROL_GAP * 2) // 3
            self.botao_densidade_leve = pygame.Rect(x, y, largura_botao, self.CONTROL_H)
            self.botao_densidade_normal = pygame.Rect(x + largura_botao + self.SPACE_CONTROL_GAP, y, largura_botao, self.CONTROL_H)
            self.botao_densidade_denso = pygame.Rect(x + (largura_botao + self.SPACE_CONTROL_GAP) * 2, y, largura_botao, self.CONTROL_H)
            self._draw_button_group([
                (self.botao_densidade_leve, "Leve", self.densidade_pocos == "leve"),
                (self.botao_densidade_normal, "Normal", self.densidade_pocos == "normal"),
                (self.botao_densidade_denso, "Denso", self.densidade_pocos == "denso"),
            ])

    def _desenhar_secao_telemetria(self, rect, ambiente, agente, fps):
        body = self._draw_collapsible_header("telemetria", rect)
        if not self.secoes["telemetria"]["aberta"]:
            return

        if not agente.modo_ia:
            dados = [
                ("Modo", "Humano"),
                ("Posicao", str(agente.pos)),
                ("Direcao", agente.simbolo_direcao()),
                ("Mapa", f"{ambiente.n} x {ambiente.n}"),
                ("Passos", str(agente.passos)),
                ("Ouro", "Sim" if agente.has_gold else "Nao"),
                ("Flecha", "Disponivel" if agente.has_arrow else "Usada"),
            ]
            self._draw_telemetry_grid(body, dados, agente)
            return

        if agente.tipo_agente == "regras":
            dados = [
                ("Modo", "Agente"),
                ("Tipo", "Regras"),
                ("Posicao", str(agente.pos)),
                ("Direcao", agente.simbolo_direcao()),
                ("Passos", str(agente.passos)),
                ("Visitadas", f"{len(agente.kb.visited)} / {ambiente.n * ambiente.n}"),
                ("Caminho", str(len(agente.caminho_atual))),
                ("Flecha", "Disponivel" if agente.has_arrow else "Usada"),
                ("Velocidade", f"{fps} Hz"),
            ]
            self._draw_telemetry_grid(body, dados, agente)
            return

        metricas = agente.q_learning.resumo_metricas()
        nomes_modo = {
            "treino_rapido": "Treino rapido",
            "demonstracao": "Demonstracao",
            "passo_a_passo": "Passo a passo",
        }
        dados = [
            ("Operacao", nomes_modo[agente.modo_q_learning]),
            ("Episodio", str(metricas["episodio"])),
            ("Passo", str(metricas["passo"])),
            ("Epsilon", f"{metricas['epsilon']:.3f}"),
            ("Alpha/Gamma", f"{metricas['alpha']:.2f}/{metricas['gamma']:.2f}"),
            ("Acao", metricas["ultima_acao"]),
            ("Q acao", f"{metricas['ultimo_valor_q']:.2f}"),
            ("R passo", f"{metricas['ultima_recompensa']:.1f}"),
            ("R episodio", f"{metricas['recompensa_episodio']:.1f}"),
            ("Melhor R", f"{metricas['melhor_recompensa']:.1f}"),
            ("Media R", f"{metricas['media_recente']:.1f}"),
            ("V/M/Lim", f"{metricas['vitorias']}/{metricas['mortes']}/{metricas['timeouts']}"),
            ("Sucesso", f"{metricas['taxa_sucesso']:.0%}"),
            ("Sobrev.", f"{metricas['taxa_sobrevivencia_recente']:.0%}"),
            ("Q-table", str(metricas["q_table"])),
            ("Fase", metricas["fase"]),
            ("Treino/s", f"{metricas['eps_por_seg']:.0f}"),
        ]
        grid_h = max(220, body.height - 62)
        grid_area = pygame.Rect(body.x, body.y, body.width, grid_h)
        self._draw_telemetry_grid(grid_area, dados, agente)
        grafico = pygame.Rect(body.x, grid_area.bottom + 8, body.width, max(54, body.bottom - grid_area.bottom - 8))
        self._desenhar_grafico_recompensas(grafico, agente)

    def _desenhar_secao_registro(self, rect, agente):
        body = self._draw_collapsible_header("registro", rect)
        if not self.secoes["registro"]["aberta"]:
            return
        self._draw_log_panel(body, agente)

    def _desenhar_secao_comandos(self, rect, agente):
        body = self._draw_collapsible_header("comandos", rect)
        if not self.secoes["comandos"]["aberta"]:
            return
        if not agente.modo_ia:
            linhas = [
                "[C] Agente automatico   [R] Reiniciar",
                "[Setas/WASD] Girar/mover   [SPACE] Atirar",
                "[P] Pausar   [M] Wumpus movel   [+/-] Velocidade",
            ]
        elif agente.tipo_agente == "regras":
            linhas = [
                "[C] Humano   [Q] Q-Learning   [S] Passo",
                "[P] Pausar   [R] Reiniciar   [M] Wumpus movel",
                "[+/-] Velocidade",
            ]
        else:
            linhas = [
                "[Q] Regras   [T] Liga/desliga treino",
                "[S] Passo unico   [X] Reset Q-table",
                "[F5] Salvar Q   [F9] Carregar Q   [+/-] Velocidade",
            ]
        for idx, linha in enumerate(linhas):
            cor = self.COR_TEXTO_MUTED if idx == 1 else self.COR_TEXTO
            self._desenhar_texto_limitado(self.fonte_pequena, linha, cor, body.x, body.y + idx * 18, body.width)

    def _draw_section_card(self, rect):
        self._desenhar_card(rect)

    def _draw_collapsible_header(self, chave, rect):
        header = pygame.Rect(rect.x + 8, rect.y + 8, rect.width - 16, self.SECTION_HEADER_H)
        self.secoes[chave]["rect"] = header
        hovered = header.collidepoint(self.hover_pos)
        fundo = self.COR_CARD_HOVER if hovered else self.COR_CARD_ALT
        borda = self.COR_DESTAQUE_SOFT if hovered else self.COR_STROKE_SOFT
        pygame.draw.rect(self.tela, fundo, header, border_radius=12)
        pygame.draw.rect(self.tela, borda, header, 1, border_radius=12)

        titulo = self.secoes[chave]["titulo"]
        self.tela.blit(self.fonte_subtitulo.render(titulo, True, self.COR_TEXTO), (header.x + 12, header.y + 5))
        seta = "v" if self.secoes[chave]["aberta"] else ">"
        seta_cor = self.COR_DESTAQUE if hovered else self.COR_TEXTO_MUTED
        txt_seta = self.fonte_subtitulo.render(seta, True, seta_cor)
        self.tela.blit(txt_seta, txt_seta.get_rect(center=(header.right - 16, header.centery)))

        body = pygame.Rect(
            rect.x + self.SPACE_CARD_PAD,
            header.bottom + 8,
            rect.width - self.SPACE_CARD_PAD * 2,
            max(0, rect.bottom - header.bottom - self.SPACE_CARD_PAD - 8),
        )
        return body

    def _draw_button_group(self, botoes):
        for rect, texto, ativo in botoes:
            self._desenhar_botao(rect, texto, ativo)

    def _desenhar_grafico_recompensas(self, rect, agente):
        pygame.draw.rect(self.tela, self.COR_CARD_DEEP, rect, border_radius=10)
        pygame.draw.rect(self.tela, self.COR_STROKE_SOFT, rect, 1, border_radius=10)
        titulo = self.fonte_micro.render("Recompensas recentes", True, self.COR_TEXTO_MUTED)
        self.tela.blit(titulo, (rect.x + 8, rect.y + 5))

        valores = list(agente.q_learning.recompensas_recentes)[-30:]
        area = pygame.Rect(rect.x + 8, rect.y + 20, rect.width - 16, rect.height - 28)
        if not valores or area.height <= 8:
            self._desenhar_texto_limitado(self.fonte_micro, "Sem episodios finalizados", self.COR_TEXTO_MUTED, area.x, area.y, area.width)
            return

        minimo = min(valores)
        maximo = max(valores)
        if minimo == maximo:
            minimo -= 1
            maximo += 1
        zero_y = area.bottom - int((0 - minimo) / (maximo - minimo) * area.height)
        zero_y = max(area.y, min(area.bottom, zero_y))
        pygame.draw.line(self.tela, self.COR_STROKE_SOFT, (area.x, zero_y), (area.right, zero_y), 1)

        largura_barra = max(2, area.width // len(valores))
        for idx, valor in enumerate(valores):
            proporcao = (valor - minimo) / (maximo - minimo)
            altura = max(2, int(proporcao * area.height))
            x = area.x + idx * largura_barra
            y = area.bottom - altura
            cor = self.COR_VERDE if valor >= 0 else self.COR_VERMELHO
            pygame.draw.rect(self.tela, cor, (x, y, max(1, largura_barra - 1), altura), border_radius=2)

    def _draw_telemetry_grid(self, body, dados, agente):
        label_x = body.x
        value_right = body.right
        row_y = body.y
        passo_linha = min(self.SPACE_ROW, max(13, body.height // max(1, len(dados))))
        for idx, (rotulo, valor) in enumerate(dados):
            valor_cor = self.COR_TEXTO
            if rotulo == "Flecha" and agente.has_arrow:
                valor_cor = self.COR_OURO
            elif rotulo == "Modo" and agente.modo_ia:
                valor_cor = self.COR_DESTAQUE
            elif rotulo == "Modo":
                valor_cor = self.COR_VERDE
            elif rotulo == "Velocidade":
                valor_cor = self.COR_ALERTA
            elif rotulo in ("Recompensa", "Epsilon", "Q-table"):
                valor_cor = self.COR_OURO
            elif rotulo == "Tipo" and agente.tipo_agente == "q_learning":
                valor_cor = self.COR_DESTAQUE

            fonte_valor = self.fonte_pequena if passo_linha < 18 else self.fonte_normal
            self.tela.blit(self.fonte_pequena.render(rotulo, True, self.COR_TEXTO_MUTED), (label_x, row_y + 1))
            valor_rect = pygame.Rect(value_right - self.TELEMETRY_VALUE_W, row_y, self.TELEMETRY_VALUE_W, max(16, passo_linha - 2))
            txt = fonte_valor.render(valor, True, valor_cor)
            self.tela.blit(txt, txt.get_rect(midright=(valor_rect.right, valor_rect.centery + 1)))

            if idx < len(dados) - 1:
                pygame.draw.line(self.tela, self.COR_STROKE_SOFT, (body.x, row_y + passo_linha - 2), (body.right, row_y + passo_linha - 2), 1)
            row_y += passo_linha

    def _draw_log_panel(self, body, agente):
        area = pygame.Rect(body.x, body.y, body.width, body.height)
        pygame.draw.rect(self.tela, self.COR_CARD_DEEP, area, border_radius=12)
        pygame.draw.rect(self.tela, self.COR_STROKE_SOFT, area, 1, border_radius=12)

        clip_prev = self.tela.get_clip()
        clip_area = area.inflate(-12, -10)
        self.tela.set_clip(clip_area)

        linhas_max = max(5, clip_area.height // 17)
        y = clip_area.y
        for entrada in agente.log[-linhas_max:]:
            cor = self.COR_TEXTO
            if "VITORIA" in entrada or "MISSAO" in entrada:
                cor = self.COR_VERDE
            elif "Morte" in entrada or "MORREU" in entrada:
                cor = self.COR_VERMELHO
            elif "Wumpus" in entrada:
                cor = self.COR_WUMPUS
            elif "Ouro" in entrada or "flecha" in entrada or "Flecha" in entrada:
                cor = self.COR_OURO
            elif "risco" in entrada or "Risco" in entrada:
                cor = self.COR_ALERTA
            self._desenhar_texto_limitado(self.fonte_micro, entrada, cor, clip_area.x, y, clip_area.width)
            y += 17

        self.tela.set_clip(clip_prev)

    def _desenhar_card(self, rect):
        pygame.draw.rect(self.tela, self.COR_CARD, rect, border_radius=18)
        pygame.draw.rect(self.tela, self.COR_STROKE, rect, 1, border_radius=18)
        brilho = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(brilho, (255, 255, 255, 7), brilho.get_rect(), border_radius=18)
        self.tela.blit(brilho, rect.topleft)

    def _desenhar_botao(self, rect, texto, ativo):
        hovered = rect.collidepoint(self.hover_pos)
        fundo = (40, 74, 112) if ativo else (self.COR_CARD_HOVER if hovered else self.COR_CARD_ALT)
        borda = self.COR_DESTAQUE if ativo else (self.COR_DESTAQUE_SOFT if hovered else self.COR_STROKE_SOFT)
        cor_texto = self.COR_TEXTO if ativo or hovered else self.COR_TEXTO_MUTED
        pygame.draw.rect(self.tela, fundo, rect, border_radius=12)
        pygame.draw.rect(self.tela, borda, rect, 2 if ativo else 1, border_radius=12)
        txt = self.fonte_pequena.render(texto, True, cor_texto)
        self.tela.blit(txt, txt.get_rect(center=rect.center))

    def _desenhar_botao_acao(self, rect, texto):
        hovered = rect.collidepoint(self.hover_pos)
        fundo = self.COR_CARD_HOVER if hovered else self.COR_CARD_ALT
        borda = self.COR_DESTAQUE_SOFT if hovered else self.COR_STROKE_SOFT
        pygame.draw.rect(self.tela, fundo, rect, border_radius=10)
        pygame.draw.rect(self.tela, borda, rect, 1, border_radius=10)
        txt = self.fonte_subtitulo.render(texto, True, self.COR_TEXTO)
        self.tela.blit(txt, txt.get_rect(center=rect.center))

    def _desenhar_texto_limitado(self, fonte, texto, cor, x, y, largura_max):
        render = texto
        while fonte.size(render)[0] > largura_max and len(render) > 1:
            render = render[:-2] + "..."
        self.tela.blit(fonte.render(render, True, cor), (x, y))
