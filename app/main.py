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

# PALETA DE COLORES (Atributos visuales extraídos)
PALETA_COLORES = {
    -1: "#1E1E1E", # Fondo oscuro
    0:  "#FFFFFF", # Celda objetivo (Vaciada/Mostrada)
    1:  "#FF5733", # Pieza 1
    2:  "#33FF57", # Pieza 2
    3:  "#3357FF", # Pieza 3
    4:  "#F3FF33", # Pieza 4
    5: "#9B59B6",  # Pieza 5
    6: "#1ABC9C",  # Pieza 6
    7: "#E67E22",  # Pieza 7
    8: "#F1C40F",  # Pieza 8
    9: "#E74C3C",  # Pieza 9
    10: "#34495E"  # Pieza 10
}

# Inicialización directa del motor
if 'motor_puzzle' not in st.session_state:
    st.session_state.motor_puzzle = RompecabezasMascara()

motor = st.session_state.motor_puzzle

# Botón para ejecutar el algoritmo de backtracking
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

# Control de navegación y renderizado de mapas
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
    st.markdown(
        "Los números del 1 al 10 te indican qué pieza va en cada posición. "