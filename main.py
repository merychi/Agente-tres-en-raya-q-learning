# MAIN.PY: Ejecutador del juego"
import time
import sys
import pygame 
import os

from game.logic import LogicaTresRayas
from game.ai import agente_global 
from ui.interface import *
from ui.menu import MenuPrincipal
from ui.assets import *
from ui.help import * 

def main():
    pygame.init()
    pygame.mixer.init()
    establecer_icono_ventana() 
    iniciar_musica_fondo()
    
    pantalla_principal = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption("Tres en Raya - Machine Learning")

    # --- BUCLE MAESTRO ---
    while True:
        # ---  MENÚ ---
        menu = MenuPrincipal(pantalla_principal)
        en_menu = True
        clock = pygame.time.Clock()

        modo_juego = "HUMANO" # Valor por defecto

        while en_menu:
            clock.tick(60)
            menu.actualizar()
            accion = menu.manejar_eventos()

            if accion == "SALIR":
                pygame.quit(); sys.exit()
            
            elif accion == "JUGAR":
                modo_juego = "HUMANO" 
                en_menu = False
            
            elif accion == "MINIMAX":  
                modo_juego = "MINIMAX"
                en_menu = False 

        # --- INICIO DEL JUEGO ---
        juego = LogicaTresRayas()
        ui = InterfazGrafica()
        
        turno = "X"
        mensaje_estado = "Juega la IA (X)"
        juego_corriendo = True
        juego_terminado_flag = False
        
        while juego_corriendo:
            clock.tick(60)

            # 1. DIBUJAR
            if modo_juego == "HUMANO":
                ui.dibujar_interfaz_humano(juego.tablero, mensaje_estado, juego.combo_ganador)
            else:
                ui.dibujar_interfaz_humano(juego.tablero, mensaje_estado, juego.combo_ganador)

            # 2. EVENTOS
            evento = ui.obtener_evento_usuario()

            if evento == 'SALIR':
                pygame.quit(); sys.exit()

            if evento == 'MENU':
                juego_corriendo = False 
                break 
            
            if evento == 'REINICIAR':
                juego.reiniciar()
                turno = "X" 
                mensaje_estado = "IA Pensando"
                juego_terminado_flag = False
                continue

            # Si el juego terminó, solo permitimos dibujar y reiniciar
            if juego_terminado_flag: 
                continue
            
            # --- C. VERIFICAR SI TERMINÓ ---
            if juego.juego_terminado():
                ganador = juego.verificar_ganador()
                if ganador == "X":
                    mensaje_estado = "¡Perdiste! Ganó la IA."
                elif ganador == "O":
                    mensaje_estado = "¡Ganaste! Increíble."
                else:
                    mensaje_estado = "¡Empate!"

                if ganador and 'win' in ui.sonidos:
                    ui.sonidos['win'].play()
                        
                juego_terminado_flag = True
                continue

            # TURNOS
            if turno == "X":
                if modo_juego == "HUMANO":
                    ui.dibujar_interfaz_humano(juego.tablero, "IA Pensando...", juego.combo_ganador)
                pygame.display.flip()
                
                time.sleep(0.5) 

                posibles = juego.obtener_movimientos_posibles()
                
                accion_ia = agente_global.obtener_accion(juego.tablero, posibles, en_entrenamiento=False)
                
                if accion_ia is not None:
                    juego.realizar_movimiento(accion_ia, "X")
                    turno = "O"
                    mensaje_estado = "Tu turno"
                else:
                    pass 

            else:
                # --- HUMANO ---
                if isinstance(evento, int): 
                    movimiento = evento
                    
                    if juego.es_movimiento_valido(movimiento):
                        juego.realizar_movimiento(movimiento, "O")
                        turno = "X" 
                        if 'colocar' in ui.sonidos: ui.sonidos['colocar'].play()
                    else:
                        if 'error' in ui.sonidos: ui.sonidos['error'].play()

if __name__ == "__main__":
    main()