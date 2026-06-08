import streamlit as st
import numpy as np
import sys
import os

# Asegurar que Python encuentre el módulo 'src' desde la carpeta raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.motor import RompecabezasMascara

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Solucionador Rompecabezas de Máscara",
    page_icon="🧩",
    layout="centered"
)

# Paleta de colores en CSS para pintar el tablero e identificar cada pieza
PALETA_COLORES = {
    -1: "#1E1E1E", # Bloqueado / Color Oculto de fondo
    0:  "#FFFFFF", # Celda Objetivo (Vaciada/Mostrada)
    1:  "#FF5733", # Pieza 1 (Naranja rojizo)
    2:  "#33FF57", # Pieza 2 (Verde brillante)
    3:  "#3357FF", # Pieza 3 (Azul eléctrico)
    4:  "#F3FF33", # Pieza 4 (Amarillo)
    5:  "#9B59B6", # Pieza 5 (Morado)
    6:  "#1ABC9C", # Pieza 6 (Turquesa)
    7:  "#E67E22", # Pieza 7 (Anaranjado oscuro)
    8:  "#F1C40F", # Pieza 8 (Oro)
    9:  "#E74C3C", # Pieza 9 (Rojo coral)
    10: "#34495E"  # Pieza 10 (Gris azulado)
}

def renderizar_tablero_html(matriz_visual):
    """Genera una tabla HTML estilizada con CSS para mostrar el tablero."""
    html = '<div style="display: flex; justify-content: center;"><table style="border-collapse: collapse; border: 4px solid #333;">'
    for fila in matriz_visual:
        html += '<tr>'
        for celda in fila:
            color_fondo = PALETA_COLORES.get(celda, "#FFF")
            if celda == 0:
                estilo_celda = f'background-color: {color_fondo}; border: 2px dashed #E74C3C; width: 45px; height: 45px; text-align: center;'
                contenido = "✨"
            else:
                estilo_celda = f'background-color: {color_fondo}; border: 1px solid #444; width: 45px; height: 45px; text-align: center; color: white; font-weight: bold;'
                contenido = str(celda) if celda > 0 else ""
            
            html += f'<td style="{estilo_celda}">{contenido}</td>'
        html += '</tr>'
    html += '</table></div>'
    return html

# --- Interfaz de Usuario ---
st.title("🧩 Solucionador del Rompecabezas de Máscara")
st.write("Configura el color que deseas dejar expuesto en el tablero y el motor buscará todas las combinaciones exactas.")

# Selector de color mapeado según los identificadores de tu tablero real
opciones_colores = {
    "Rojo": "R",
    "Azul": "A",
    "Amarillo": "Y",
    "Verde": "V",
    "Naranja": "N",
    "Morado": "M"
}

color_seleccionado = st.selectbox("Selecciona el Color Objetivo:", list(opciones_colores.keys()))
codigo_color = opciones_colores[color_seleccionado]

# Inicializar el motor de cálculo
def obtener_motor():
    return RompecabezasMascara()

motor = obtener_motor()

if st.button("Buscar Soluciones", type="primary"):
    with st.spinner(f"Analizando combinaciones para despejar el color {color_seleccionado}..."):
        soluciones = motor.resolver(codigo_color)
    
    if len(soluciones) == 0:
        st.error(f"No se encontraron soluciones posibles para dejar expuesto el color {color_seleccionado}. Verifica la disposición de las piezas.")
    else:
        st.success(f"¡Búsqueda completada! Se encontraron **{len(soluciones)}** soluciones válidas.")
        
        # Guardar soluciones en el estado de la sesión para evitar recalcular al cambiar de página
        st.session_state['soluciones_encontradas'] = soluciones

if 'soluciones_encontradas' in st.session_state:
    sols = st.session_state['soluciones_encontradas']
    
    idx_solucion = st.number_input(
        f"Ver solución (1 al {len(sols)}):", 
        min_value=1, 
        max_value=len(sols), 
        value=1, 
        step=1
    )
    
    # Reconstruir la matriz 8x8 de la solución seleccionada
    solucion_actual = sols[idx_solucion - 1]
    matriz_8x8 = motor.reconstruir_matriz_solucion(solucion_actual)
    
    # Renderizar en la pantalla
    st.markdown("### Mapa de Colocación de Piezas")
    st.write("Los números del 1 al 10 te indican qué pieza va en cada posición. Las celdas marcadas con ✨ corresponden a las ventanas del color expuesto.")
    st.markdown(renderizar_tablero_html(matriz_8x8), unsafe_allow_html=True)
    
    # Guía de ensamblado paso a paso
    with st.expander("Ver orden de ensamble paso a paso"):
        for paso in solucion_actual:
            st.write(f"🔹 **Pieza {paso['pieza']}**: Colocar en la esquina superior izquierda de su caja en la coordenada de la cuadrícula: Fila **{paso['coords'][0] + 1}**, Columna **{paso['coords'][1] + 1}**.")