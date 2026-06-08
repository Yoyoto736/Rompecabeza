import sys
import os

# --- BLINDAJE DE RUTAS PARA STREAMLIT CLOUD ---
dir_actual = os.path.dirname(os.path.abspath(__file__))
dir_raiz = os.path.abspath(os.path.join(dir_actual, '..'))

if dir_raiz not in sys.path:
    sys.path.insert(0, dir_raiz)
if dir_actual not in sys.path:
    sys.path.insert(1, dir_actual)

import streamlit as st
import numpy as np
from src.motor import RompecabezasMascara

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Solucionador de Rompecabezas de Máscara",
    page_icon="🧩",
    layout="centered"
)

# PERSISTENCIA ABSOLUTA: Inicializar variables de estado para evitar que desaparezcan al recargar
if 'soluciones' not in st.session_state:
    st.session_state.soluciones = None
if 'indice_solucion' not in st.session_state:
    st.session_state.indice_solucion = 0

st.title("🧩 Solucionador del Rompecabezas de Máscara")
st.write(
    "Configura el color que deseas dejar expuesto en el tablero y el motor "
    "buscará todas las combinaciones exactas."
)

# Selector de interfaz en Español
color_seleccionado = st.selectbox(
    "Selecciona el Color Objetivo:",
    ["Rojo", "Azul", "Amarillo", "Verde", "Morado", "Naranja"]
)

# Mapeo estricto hacia los caracteres del TABLERO_COLORES del motor
MAPEO_LETRAS = {
    "Rojo": "R",
    "Azul": "A",
    "Amarillo": "Y",
    "Verde": "V",
    "Morado": "M",
    "Naranja": "N"
}

# Paleta de colores viva con la estética de botones en relieve original
PALETA_COLORES = {
    -1: "#2e2e2e", # Vacío / Fondo neutro
    0: "#ffffff",  # Ventana libre expuesta (Fondo blanco limpio para resaltar destellos)
    1: "#ff4d4d",  # Pieza 1 - Rojo Coral
    2: "#2ecc71",  # Pieza 2 - Verde Esmeralda
    3: "#3498db",  # Pieza 3 - Azul Brillante
    4: "#f1c40f",  # Pieza 4 - Amarillo Girasol
    5: "#9b59b6",  # Pieza 5 - Amatista / Morado
    6: "#1abc9c",  # Pieza 6 - Turquesa / Menta
    7: "#e67e22",  # Pieza 7 - Naranja Otoño
    8: "#f39c12",  # Pieza 8 - Ámbar / Oro
    9: "#e74c3c",  # Pieza 9 - Bermellón
    10: "#34495e"  # Pieza 10 - Asfalto / Azul Grisáceo
}

# Inicialización del motor
if 'motor_puzzle' not in st.session_state:
    st.session_state.motor_puzzle = RompecabezasMascara()

motor = st.session_state.motor_puzzle

# Botón para ejecutar el algoritmo
if st.button("Buscar Soluciones", type="primary"):
    with st.spinner(f"Analizando combinaciones para despejar el color {color_seleccionado}..."):
        letra_interna = MAPEO_LETRAS[color_seleccionado]
        
        # Ejecutar la búsqueda con tu motor exacto
        lista_soluciones = motor.resolver(letra_interna)
        
        if lista_soluciones and len(lista_soluciones) > 0:
            st.success(f"¡Búsqueda completada! Se encontraron **{len(lista_soluciones)}** soluciones válidas.")
            st.session_state.soluciones = lista_soluciones
            st.session_state.indice_solucion = 0
        else:
            st.error(
                f"No se encontraron soluciones analíticas que logren despejar completamente "
                f"las 4 ventanas del color {color_seleccionado} con las piezas dadas."
            )
            st.session_state.soluciones = None

# Renderizado gráfico estable (Evaluamos si la persistencia tiene datos válidos)
if st.session_state.soluciones is not None and len(st.session_state.soluciones) > 0:
    soluciones = st.session_state.soluciones
    max_soluciones = len(soluciones)
    
    st.write("---")
    
    idx = st.number_input(
        f"Ver solución (1 al {max_soluciones}):",
        min_value=1,
        max_value=max_soluciones,
        value=st.session_state.indice_solucion + 1,
        step=1
    ) - 1
    
    st.session_state.indice_solucion = idx
    
    st.subheader("Mapa de Colocación de Piezas")
    st.markdown(
        "Los números del 1 al 10 te indican qué pieza va en cada posición. "
        "Las celdas marcadas con ✨ corresponden a las ventanas del color expuesto."
    )
    
    # Reconstrucción de la matriz usando la solución seleccionada
    matriz_visual = motor.reconstruir_matriz_solucion(soluciones[idx])
    
    # Forzar la reducción de espacios entre columnas nativas de Streamlit
    st.markdown(
        """
        <style>
        [data-testid="column"] {
            padding: 0px 1px !important;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    # Renderizado de la cuadrícula
    for f in range(8):
        cols = st.columns(8)
        for c in range(8):
            val_celda = matriz_visual[f][c]
            bg_color = PALETA_COLORES.get(val_celda, "#2e2e2e")
            
            if val_celda == 0:
                contenido_html = "<span style='color: #e67e22; font-size: 20px; font-weight: bold;'>✨</span>"
                border_style = "border: 2px dashed #e74c3c;" # Borde discontinuo de la ventana
            else:
                contenido_html = f"<span style='color: white; font-size: 16px; font-weight: bold;'>{val_celda}</span>"
                border_style = "border: 1px solid rgba(0,0,0,0.15);"
            
            # CSS Ajustado: 'margin: 3px 1px' y efectos 3D restaurados para el look de mosaico físico real
            cols[c].markdown(
                f"""
                <div style="
                    background-color: {bg_color};
                    height: 54px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    {border_style}
                    border-radius: 6px;
                    margin: 3px 1px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), inset 0 -3px 0 rgba(0,0,0,0.2);
                ">
                    {contenido_html}
                </div>
                """,
                unsafe_allow_html=True
            )
            
    with st.expander("Ver orden de ensamble paso a paso"):
        for paso_num, paso in enumerate(soluciones[idx], 1):
            st.write(
                f"**Paso {paso_num}:** Colocar la **Pieza {paso['pieza']}** "
                f"en la coordenada de origen del tablero (Fila: {paso['coords'][0] + 1}, Columna: {paso['coords'][1] + 1})."
            )