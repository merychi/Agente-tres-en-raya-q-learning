import random
import time
from game.logic import LogicaTresRayas
from game.ai import agente_global

# =============================================================================
#  MÓDULO DE ENTRENAMIENTO (EL GIMNASIO)
# =============================================================================
#  Función Principal:
#  [cite_start]Actúa como el "Entorno" (Environment) descrito en la teoría[cite: 9].
#  Su responsabilidad es simular miles de partidas (Episodios) a alta velocidad
#  para proveer al Agente de:
#  1. Estado (S): La situación del tablero.
#  2. Recompensa (r): Feedback positivo o negativo según el resultado.
# =============================================================================

def jugar_episodio_entrenamiento(jugar_vs_si_mismo=False):
    """
    Simula UN Episodio completo (una partida de principio a fin).
    [cite_start]Ref PDF 'Agente de ML' (Pág. 11): "Episodios (Partidas jugadas)". [cite: 131]
    
    Retorna: El resultado ('X', 'O', 'Empate')
    """
    juego = LogicaTresRayas()
    turno = "X" # El agente siempre será X en este entrenamiento
    
    # --- MEMORIA DE CORTO PLAZO PARA RECOMPENSA DIFERIDA ---
    # Ref PDF 'Q-Learning' (Pág. 3): "El agente debe aprender que un costo inmediato 
    # [cite_start]puede generar una mejor recompensa a largo plazo"[cite: 29].
    # Guardamos el estado anterior para juzgarlo DESPUÉS de que el oponente juegue.
    estado_previo_agente = None
    accion_previa_agente = None
    
    while True:
        # ---------------------------------------------------
        # TURNO DEL AGENTE (X)
        # ---------------------------------------------------
        if turno == "X":
            movimientos_validos = juego.obtener_movimientos_posibles()
            
            # [cite_start]1. Observar Estado (S) [cite: 8]
            estado_actual = list(juego.tablero)
            
            # [cite_start]2. Elegir Acción (A) [cite: 11]
            # Aquí ocurre la Exploración vs Explotación interna del agente.
            accion = agente_global.obtener_accion(estado_actual, movimientos_validos, en_entrenamiento=True)
            
            # 3. Ejecutar Acción en el Entorno
            juego.realizar_movimiento(accion, "X")
            
            ganador = juego.verificar_ganador()
            
            # --- EVALUACIÓN INMEDIATA ---
            if ganador == "X":
                # [cite_start]Recompensa Directa: Ganar [cite: 112]
                # El PDF sugiere +1, nosotros usamos +10 para acelerar la convergencia.
                recompensa = 10
                agente_global.aprender(estado_actual, accion, recompensa, juego.tablero, [], True)
                return "X"
            elif not juego.existe_espacio_libre():
                # [cite_start]Recompensa por Empate [cite: 114]
                # Premiamos el empate (+5) para fomentar la defensa sólida.
                recompensa = 5 
                agente_global.aprender(estado_actual, accion, recompensa, juego.tablero, [], True)
                return "Empate"
            
            # Si el juego no termina, NO aprendemos todavía.
            # Esperamos a ver si esta jugada fue un error que el oponente aprovechará.
            estado_previo_agente = estado_actual
            accion_previa_agente = accion
            
            turno = "O"

        # ---------------------------------------------------
        # TURNO DEL OPONENTE (O) - (El Ambiente responde)
        # ---------------------------------------------------
        else:
            movimientos_validos = juego.obtener_movimientos_posibles()
            
            # El rival puede ser Random (Ruido) o el propio Agente (Self-Play)
            if jugar_vs_si_mismo:
                accion_rival = agente_global.obtener_accion(juego.tablero, movimientos_validos, en_entrenamiento=True)
            else:
                accion_rival = random.choice(movimientos_validos)
            
            juego.realizar_movimiento(accion_rival, "O")
            
            ganador = juego.verificar_ganador()
            movimientos_futuros = juego.obtener_movimientos_posibles() 
            
            # --- FASE DE APRENDIZAJE RETROACTIVO (DELAYED REWARD) ---
            # Aquí evaluamos la jugada que hizo el Agente en el turno anterior basedado en la respuesta del rival.
            
            if ganador == "O":
                # EL RIVAL GANÓ -> La jugada anterior del Agente fue MALA (no bloqueó).
                # [cite_start]Castigo[cite: 113]. PDF sugiere -1, usamos -10.
                if estado_previo_agente is not None:
                    castigo = -10
                    agente_global.aprender(estado_previo_agente, accion_previa_agente, castigo, juego.tablero, [], True)
                return "O"
            
            elif not juego.existe_espacio_libre():
                # EMPATE -> La jugada anterior fue BUENA (sobrevivió).
                if estado_previo_agente is not None:
                    agente_global.aprender(estado_previo_agente, accion_previa_agente, 5, juego.tablero, [], True)
                return "Empate"
            
            else:
                # EL JUEGO SIGUE -> Recompensa Neutra/Transicional.
                # [cite_start]Ref PDF (Pág. 10): "La promesa de ganar en el futuro"[cite: 123, 176].
                # Actualizamos el valor Q usando el maxQ del estado futuro resultante.
                if estado_previo_agente is not None:
                    agente_global.aprender(estado_previo_agente, accion_previa_agente, 0, juego.tablero, movimientos_futuros, False)
            
            turno = "X"

def ejecutar_entrenamiento(n_episodios=10000):
    """
    Ejecuta el ciclo de vida del aprendizaje.
    [cite_start]Ref PDF 'Q-Learning' (Pág. 11): "Curva de Aprendizaje - Convergencia"[cite: 125].
    """
    print(f"\n INICIANDO ENTRENAMIENTO ({n_episodios} Partidas)...")
    print("El agente está aprendiendo. Por favor espere.")
    
    tiempo_inicio = time.time()
    
    victorias_x = 0
    victorias_o = 0
    empates = 0
    
    for i in range(1, n_episodios + 1):
        # Cada 500 episodios, activamos Self-Play para mejorar defensa
        vs_self = (i % 500 == 0)
        
        resultado = jugar_episodio_entrenamiento(jugar_vs_si_mismo=vs_self)
        
        # Recolección de estadísticas para la Curva de Aprendizaje
        if resultado == "X": victorias_x += 1
        elif resultado == "O": victorias_o += 1
        else: empates += 1
        
        # DECAY DE EPSILON:
        # [cite_start]Ref PDF (Pág. 8): "Al principio exploramos mucho (azar), con el tiempo explotamos más"[cite: 94].
        agente_global.reducir_epsilon()
        
        if i % (n_episodios // 10) == 0:
            porcentaje = (i / n_episodios) * 100
            print(f"Progreso: {porcentaje:.0f}% | Epsilon: {agente_global.epsilon:.4f} | Gana X: {victorias_x} - Gana O: {victorias_o}")

    tiempo_fin = time.time()
    duracion = tiempo_fin - tiempo_inicio
    
    print("\n" + "="*40)
    print(" ENTRENAMIENTO FINALIZADO")
    print(f"Tiempo total: {duracion:.2f} segundos")
    print(f"Victorias IA (X): {victorias_x}")
    print(f"Derrotas IA (O):  {victorias_o}")
    print(f"Empates:          {empates}")
    print("="*40 + "\n")
    
    # Persistencia del conocimiento aprendido
    agente_global.guardar_conocimiento()

if __name__ == "__main__":
    ejecutar_entrenamiento(10000)