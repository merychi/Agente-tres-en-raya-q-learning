# MENU.PY: ARCHIVO DIBUJA LA INTERFAZ DEL MENÚ DEL JUEGO"

import pygame
import os
import sys
from ui.config import *
from ui.assets import *

class MenuPrincipal:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.fuentes = cargar_fuentes()
        self.sonidos = cargar_sonidos()
        self.fondo = cargar_fondo_menu()

        # Boton
        center_x = ANCHO_VENTANA // 2
        start_y = 320  

        self.ultimo_boton_hover = None
        self.btn_jugar = pygame.Rect(0, 0, 390, 100)
        self.btn_jugar.center = (center_x, start_y)

        self.btn_minimax = pygame.Rect(0, 0, 390, 100)
        self.btn_minimax.center = (center_x, start_y + 140)
        
        self.btn_salir = pygame.Rect(0, 0, 390, 100)
        self.btn_salir.center = (center_x, start_y + 280)  

    # --------------------
    # dibujar_boton
    # --------------------
    def dibujar_boton(self, rect, texto, color_base, color_hover):
        mouse_pos = pygame.mouse.get_pos()
        es_hover = rect.collidepoint(mouse_pos)
        
        color_actual = color_hover if es_hover else color_base
        elevacion = 6 if es_hover else 0
        
        # Sombra
        rect_sombra = rect.copy()
        rect_sombra.y += 12
        pygame.draw.rect(self.pantalla, (79, 87, 175), rect_sombra, border_radius=30)
        
        # Botón principal
        rect_visual = rect.copy()
        rect_visual.y -= elevacion 
        pygame.draw.rect(self.pantalla, color_actual, rect_visual, border_radius=30)
        
        # Texto
        txt_surf = self.fuentes['boton_menu'].render(texto, True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=rect_visual.center) 
        self.pantalla.blit(txt_surf, txt_rect)
        
        return es_hover
    
    # --------------------
    # actualizar
    # --------------------
    def actualizar(self):
        # 1. Dibujar Fondo
        if self.fondo:
            self.pantalla.blit(self.fondo, (0, 0))
        else:
            self.pantalla.fill((100, 100, 200)) 

        # 2. Títulos 
        color_titulo = (45, 42, 85) 
        texto_titulo = self.fuentes['titulo_menu'].render("TIC TAC TOE", True, color_titulo)
        self.pantalla.blit(texto_titulo, (40, 90))

        color_sub = (235, 186, 239)
        texto_sub = self.fuentes['subtitulo_menu'].render("Tres en raya", True, color_sub)
        self.pantalla.blit(texto_sub, (45, 185))

        # 3. Créditos
        color_creditos = (200, 200, 255) 
        texto_creditos = "© Julio Romero & Merry-am Blanco"
        surf_creditos = self.fuentes['creditos'].render(texto_creditos, True, color_creditos)
        rect_creditos = surf_creditos.get_rect(bottomleft=(20, ALTO_VENTANA - 20))
        self.pantalla.blit(surf_creditos, rect_creditos)
        
        # 4. Botones
        hover_jugar = self.dibujar_boton(self.btn_jugar, "Jugar vs IA", (44, 44, 84), (32, 32, 61))
        hover_mini  = self.dibujar_boton(self.btn_minimax, "IA vs Minimax", (44, 44, 84), (32, 32, 61))
        hover_salir = self.dibujar_boton(self.btn_salir, "Salir", (44, 44, 84), (32, 32, 61))

        # 5. Gestión de Sonidos Hover
        boton_actual_hover = None 

        if hover_jugar:
            boton_actual_hover = "JUGAR"
        elif hover_mini:
            boton_actual_hover = "MINIMAX"
        elif hover_salir:
            boton_actual_hover = "SALIR"

        if boton_actual_hover != self.ultimo_boton_hover:
            if boton_actual_hover is not None:
                if 'menu_hover' in self.sonidos:
                    self.sonidos['menu_hover'].play()
            
            self.ultimo_boton_hover = boton_actual_hover

        pygame.display.flip()

    # --------------------
    # manejar_eventos
    # --------------------        
    def manejar_eventos(self):
        """Retorna 'JUGAR', 'MINIMAX', 'SALIR' o None"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "SALIR"
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1: 
                    mouse_pos = pygame.mouse.get_pos()
                    
                    accion = None
                    if self.btn_jugar.collidepoint(mouse_pos):
                        accion = "JUGAR"
                    elif self.btn_minimax.collidepoint(mouse_pos):
                        accion = "MINIMAX" 
                    elif self.btn_salir.collidepoint(mouse_pos):
                        accion = "SALIR"
                    
                    if accion:
                        if 'menu_click' in self.sonidos:
                            self.sonidos['menu_click'].play()
                        return accion
        return None