import pygame
import time
from ambiente import Ambiente
from agente import Agente
from interface import InterfaceGrafica
from qlearning_runner import treinar_q_learning_em_lote

# ==========================================
# CONFIGURACOES INICIAIS DA SIMULACAO
# ==========================================
BOARD_SIZE = 6
NUM_PITS = None
PIT_DENSITY_MODE = "normal"  # leve=10%, normal=12.5%, denso=20%
WUMPUS_MOVEL = True
WUMPUS_MOVE_FREQUENCY = 3
SIMULATION_SPEED = 2
Q_TABLE_PATH = "q_table.json"
EPISODE_RESET_DELAY = 1.0
FAST_TRAIN_EPISODES_PER_CYCLE = 80
MAX_STEPS_PER_Q_EPISODE = 180
# ==========================================


def obter_densidade_pocos(modo):
    densidades = {
        "leve": 0.10,
        "normal": 0.125,
        "denso": 0.20,
    }
    return densidades.get(modo, 0.125)


def inicializar_jogo(n, num_pocos, wumpus_movel, modo_densidade):
    """
    Instancia ou reinicia o Ambiente, o Agente e limpa estados.
    """
    ambiente = Ambiente(
        n,
        num_pocos=num_pocos,
        wumpus_movel=wumpus_movel,
        densidade_pocos=obter_densidade_pocos(modo_densidade),
    )
    agente = Agente(n, wumpus_movel=wumpus_movel)
    return ambiente, agente


def recriar_jogo(
    interface,
    board_size,
    num_pits,
    wumpus_movel,
    pit_density_mode,
    agente_anterior=None,
    novo_episodio=False,
):
    ambiente, agente = inicializar_jogo(board_size, num_pits, wumpus_movel, pit_density_mode)
    nova_interface = InterfaceGrafica(board_size, densidade_pocos=pit_density_mode)
    nova_interface.modo_visualizacao = interface.modo_visualizacao
    if agente_anterior is not None:
        agente.herdar_aprendizado_de(agente_anterior)
        agente.episodios = agente.q_learning.episodio_atual
        agente.passos_episodio = agente.q_learning.passo_atual
    agente.adicionar_log(f"Modo de jogo: {'Agente automatico' if agente.modo_ia else 'Humano'}")
    agente.adicionar_log(
        f"Tipo de agente: {'Q-Learning' if agente.tipo_agente == 'q_learning' else 'Baseado em regras'}"
    )
    return ambiente, agente, nova_interface


def main():
    global BOARD_SIZE, NUM_PITS, PIT_DENSITY_MODE, WUMPUS_MOVEL, WUMPUS_MOVE_FREQUENCY, SIMULATION_SPEED

    if BOARD_SIZE < 4:
        print("Tamanho minimo do tabuleiro e 4x4. Ajustando BOARD_SIZE para 4.")
        BOARD_SIZE = 4

    ambiente, agente = inicializar_jogo(BOARD_SIZE, NUM_PITS, WUMPUS_MOVEL, PIT_DENSITY_MODE)
    interface = InterfaceGrafica(BOARD_SIZE, densidade_pocos=PIT_DENSITY_MODE)

    em_pausa = False
    ultimo_passo_tempo = time.time()
    momento_fim_episodio = None

    rodando = True
    while rodando:
        cmd = interface.processar_eventos(agente)

        if cmd == "PAUSAR":
            em_pausa = not em_pausa
            agente.adicionar_log("Simulacao PAUSADA" if em_pausa else "Simulacao RETOMADA")
        elif cmd == "REINICIAR":
            ambiente, agente, interface = recriar_jogo(
                interface, BOARD_SIZE, NUM_PITS, WUMPUS_MOVEL, PIT_DENSITY_MODE, agente, novo_episodio=True
            )
            ultimo_passo_tempo = time.time()
            momento_fim_episodio = None
            em_pausa = False
            agente.adicionar_log("Simulacao reiniciada com novo tabuleiro.")
            agente.adicionar_log(f"Modo de controle: {'IA (Automatico)' if agente.modo_ia else 'MANUAL (Teclado)'}")
        elif cmd == "MODO_WUMPUS":
            WUMPUS_MOVEL = not WUMPUS_MOVEL
            ambiente.wumpus_movel = WUMPUS_MOVEL
            agente.wumpus_movel = WUMPUS_MOVEL
            agente.kb.wumpus_movel = WUMPUS_MOVEL
            if WUMPUS_MOVEL and agente.kb.wumpus_vivo:
                agente.kb.possiveis_posicoes_wumpus = {
                    (r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if (r, c) != (0, 0)
                }
            agente.adicionar_log(f"Wumpus Movel: {'ATIVADO' if WUMPUS_MOVEL else 'DESATIVADO'}")
        elif cmd == "TOGGLE_IA":
            agente.configurar_modo_jogo("humano" if agente.modo_ia else "agente")
        elif cmd == "MODO_HUMANO":
            agente.configurar_modo_jogo("humano")
        elif cmd == "MODO_AGENTE":
            agente.configurar_modo_jogo("agente")
        elif cmd == "TIPO_REGRAS":
            agente.configurar_tipo_agente("regras")
        elif cmd == "TIPO_Q_LEARNING":
            agente.configurar_tipo_agente("q_learning")
        elif cmd == "TOGGLE_TIPO_AGENTE":
            agente.configurar_tipo_agente("regras" if agente.tipo_agente == "q_learning" else "q_learning")
        elif cmd == "Q_TREINO_RAPIDO":
            agente.configurar_modo_jogo("agente")
            agente.configurar_tipo_agente("q_learning")
            agente.configurar_modo_q_learning("treino_rapido")
            agente.treinamento_q = True
            em_pausa = False
        elif cmd == "Q_DEMONSTRACAO":
            agente.configurar_modo_jogo("agente")
            agente.configurar_tipo_agente("q_learning")
            agente.configurar_modo_q_learning("demonstracao")
            agente.treinamento_q = False
            ambiente, agente, interface = recriar_jogo(
                interface, BOARD_SIZE, NUM_PITS, WUMPUS_MOVEL, PIT_DENSITY_MODE, agente
            )
            ultimo_passo_tempo = time.time()
            momento_fim_episodio = None
        elif cmd == "Q_PASSO_A_PASSO":
            agente.configurar_modo_jogo("agente")
            agente.configurar_tipo_agente("q_learning")
            agente.configurar_modo_q_learning("passo_a_passo")
            agente.treinamento_q = True
        elif cmd == "TOGGLE_TREINAMENTO_Q":
            agente.alternar_treinamento_q()
        elif cmd == "RESET_Q_LEARNING":
            agente.reiniciar_treinamento_q()
        elif cmd == "SALVAR_Q":
            agente.q_learning.salvar(Q_TABLE_PATH)
            agente.adicionar_log(f"Q-table salva em {Q_TABLE_PATH}.")
        elif cmd == "CARREGAR_Q":
            try:
                agente.q_learning.carregar(Q_TABLE_PATH)
                agente.adicionar_log(f"Q-table carregada de {Q_TABLE_PATH}.")
            except FileNotFoundError:
                agente.adicionar_log(f"Nenhuma Q-table encontrada em {Q_TABLE_PATH}.")
        elif cmd == "VISAO_AGENTE":
            agente.adicionar_log("Visualizacao alterada para: visao do agente")
        elif cmd == "VISAO_COMPLETA":
            agente.adicionar_log("Visualizacao alterada para: visao completa do mapa")
        elif cmd == "MAPA_MAIS":
            BOARD_SIZE += 1
            ambiente, agente, interface = recriar_jogo(
                interface, BOARD_SIZE, NUM_PITS, WUMPUS_MOVEL, PIT_DENSITY_MODE, agente, novo_episodio=True
            )
            ultimo_passo_tempo = time.time()
            momento_fim_episodio = None
            em_pausa = False
            agente.adicionar_log(f"Tamanho do mapa alterado para {BOARD_SIZE}x{BOARD_SIZE}.")
            agente.adicionar_log(f"Modo de controle: {'IA (Automatico)' if agente.modo_ia else 'MANUAL (Teclado)'}")
        elif cmd == "MAPA_MENOS":
            if BOARD_SIZE > 4:
                BOARD_SIZE -= 1
                ambiente, agente, interface = recriar_jogo(
                    interface, BOARD_SIZE, NUM_PITS, WUMPUS_MOVEL, PIT_DENSITY_MODE, agente, novo_episodio=True
                )
                ultimo_passo_tempo = time.time()
                momento_fim_episodio = None
                em_pausa = False
                agente.adicionar_log(f"Tamanho do mapa alterado para {BOARD_SIZE}x{BOARD_SIZE}.")
                agente.adicionar_log(f"Modo de controle: {'IA (Automatico)' if agente.modo_ia else 'MANUAL (Teclado)'}")
            else:
                agente.adicionar_log("Tamanho minimo do mapa: 4x4.")
        elif cmd == "DENSIDADE_LEVE":
            PIT_DENSITY_MODE = "leve"
            ambiente, agente, interface = recriar_jogo(
                interface, BOARD_SIZE, NUM_PITS, WUMPUS_MOVEL, PIT_DENSITY_MODE, agente, novo_episodio=True
            )
            ultimo_passo_tempo = time.time()
            momento_fim_episodio = None
            em_pausa = False
            agente.adicionar_log("Densidade de pocos alterada para: leve")
        elif cmd == "DENSIDADE_NORMAL":
            PIT_DENSITY_MODE = "normal"
            ambiente, agente, interface = recriar_jogo(
                interface, BOARD_SIZE, NUM_PITS, WUMPUS_MOVEL, PIT_DENSITY_MODE, agente, novo_episodio=True
            )
            ultimo_passo_tempo = time.time()
            momento_fim_episodio = None
            em_pausa = False
            agente.adicionar_log("Densidade de pocos alterada para: normal")
        elif cmd == "DENSIDADE_DENSO":
            PIT_DENSITY_MODE = "denso"
            ambiente, agente, interface = recriar_jogo(
                interface, BOARD_SIZE, NUM_PITS, WUMPUS_MOVEL, PIT_DENSITY_MODE, agente, novo_episodio=True
            )
            ultimo_passo_tempo = time.time()
            momento_fim_episodio = None
            em_pausa = False
            agente.adicionar_log("Densidade de pocos alterada para: denso")
        elif cmd == "ATIRAR":
            acertou = agente.atirar_flecha(ambiente)
            if acertou:
                agente.adicionar_log("O fedor deve desaparecer das proximas percepcoes.")
        elif cmd in ["DIR_UP", "DIR_DOWN", "DIR_LEFT", "DIR_RIGHT"]:
            if agente.alive and not agente.vitorioso and not agente.modo_ia:
                r, c = agente.pos
                proxima_pos = agente.pos
                direcao_cmd = None
                if cmd == "DIR_UP":
                    direcao_cmd = "UP"
                    proxima_pos = (r - 1, c)
                elif cmd == "DIR_DOWN":
                    direcao_cmd = "DOWN"
                    proxima_pos = (r + 1, c)
                elif cmd == "DIR_LEFT":
                    direcao_cmd = "LEFT"
                    proxima_pos = (r, c - 1)
                elif cmd == "DIR_RIGHT":
                    direcao_cmd = "RIGHT"
                    proxima_pos = (r, c + 1)

                if agente.girar_para(direcao_cmd):
                    continue

                if 0 <= proxima_pos[0] < BOARD_SIZE and 0 <= proxima_pos[1] < BOARD_SIZE:
                    agente.mover_para(proxima_pos)
                    ambiente.agente_pos = proxima_pos

                    if WUMPUS_MOVEL and agente.passos > 0 and agente.passos % WUMPUS_MOVE_FREQUENCY == 0:
                        pos_antiga = ambiente.wumpus_pos
                        if ambiente.mover_wumpus():
                            agente.wumpus_moveu()
                            agente.adicionar_log(f"Wumpus moveu-se de {pos_antiga} para {ambiente.wumpus_pos}")
                            if ambiente.wumpus_pos == agente.pos:
                                agente.alive = False
                                agente.adicionar_log("Morte: O Wumpus se moveu para a celula do agente!")

                    if agente.pos in ambiente.pocos:
                        agente.alive = False
                        agente.adicionar_log("Morte: Agente caiu em um poco profundo!")
                    elif agente.pos == ambiente.wumpus_pos:
                        agente.alive = False
                        agente.adicionar_log("Morte: Agente foi devorado pelo Wumpus!")

                    if agente.alive:
                        percepcoes = ambiente.get_percepcoes(agente.pos)
                        agente.agir(percepcoes)
        elif cmd == "VEL_MAIS":
            SIMULATION_SPEED = min(20, SIMULATION_SPEED + 1)
            agente.adicionar_log(f"Velocidade aumentada para {SIMULATION_SPEED} Hz")
        elif cmd == "VEL_MENOS":
            SIMULATION_SPEED = max(1, SIMULATION_SPEED - 1)
            agente.adicionar_log(f"Velocidade reduzida para {SIMULATION_SPEED} Hz")

        if (
            agente.modo_ia
            and agente.tipo_agente == "q_learning"
            and agente.modo_q_learning == "treino_rapido"
            and not em_pausa
        ):
            treinar_q_learning_em_lote(
                agente.q_learning,
                BOARD_SIZE,
                NUM_PITS,
                obter_densidade_pocos(PIT_DENSITY_MODE),
                WUMPUS_MOVEL,
                WUMPUS_MOVE_FREQUENCY,
                episodios_por_lote=FAST_TRAIN_EPISODES_PER_CYCLE,
                max_passos_por_episodio=MAX_STEPS_PER_Q_EPISODE,
            )
            agente.episodios = agente.q_learning.episodio_atual
            agente.passos_episodio = agente.q_learning.passo_atual
            agente.ultima_acao = agente.q_learning.ultima_acao
            agente.ultima_recompensa = agente.q_learning.ultima_recompensa
            agente.ultimo_valor_q = agente.q_learning.ultimo_valor_q

        passo_manual = cmd == "PASSO"
        tempo_atual = time.time()
        deve_agir = False

        if agente.modo_ia and not (
            agente.tipo_agente == "q_learning" and agente.modo_q_learning == "treino_rapido"
        ):
            q_passo_a_passo = agente.tipo_agente == "q_learning" and agente.modo_q_learning == "passo_a_passo"
            if q_passo_a_passo:
                deve_agir = passo_manual
            elif (not em_pausa and (tempo_atual - ultimo_passo_tempo) >= (1.0 / SIMULATION_SPEED)) or passo_manual:
                deve_agir = True

        if deve_agir and agente.alive and not agente.vitorioso:
            ultimo_passo_tempo = tempo_atual

            if WUMPUS_MOVEL and agente.passos > 0 and agente.passos % WUMPUS_MOVE_FREQUENCY == 0:
                pos_antiga = ambiente.wumpus_pos
                if ambiente.mover_wumpus():
                    agente.wumpus_moveu()
                    agente.adicionar_log(f"Wumpus moveu-se de {pos_antiga} para {ambiente.wumpus_pos}")
                    if ambiente.wumpus_pos == agente.pos:
                        agente.alive = False
                        agente.adicionar_log("Morte: O Wumpus se moveu para a celula do agente!")

            if agente.alive:
                if agente.tipo_agente == "q_learning":
                    treinamento_visual = agente.modo_q_learning == "passo_a_passo" and agente.treinamento_q
                    agente.passo_q_learning(ambiente, treinamento=treinamento_visual)
                else:
                    percepcoes = ambiente.get_percepcoes(agente.pos)
                    agente.agir(percepcoes)
                    ambiente.agente_pos = agente.pos

                    if agente.pos in ambiente.pocos:
                        agente.alive = False
                        agente.adicionar_log("Morte: Agente caiu em um poco profundo!")
                    elif agente.pos == ambiente.wumpus_pos:
                        agente.alive = False
                        agente.adicionar_log("Morte: Agente foi devorado pelo Wumpus!")

        episodio_terminal = (
            agente.tipo_agente == "q_learning"
            and agente.modo_ia
            and agente.modo_q_learning != "treino_rapido"
            and (not agente.alive or agente.vitorioso)
        )
        if episodio_terminal and agente.modo_q_learning != "passo_a_passo":
            if momento_fim_episodio is None:
                momento_fim_episodio = time.time()
            elif time.time() - momento_fim_episodio >= EPISODE_RESET_DELAY:
                ambiente, agente, interface = recriar_jogo(
                    interface, BOARD_SIZE, NUM_PITS, WUMPUS_MOVEL, PIT_DENSITY_MODE, agente
                )
                ultimo_passo_tempo = time.time()
                momento_fim_episodio = None
                em_pausa = False
                agente.adicionar_log("Novo episodio Q-Learning iniciado.")
        elif not episodio_terminal:
            momento_fim_episodio = None

        interface.desenhar(ambiente, agente, em_pausa, SIMULATION_SPEED)

    pygame.quit()


if __name__ == "__main__":
    main()
