import random
import os
import json
import ast
import time
from copy import deepcopy
from game.logic import LogicaTresRayas

# =============================================================================
# SECCIÓN 1: AGENTE Q-LEARNING (El Gato Aprendiz)
# =============================================================================

ARCHIVO_Q_TABLE = "conocimiento_gato.json"

class QAgent:
    def __init__(self, alpha=0.5, gamma=0.9, epsilon=1.0):
        """
        Inicializa al agente (El Gato) De Julio y Merry la nueva era de la AI.
        """
        self.q_table = {} 
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9995 
        
        self.cargar_conocimiento()

    def obtener_estado(self, tablero):
        return tuple(tablero)

    def obtener_accion(self, tablero, movimientos_posibles, en_entrenamiento=True):
        estado = self.obtener_estado(tablero)

        # 1. Fase de EXPLORACIÓN
        if en_entrenamiento and random.uniform(0, 1) < self.epsilon:
            return random.choice(movimientos_posibles)

        # 2. Fase de EXPLOTACIÓN
        if estado not in self.q_table:
            self.q_table[estado] = {mov: 0.0 for mov in movimientos_posibles}

        valores_movimientos = self.q_table[estado]
        valores_validos = {m: valores_movimientos.get(m, 0.0) for m in movimientos_posibles}
        
        max_valor = max(valores_validos.values())
        mejores_movimientos = [m for m, v in valores_validos.items() if v == max_valor]
        
        return random.choice(mejores_movimientos)

    def aprender(self, estado_actual, accion, recompensa, estado_siguiente, movimientos_siguientes, termino_juego):
        estado_t = self.obtener_estado(estado_actual)
        estado_t1 = self.obtener_estado(estado_siguiente)

        if estado_t not in self.q_table:
            self.q_table[estado_t] = {accion: 0.0}
        if estado_t1 not in self.q_table:
            self.q_table[estado_t1] = {m: 0.0 for m in movimientos_siguientes}

        q_actual = self.q_table[estado_t].get(accion, 0.0)

        if termino_juego:
            max_q_futuro = 0.0
        else:
            vals_siguientes = [self.q_table[estado_t1].get(m, 0.0) for m in movimientos_siguientes]
            max_q_futuro = max(vals_siguientes) if vals_siguientes else 0.0

        nuevo_q = q_actual + self.alpha * (recompensa + (self.gamma * max_q_futuro) - q_actual)
        self.q_table[estado_t][accion] = nuevo_q

    def reducir_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def guardar_conocimiento(self):
        try:
            data_para_json = {str(k): v for k, v in self.q_table.items()}
            with open(ARCHIVO_Q_TABLE, "w") as f:
                json.dump(data_para_json, f, indent=4)
            print(f" Cerebro guardado en {ARCHIVO_Q_TABLE} ({len(self.q_table)} estados).")
        except Exception as e:
            print(f" Error guardando cerebro: {e}")

    def cargar_conocimiento(self):
        if os.path.exists(ARCHIVO_Q_TABLE):
            try:
                with open(ARCHIVO_Q_TABLE, "r") as f:
                    data_cargada = json.load(f)
                
                self.q_table = {}
                for k_str, v in data_cargada.items():
                    key_tupla = ast.literal_eval(k_str)
                    valores_int = {int(m): valor for m, valor in v.items()}
                    self.q_table[key_tupla] = valores_int
                    
                print(f"Cerebro cargado: {len(self.q_table)} estados aprendidos.")
                # Si va a jugar contra Minimax, ¡que juegue serio! (Epsilon 0)
                self.epsilon = 0.0 
            except Exception as e:
                print(f" Error cargando cerebro JSON: {e}")
                self.q_table = {}
        else:
            print("⚠️ No hay cerebro guardado. Se inicia desde cero.")

# Instancia global del Q-Agent
agente_global = QAgent()


# =============================================================================
# SECCIÓN 2: ALGORITMO MINIMAX (El Dios Calculador)
# =============================================================================

CACHE_MINIMAX = {}

def limpiar_cache():
    """Limpia la memoria para reiniciar partida"""
    CACHE_MINIMAX.clear()

def minimax(tablero, profundidad, es_turno_max):
    """
    Algoritmo Minimax recursivo con Memoización.
    """
    estado_clave = (tuple(tablero), es_turno_max)
    if estado_clave in CACHE_MINIMAX:
        return CACHE_MINIMAX[estado_clave]

    juego = LogicaTresRayas()
    juego.tablero = list(tablero)
    ganador = juego.verificar_ganador()

    # Evaluación estática
    # 10 - prof para preferir victorias rápidas
    # prof - 10 para preferir derrotas lentas
    if ganador == "X":
        return 10 - profundidad
    elif ganador == "O":
        return profundidad - 10
    elif not juego.existe_espacio_libre():
        return 0

    movimientos = juego.obtener_movimientos_posibles()
    
    if es_turno_max: # Turno de X (Maximizar)
        mejor_puntaje = -float('inf')
        for mov in movimientos:
            juego.tablero[mov] = "X"
            # El siguiente turno será de MIN (False)
            puntaje = minimax(juego.tablero, profundidad + 1, False)
            juego.tablero[mov] = " " # Backtracking
            mejor_puntaje = max(mejor_puntaje, puntaje)
    else: # Turno de O (Minimizar)
        mejor_puntaje = float('inf')
        for mov in movimientos:
            juego.tablero[mov] = "O"
            # El siguiente turno será de MAX (True)
            puntaje = minimax(juego.tablero, profundidad + 1, True)
            juego.tablero[mov] = " " # Backtracking
            mejor_puntaje = min(mejor_puntaje, puntaje)
    
    CACHE_MINIMAX[estado_clave] = mejor_puntaje
    return mejor_puntaje

def obtener_movimiento_minimax_adaptable(tablero, ficha_jugador):
    """
    Decide el mejor movimiento para Minimax, sea jugando como 'X' o como 'O'.
    Esta función es necesaria para el enfrentamiento IA vs IA.
    """
    mejor_movimiento = None
    
    # Si Minimax es X, busca MAXIMIZAR (-inf inicio)
    # Si Minimax es O, busca MINIMIZAR (+inf inicio)
    es_maximizador = (ficha_jugador == "X")
    
    if es_maximizador:
        mejor_puntaje = -float('inf')
    else:
        mejor_puntaje = float('inf')

    for movimiento in range(9):
        if tablero[movimiento] == " ":
            tablero_copia = list(tablero)
            tablero_copia[movimiento] = ficha_jugador
            
            # Llamamos a minimax para ver el valor del futuro.
            # Si acabo de jugar (como X u O), el siguiente turno es del oponente.
            # Por tanto, pasamos "not es_maximizador" para el turno siguiente.
            puntaje = minimax(tablero_copia, 0, not es_maximizador)
            
            if es_maximizador:
                if puntaje > mejor_puntaje:
                    mejor_puntaje = puntaje
                    mejor_movimiento = movimiento
            else:
                if puntaje < mejor_puntaje:
                    mejor_puntaje = puntaje
                    mejor_movimiento = movimiento
                    
    return mejor_movimiento

# =============================================================================
# SECCIÓN 3: VISUALIZACIÓN DE ÁRBOL (Legacy Minimax)
# =============================================================================

def generar_arbol_visual(tablero_final):
    """
    Reconstruye la historia y genera datos para dibujar el árbol.
    """
    secuencia_reconstruida = []
    tablero_temp = [" "]*9
    copia_final = list(tablero_final)
    total_fichas = sum(1 for c in copia_final if c != " ")
    
    # 1. Ingeniería Inversa
    for _ in range(total_fichas):
        turno_actual = "X" if len(secuencia_reconstruida) % 2 == 0 else "O"
        movimiento_encontrado = None
        for i in range(9):
            if copia_final[i] == turno_actual and tablero_temp[i] == " ":
                movimiento_encontrado = i
                break
        if movimiento_encontrado is not None:
            secuencia_reconstruida.append((movimiento_encontrado, turno_actual))
            tablero_temp[movimiento_encontrado] = turno_actual
        else:
            break

    # 2. Construcción Recursiva
    def construir_nivel_recursivo(tablero_actual, paso_idx):
        if paso_idx >= len(secuencia_reconstruida):
            return []

        mov_real, turno_quien_jugo = secuencia_reconstruida[paso_idx]
        nodos_hermanos = []
        movimientos_posibles = [i for i, c in enumerate(tablero_actual) if c == " "]
        nodo_camino_real = None

        for mov in movimientos_posibles:
            t_futuro = list(tablero_actual)
            t_futuro[mov] = turno_quien_jugo
            
            es_turno_max_siguiente = (turno_quien_jugo == "O")
            puntaje = minimax(t_futuro, 0, es_turno_max_siguiente)
            es_el_elegido = (mov == mov_real)
            
            nodo = {
                "movimiento": mov,
                "tablero": t_futuro,
                "puntaje": puntaje,
                "es_camino_ganador": es_el_elegido,
                "sub_ramas": [] 
            }
            nodos_hermanos.append(nodo)
            if es_el_elegido:
                nodo_camino_real = nodo
        
        if nodo_camino_real:
            nodo_camino_real["sub_ramas"] = construir_nivel_recursivo(
                nodo_camino_real["tablero"], paso_idx + 1
            )
            
        return nodos_hermanos

    return construir_nivel_recursivo([" "]*9, 0)