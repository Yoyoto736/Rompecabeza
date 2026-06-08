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

st.title("🧩 Solucionador de Rompecabezas (Edición Madera)")
st.write(
    "Configura el color que deseas dejar expuesto en el fondo y el motor "
    "buscará el encaje perfecto de los bloques."
)

color_seleccionado = st.selectbox(
    "Selecciona el Color Objetivo:",
    ["Rojo", "Azul", "Amarillo", "Verde", "Morado", "Naranja"]
)

# --- NUEVA LÓGICA DE LIMPIEZA ---
if 'color_previo' not in st.session_state:
    st.session_state.color_previo = color_seleccionado

if st.session_state.color_previo != color_seleccionado:
    st.session_state.color_previo = color_seleccionado
    if 'soluciones' in st.session_state:
        del st.session_state.soluciones
# --------------------------------

# Paleta de tonos de madera
PALETA_MADERA = {
    -1: "#1e1e1e", # Fondo vacío
    1: "#E9C46A",  # Amarillo pino
    2: "#F4A261",  # Naranja claro
    3: "#E76F51",  # Terracota
    4: "#D4A373",  # Roble clásico
    5: "#C68642",  # Madera quemada
    6: "#A0522D",  # Siena
    7: "#8B4513",  # Marrón madera
    8: "#D2691E",  # Chocolate
    9: "#BC8F8F",  # Rosado madera
    10: "#A52A2A"  # Marrón rojizo
}

# Colores profundos tipo "fieltro" para el fondo de las ventanas
MAPA_COLOR_FONDO = {
    "Rojo": "#8b0000",
    "Azul": "#0b3b60",
    "Amarillo": "#b8860b",
    "Verde": "#006400",
    "Morado": "#4b0082",
    "Naranja": "#cc5500"
}
color_ventana = MAPA_COLOR_FONDO.get(color_seleccionado, "#333333")

if 'motor_puzzle' not in st.session_state:
    st.session_state.motor_puzzle = RompecabezasMascara()

motor = st.session_state.motor_puzzle

if st.button("Buscar Soluciones", type="primary"):
    with st.spinner(f"Encajando bloques para el fondo {color_seleccionado}..."):
        soluciones, letra_obj = motor.resolver(color_seleccionado)
        
        if soluciones:
            st.success(f"¡Búsqueda completada! Se encontraron **{len(soluciones)}** soluciones válidas.")
            st.session_state.soluciones = soluciones
            st.session_state.letra_obj = letra_obj
            st.session_state.indice_solucion = 0
        else:
            st.error(
                f"No se encontraron soluciones analíticas que logren despejar completamente "
                f"las 4 ventanas del color {color_seleccionado}."
            )
            if 'soluciones' in st.session_state:
                del st.session_state.soluciones

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
    
    st.subheader("Tablero Físico")
    
    matriz_visual = motor.reconstruir_matriz_solucion(soluciones[idx], letra_obj)
    
    # --- CONSTRUCCIÓN DEL GRID HTML/CSS SIN SANGRÍAS ---
    # Contenedor principal
    html_grid = f"""<div style="display: grid; grid-template-columns: repeat(8, 1fr); gap: 2px; background-color: #1a1a1a; padding: 8px; border: 12px solid #c99b68; border-radius: 4px; box-shadow: 5px 5px 15px rgba(0,0,0,0.6), inset 3px 3px 8px rgba(0,0,0,0.8); width: 100%; max-width: 500px; margin: 0 auto;">"""
    
    # Generación de las 64 celdas
    for f in range(8):
        for c in range(8):
            val_celda = matriz_