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

# Inyección de estilos CSS globales para compactar la rejilla
st.markdown("""
    <style>
    [data-testid="column"] {
        padding: 0px !important;
    }
    .stColumns {
        gap: 0px !important;
        background-color: #222; /* Color de fondo de la bandeja/tablero base */
        padding: 4px;
        border-radius: 8px;
        box-shadow: inset 0px 0px 10px rgba(0,0,0,0.8);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧩 Solucionador del Rompecabezas de Máscara")
st.write(
    "Configura el color que deseas dejar expuesto en el tablero y el motor "
    "buscará todas las combinaciones exactas."
)

# 1. Selector de Color Objetivo
color_seleccionado = st.selectbox(
    "Selecciona el Color Objetivo:",
    ["Rojo", "Azul", "Amarillo", "Verde", "Morado", "Naranja"]
)

# Diccionario de colores hexadecimales para las piezas de plástico
PALETA_COLORES = {
    -1: "#1e1e1e",
    1: "#e74c3c",  # Pieza 1 - Rojo
    2: "#2ecc71",  # Pieza 2 - Verde
    3: "#3498db",  # Pieza 3 - Azul
    4: "#f1c40f",  # Pieza 4 - Amarillo
    5: "#9b59b6",  # Pieza 5 - Morado
    6: "#1abc9c",  # Pieza 6 - Turquesa
    7: "#e67e22",  # Pieza 7 - Naranja
    8: "#f39c12",  # Pieza 8 - Ocre
    9: "#c0392b",  # Pieza 9 - Rojo oscuro
    10: "#34495e"  # Pieza 10 - Gris oscuro
}

# Mapeo del color real que se verá a través de las ventanas
MAPA_COLOR_FONDO = {
    "Rojo": "#ff4b4b",
    "Azul": "#1f77b4",
    "Amarillo": "#f1c40f",
    "Verde": "#4bfa4b",
    "Morado": "#9b59b6",
    "Naranja": "#e67e22"
}
color_ventana = MAPA_COLOR_FONDO.get(color_seleccionado, "#ffffff")

if 'motor_puzzle' not in st.session_state:
    st.session_state.motor_puzzle = RompecabezasMascara()

motor = st.session_state.motor_puzzle

# Botón para ejecutar
if st.button("Buscar Soluciones", type="primary"):
    with st.spinner(f"Analizando combinaciones para despejar el color {color_seleccionado}..."):
        soluciones, letra_obj = motor.resolver(color_seleccionado)
        
        if soluciones:
            st.success(f"¡Búsqueda completada! Se encontraron **{len(soluciones)}** soluciones válidas.")
            st.session_state.soluciones = soluciones
            st.session_state.letra_obj = letra_obj
            st.session_state.indice_solucion = 0
        else:
            st.error(
                f"No se encontraron soluciones analíticas que logren despejar completamente "
                f"las 4 ventanas del color {color_seleccionado} con las piezas dadas."
            )
            if 'soluciones' in st.session_state:
                del st.session_state.soluciones

# Renderizado del mapa
if 'soluciones' in st.session_state and st.session_state.soluciones:
    soluciones = st.session_state.soluciones
    letra_obj = st.session_state.letra_obj
    
    st.write("---")
    
    idx = st.number_input(
        f"Ver solución (1 al {len(soluciones)}):",
        min_value=1,
        max_value=len(soluciones),
        value=st.session_state.indice_solucion + 1,
        step=1
    ) - 1
    
    st.session_state.indice_solucion = idx
    
    st.subheader("Mapa de Colocación de Piezas")
    
    matriz_visual = motor.reconstruir_matriz_solucion(soluciones[idx], letra_obj)
    
    # Contenedor principal de la rejilla
    for f in range(8):
        cols = st.columns(8)
        for c in range(8):
            val_celda = matriz_visual[f][c]
            
            if val_celda == 0:
                # Estilo para "Agujero" profundo mostrando el cartón de color de fondo
                estilo_html = f"""
                <div style="
                    background-color: {color_ventana};
                    height: 52px;
                    border-radius: 50%; /* Lo hace redondo como un agujero real */
                    margin: 2px;
                    box-shadow: inset 4px 4px 8px rgba(0,0,0,0.8), inset -2px -2px 4px rgba(0,0,0,0.5);
                    border: 1px solid rgba(0,0,0,0.6);
                ">
                </div>
                """
            else:
                # Estilo para "Pieza de Plástico" en relieve
                bg_color = PALETA_COLORES.get(val_celda, "#1e1e1e")
                estilo_html = f"""
                <div style="
                    background-color: {bg_color};
                    height: 52px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 4px;
                    margin: 1px;
                    /* Múltiples sombras para simular luz arriba a la izquierda y sombra abajo a la derecha */
                    box-shadow: 
                        inset 2px 2px 4px rgba(255, 255, 255, 0.4), 
                        inset -3px -3px 6px rgba(0, 0, 0, 0.3),
                        2px 2px 3px rgba(0, 0, 0, 0.5);
                    border: 1px solid rgba(0,0,0,0.3);
                ">
                    <b style='
                        color: rgba(255,255,255,0.9); 
                        font-size: 16px; 
                        text-shadow: 1px 1px 2px rgba(0,0,0,0.6);
                        font-family: sans-serif;
                    '>
                        {val_celda}
                    </b>
                </div>
                """
            
            cols[c].markdown(estilo_html, unsafe_allow_html=True)
            
    with st.expander("Ver orden de ensamble paso a paso"):
        for paso_num, paso in enumerate(soluciones[idx], 1):
            st.write(
                f"**Paso {paso_num}:** Colocar la **Pieza {paso['pieza']}** "
                f"en la coordenada de origen (Fila: {paso['coords'][0] + 1}, Columna: {paso['coords'][1] + 1})."
            )