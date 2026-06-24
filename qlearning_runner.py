from ambiente import Ambiente
from agente import Agente


def treinar_q_learning_em_lote(
    q_learning,
    n,
    num_pocos,
    densidade_pocos,
    wumpus_movel,
    frequencia_wumpus,
    episodios_por_lote=100,
    max_passos_por_episodio=160,
):
    """
    Executa episodios sem renderizacao para acelerar o aprendizado.
    """
    q_learning.iniciar_lote()
    for _ in range(episodios_por_lote):
        executar_episodio_q_learning(
            q_learning,
            n,
            num_pocos,
            densidade_pocos,
            wumpus_movel,
            frequencia_wumpus,
            max_passos_por_episodio,
        )
    q_learning.finalizar_lote(episodios_por_lote)


def executar_episodio_q_learning(
    q_learning,
    n,
    num_pocos,
    densidade_pocos,
    wumpus_movel,
    frequencia_wumpus,
    max_passos_por_episodio,
):
    ambiente = Ambiente(
        n,
        num_pocos=num_pocos,
        wumpus_movel=wumpus_movel,
        densidade_pocos=densidade_pocos,
    )
    agente = Agente(n, wumpus_movel=wumpus_movel)
    agente.configurar_modo_jogo("agente")
    agente.configurar_tipo_agente("q_learning")
    agente.configurar_modo_q_learning("treino_rapido")
    agente.q_learning = q_learning
    agente.logs_ativos = False

    for _ in range(max_passos_por_episodio):
        if wumpus_movel and agente.passos > 0 and agente.passos % frequencia_wumpus == 0:
            if ambiente.mover_wumpus():
                agente.wumpus_moveu()
                if ambiente.wumpus_pos == agente.pos:
                    agente.alive = False
                    agente.q_learning.registrar_passo(-250.0)
                    agente.q_learning.finalizar_episodio("morte", aplicar_decay=True)
                    return

        transicao = agente.passo_q_learning(
            ambiente,
            treinamento=True,
            registrar_log=False,
            finalizar_episodio=True,
        )
        if transicao is None or transicao["terminou"]:
            return

    q_learning.registrar_passo(-35.0)
    q_learning.finalizar_episodio("limite_passos", aplicar_decay=True)
