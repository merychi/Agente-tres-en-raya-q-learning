import json
import ast
import os
import webbrowser

# Generar un reporte HTML similar al PDF para que no te rompas la cabeza tratando de organizar el json en el paper
def generar_html_como_en_el_pdf():
    archivo_entrada = "conocimiento_gato.json"
    archivo_salida = "REPORTE_CEREBRO_IA.html"
    
    print(f"Leyendo {archivo_entrada}...")
    
    if not os.path.exists(archivo_entrada):
        print("Error: No se encuentra el archivo de conocimiento.")
        return

    with open(archivo_entrada, "r") as f:
        data = json.load(f)

    # Ordenamos estados para que se vea organizado
    estados_ordenados = sorted(data.keys())

    # --- INICIO DEL HTML (CSS para que se vea bonito) ---
    html = """
    <html>
    <head>
        <title>Cerebro del Agente Q-Learning</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f9; padding: 20px; }
            h1 { color: #333; text-align: center; }
            .resumen { text-align: center; margin-bottom: 20px; color: #666; }
            table { width: 100%; border-collapse: collapse; box-shadow: 0 0 20px rgba(0,0,0,0.1); background-color: white; }
            th, td { padding: 12px 15px; text-align: center; border-bottom: 1px solid #ddd; }
            th { background-color: #009879; color: white; text-transform: uppercase; font-size: 0.85em; position: sticky; top: 0; }
            tr:hover { background-color: #f1f1f1; }
            
            /* Estilo para el mini tablero visual */
            .tablero-visual { 
                font-family: 'Courier New', monospace; 
                font-weight: bold; 
                line-height: 14px; 
                display: inline-block;
                border: 1px solid #ccc;
                padding: 3px;
                background: #eee;
            }
            
            /* Colores para valores */
            .positivo { color: green; font-weight: bold; }
            .negativo { color: red; opacity: 0.7; }
            .mejor-jugada { background-color: #d4edda; border: 2px solid #28a745; }
            .zero { color: #ccc; font-size: 0.8em; }
        </style>
    </head>
    <body>
        <h1>Visualización de la Tabla Q (Q-Table)</h1>
        <p class="resumen">Este reporte muestra el valor aprendido para cada acción en cada estado posible.</p>
        <p class="resumen">Julio Romero  Merry-am Blanco.</p>
        <table>
            <thead>
                <tr>
                    <th>Estado Visual</th>
                    <th>Estado (Tupla)</th>
                    <th>Casilla 0</th>
                    <th>Casilla 1</th>
                    <th>Casilla 2</th>
                    <th>Casilla 3</th>
                    <th>Casilla 4</th>
                    <th>Casilla 5</th>
                    <th>Casilla 6</th>
                    <th>Casilla 7</th>
                    <th>Casilla 8</th>
                </tr>
            </thead>
            <tbody>
    """

    # --- GENERAR FILAS ---
    for estado_str in estados_ordenados:
        acciones = data[estado_str]
        
        # 1. Crear representación visual del tablero (3x3 real con saltos de línea HTML)
        try:
            estado_tupla = ast.literal_eval(estado_str)
            # Reemplazamos espacios con puntos para visibilidad
            v = [c if c != " " else "·" for c in estado_tupla]
            # Formato HTML con <br> para saltos de línea
            visual_html = f"{v[0]} {v[1]} {v[2]}<br>{v[3]} {v[4]} {v[5]}<br>{v[6]} {v[7]} {v[8]}"
        except:
            visual_html = "Error"

        html += "<tr>"
        html += f"<td><div class='tablero-visual'>{visual_html}</div></td>"
        html += f"<td style='font-size: 0.8em; color: #555;'>{estado_str}</td>"
        
        # Encontrar el valor máximo para resaltar la celda
        valores = [acciones.get(str(i), 0.0) for i in range(9)]
        # Si todos son 0, no hay mejor jugada aún
        max_val = max(valores) if any(v != 0 for v in valores) else None

        # 2. Llenar las 9 columnas de acciones
        for val in valores:
            clase_css = ""
            if val > 0: clase_css = "positivo"
            elif val < 0: clase_css = "negativo"
            else: clase_css = "zero"
            
            # Resaltar la mejor jugada con fondo verde
            estilo_extra = ""
            if max_val is not None and val == max_val and val != 0:
                estilo_extra = "class='mejor-jugada'"
                # Añadir un icono de estrella o check si es la mejor
                val_str = f"★ {val:.2f}"
            else:
                val_str = f"{val:.2f}"
            
            # Insertar celda
            html += f"<td {estilo_extra}><span class='{clase_css}'>{val_str}</span></td>"

        html += "</tr>"

    html += """
            </tbody>
        </table>
    </body>
    </html>
    """

    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"Reporte generado: {archivo_salida}")
    # Abrir automáticamente en el navegador
    webbrowser.open('file://' + os.path.realpath(archivo_salida))

if __name__ == "__main__":
    generar_html_como_en_el_pdf()