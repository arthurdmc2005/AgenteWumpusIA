import pygame
import time
from ambiente import Ambiente
from agente import Agente
from interface import InterfaceGrafica

# ==========================================
# CONFIGURAÇÕES INICIAIS DA SIMULAÇÃO
# ==========================================
BOARD_SIZE = 6               # Tamanho do tabuleiro N x N (mínimo 4x4)
NUM_PITS = None              # Número de poços (None = automático N²/8)
WUMPUS_MOVEL = True          # Habilita movimentação aleatória do Wumpus
WUMPUS_MOVE_FREQUENCY = 3    # Wumpus se move a cada X passos do agente
SIMULATION_SPEED = 2         # Velocidade padrão (passos por segundo, 1 a 20)
# ==========================================

def inicializar_jogo(n, num_pocos, wumpus_movel):
    """
    Instancia ou reinicia o Ambiente, o Agente e limpa estados.
    """
    ambiente = Ambiente(n, num_pocos=num_pocos, wumpus_movel=wumpus_movel)
    agente = Agente(n, wumpus_movel=wumpus_movel)
    return ambiente, agente

def main():
    global BOARD_SIZE, NUM_PITS, WUMPUS_MOVEL, WUMPUS_MOVE_FREQUENCY, SIMULATION_SPEED
    
    # Valida parâmetros de tamanho mínimo
    if BOARD_SIZE < 4:
        print("Tamanho mínimo do tabuleiro é 4x4. Ajustando BOARD_SIZE para 4.")
        BOARD_SIZE = 4
        
    ambiente, agente = inicializar_jogo(BOARD_SIZE, NUM_PITS, WUMPUS_MOVEL)
    interface = InterfaceGrafica(BOARD_SIZE)
    
    em_pausa = False
    ultimo_passo_tempo = time.time()
    
    rodando = True
    while rodando:
        # 1. Processamento de Eventos da Interface
        cmd = interface.processar_eventos(agente.modo_ia)
        
        if cmd == "PAUSAR":
            em_pausa = not em_pausa
            agente.adicionar_log("Simulação PAUSADA" if em_pausa else "Simulação RETOMADA")
        elif cmd == "REINICIAR":
            # Guarda a preferência de controle para o novo jogo
            pref_modo_ia = agente.modo_ia
            ambiente, agente = inicializar_jogo(BOARD_SIZE, NUM_PITS, WUMPUS_MOVEL)
            agente.modo_ia = pref_modo_ia
            ultimo_passo_tempo = time.time()
            em_pausa = False
            agente.adicionar_log("Simulação reiniciada com novo tabuleiro.")
            agente.adicionar_log(f"Modo de controle: {'IA (Automático)' if agente.modo_ia else 'MANUAL (Teclado)'}")
        elif cmd == "MODO_WUMPUS":
            WUMPUS_MOVEL = not WUMPUS_MOVEL
            ambiente.wumpus_movel = WUMPUS_MOVEL
            agente.wumpus_movel = WUMPUS_MOVEL
            agente.kb.wumpus_movel = WUMPUS_MOVEL
            # Ajusta base de crenças sobre o Wumpus caso seja alterado no meio do jogo
            if WUMPUS_MOVEL:
                agente.kb.possiveis_posicoes_wumpus = {(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if (r, c) != (0, 0)}
            agente.adicionar_log(f"Wumpus Móvel: {'ATIVADO' if WUMPUS_MOVEL else 'DESATIVADO'}")
        elif cmd == "TOGGLE_IA":
            agente.modo_ia = not agente.modo_ia
            agente.caminho_atual = [] # Limpa planos antigos
            agente.adicionar_log(f"Controle alterado para: {'IA (Automático)' if agente.modo_ia else 'MANUAL (Teclado)'}")
        elif cmd in ["DIR_UP", "DIR_DOWN", "DIR_LEFT", "DIR_RIGHT"]:
            if agente.alive and not agente.vitorioso and not agente.modo_ia:
                r, c = agente.pos
                proxima_pos = agente.pos
                if cmd == "DIR_UP": proxima_pos = (r - 1, c)
                elif cmd == "DIR_DOWN": proxima_pos = (r + 1, c)
                elif cmd == "DIR_LEFT": proxima_pos = (r, c - 1)
                elif cmd == "DIR_RIGHT": proxima_pos = (r, c + 1)
                
                # Verifica limites do tabuleiro antes de mover
                if 0 <= proxima_pos[0] < BOARD_SIZE and 0 <= proxima_pos[1] < BOARD_SIZE:
                    # Move o agente
                    agente.mover_para(proxima_pos)
                    ambiente.agente_pos = proxima_pos
                    
                    # Movimentação do Wumpus móvel (se ativado)
                    if WUMPUS_MOVEL and agente.passos > 0 and agente.passos % WUMPUS_MOVE_FREQUENCY == 0:
                        pos_antiga = ambiente.wumpus_pos
                        if ambiente.mover_wumpus():
                            agente.wumpus_moveu()
                            agente.adicionar_log(f"Wumpus moveu-se de {pos_antiga} para {ambiente.wumpus_pos}")
                            if ambiente.wumpus_pos == agente.pos:
                                agente.alive = False
                                agente.adicionar_log("Morte: O Wumpus se moveu para a célula do agente!")
                    
                    # Validação de perigos imediatos
                    if agente.pos in ambiente.pocos:
                        agente.alive = False
                        agente.adicionar_log("Morte: Agente caiu em um poço profundo!")
                    elif agente.pos == ambiente.wumpus_pos:
                        agente.alive = False
                        agente.adicionar_log("Morte: Agente foi devorado pelo Wumpus!")
                        
                    # Se o agente sobreviveu ao passo, atualiza suas percepções e base de conhecimento
                    if agente.alive:
                        percepcoes = ambiente.get_percepcoes(agente.pos)
                        agente.agir(percepcoes)
        elif cmd == "VEL_MAIS":
            SIMULATION_SPEED = min(20, SIMULATION_SPEED + 1)
            agente.adicionar_log(f"Velocidade aumentada para {SIMULATION_SPEED} Hz")
        elif cmd == "VEL_MENOS":
            SIMULATION_SPEED = max(1, SIMULATION_SPEED - 1)
            agente.adicionar_log(f"Velocidade reduzida para {SIMULATION_SPEED} Hz")
            
        # Determina se devemos executar um passo (seja por tempo ou clique de passo único manual)
        passo_manual = (cmd == "PASSO")
        tempo_atual = time.time()
        deve_agir = False
        
        # Só age automaticamente se estiver no modo IA e não estiver pausado
        if agente.modo_ia:
            if (not em_pausa and (tempo_atual - ultimo_passo_tempo) >= (1.0 / SIMULATION_SPEED)) or passo_manual:
                deve_agir = True
            
        # 2. Loop de Ação do Agente (apenas se estiver em modo IA)
        if deve_agir and agente.alive and not agente.vitorioso:
            ultimo_passo_tempo = tempo_atual
            
            # --- Fase 1: Movimento do Wumpus ---
            if WUMPUS_MOVEL and agente.passos > 0 and agente.passos % WUMPUS_MOVE_FREQUENCY == 0:
                pos_antiga = ambiente.wumpus_pos
                if ambiente.mover_wumpus():
                    # Notifica a base de conhecimento do agente
                    agente.wumpus_moveu()
                    agente.adicionar_log(f"Wumpus moveu-se de {pos_antiga} para {ambiente.wumpus_pos}")
                    
                    # Se o Wumpus entrar na mesma célula que o agente, o agente morre
                    if ambiente.wumpus_pos == agente.pos:
                        agente.alive = False
                        agente.adicionar_log("Morte: O Wumpus se moveu para a célula do agente!")
            
            # --- Fase 2: Percepção e Ação do Agente ---
            if agente.alive:
                # Percepções baseadas na célula atual
                percepcoes = ambiente.get_percepcoes(agente.pos)
                
                # Executa raciocínio e movimento
                agente.agir(percepcoes)
                
                # Atualiza a posição do agente no ambiente real para renderização
                ambiente.agente_pos = agente.pos
                
                # --- Fase 3: Validação de Consequências no Ambiente ---
                # Queda em Poço
                if agente.pos in ambiente.pocos:
                    agente.alive = False
                    agente.adicionar_log("Morte: Agente caiu em um poço profundo!")
                # Encontro Estático com o Wumpus
                elif agente.pos == ambiente.wumpus_pos:
                    agente.alive = False
                    agente.adicionar_log("Morte: Agente foi devorado pelo Wumpus!")

        # 3. Renderização Gráfica
        interface.desenhar(ambiente, agente, em_pausa, SIMULATION_SPEED)
        
    pygame.quit()

if __name__ == "__main__":
    main()
