import time
import os
import datetime
from game.logic import LogicaTresRayas
from game.ai import agente_global, obtener_movimiento_minimax_adaptable

# Generamos un nombre de archivo único con la hora actual
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
ARCHIVO_LOG = f"registro_duelo_{TIMESTAMP}.txt"

def log(mensaje):
    """Guarda el mensaje tanto en consola como en el archivo de texto."""
    print(mensaje)
    with open(ARCHIVO_LOG, "a", encoding="utf-8") as f:
        f.write(mensaje + "\n")

def tablero_a_string(tablero):
    """Convierte el tablero en un string visual para el archivo de texto."""
    s = "\n"
    s += f" {tablero[0]} | {tablero[1]} | {tablero[2]} \n"
    s += "---+---+---\n"
    s += f" {tablero[3]} | {tablero[4]} | {tablero[5]} \n"
    s += "---+---+---\n"
    s += f" {tablero[6]} | {tablero[7]} | {tablero[8]} \n"
    return s

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def ejecutar_duelo():
    # Encabezado del log
    log("="*40)
    log(f"🥊 REGISTRO DE DUELO DE TITANES - {TIMESTAMP}")
    log("="*40)
    log("JUGADOR X: Q-Learning (El Gato Aprendiz)")
    log("JUGADOR O: Minimax (El Dios Calculador)")
    log("-" * 40)

    juego = LogicaTresRayas()
    turno = "X"
    
    # Modo Serio
    agente_global.epsilon = 0.0
    log(f"🧠 Cerebro Q-Learning cargado. Epsilon: {agente_global.epsilon}")
    log(f"📂 El historial se guardará en: {ARCHIVO_LOG}")
    
    time.sleep(2)
    pasos = 1
    
    while not juego.juego_terminado():
        limpiar_pantalla()
        
        # Guardamos el estado actual antes de mover
        estado_visual = tablero_a_string(juego.tablero)
        print(estado_visual) # Solo mostrar en consola para no spammear el log visualmente aun
        
        mensaje_turno = f"\n--- TURNO {pasos}: Juega {turno} ---"
        log(mensaje_turno)
        
        if turno == "X":
            # --- TURNO Q-LEARNING ---
            print(">> El Gato está pensando...")
            time.sleep(1)
            
            movimientos_validos = juego.obtener_movimientos_posibles()
            accion = agente_global.obtener_accion(juego.tablero, movimientos_validos, en_entrenamiento=False)
            
            log(f"🤖 Q-Learning elige casilla: {accion}")
            juego.realizar_movimiento(accion, "X")
            
            # Registramos cómo quedó el tablero tras la jugada
            log(tablero_a_string(juego.tablero))
            turno = "O"
            
        else:
            # --- TURNO MINIMAX ---
            print(">> Minimax está calculando...")
            time.sleep(1)
            
            accion = obtener_movimiento_minimax_adaptable(juego.tablero, "O")
            
            log(f"📐 Minimax elige casilla: {accion}")
            juego.realizar_movimiento(accion, "O")
            
            # Registramos cómo quedó el tablero tras la jugada
            log(tablero_a_string(juego.tablero))
            turno = "X"
            
        pasos += 1

    # --- FINAL DEL JUEGO ---
    limpiar_pantalla()
    print(tablero_a_string(juego.tablero))
    
    ganador = juego.verificar_ganador()
    log("\n" + "="*40)
    log("🏁 FIN DEL DUELO 🏁")
    
    if ganador == "X":
        log("🏆 RESULTADO: ¡VICTORIA DE Q-LEARNING!")
        log("Nota: Esto es casi imposible contra Minimax. ¿Bug o Milagro?")
    elif ganador == "O":
        log("🤖 RESULTADO: VICTORIA DE MINIMAX")
        log("Nota: Q-Learning necesita más entrenamiento.")
    else:
        log("🤝 RESULTADO: EMPATE")
        log("Nota: ¡ÉXITO TOTAL! Q-Learning jugó al nivel óptimo perfecto.")
    
    log("="*40)
    print(f"\n📄 Historial completo guardado en: {ARCHIVO_LOG}")

if __name__ == "__main__":
    ejecutar_duelo()