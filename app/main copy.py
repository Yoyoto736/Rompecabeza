import sys
import os

# --- BLINDAJE DE RUTAS PARA STREAMLIT CLOUD ---
# Detectamos la ubicación del archivo actual y forzamos la inclusión de la raíz en sys.path
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

# Inyección de estilos CSS globales para unificar la rejilla eliminando márgenes nativos
st.markdown("""
    <style>
    [data-testid="column"] {
        padding: 0px !important;
    }
    .stColumns {
        gap: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧩 Solucionador del Rompecabezas de Máscara")
st.write(
    "Configura el color que deseas dejar expuesto en el tablero y el motor "
    "buscará todas las combinaciones exactas."
)

# 1. Selector de Color Objetivo (Coincide con las llaves del diccionario en el motor)
color_seleccionado = st.selectbox(
    "Selecciona el Color Objetivo:",
    ["Rojo", "Azul", "Amarillo", "Verde", "Morado", "Naranja"]
)

# Diccionario de colores hexadecimales atractivos para cada pieza/bloque
PALETA_COLORES = {
    -1: "#1e1e1e", # Vacío / Fondo oscuro
    0: "#ffffff",  # Ventana objetivo expuesta (Blanco puro para resaltar destellos)
    1: "#ff4b4b",  # Pieza 1 - Rojo
    2: "#4bfa4b",  # Pieza 2 - Verde brillante
    3: "#1f77b4",  # Pieza 3 - Azul marino
    4: "#f1c40f",  # Pieza 4 - Amarillo
    5: "#9b59b6",  # Pieza 5 - Morado
    6: "#1abc9c",  # Pieza 6 - Turquesa
    7: "#e67e22",  # Pieza 7 - Naranja
    8: "#f39c12",  # Pieza 8 - Oro / Ocre
    9: "#e74c3c",  # Pieza 9 - Alizarina / Coral
    10: "#34495e"  # Pieza 10 - Gris Azulado / Madera oscura
}

# Inicialización directa del motor (Sin @st.cache_resource para evitar congelamientos en la RAM)
if 'motor_puzzle' not in st.session_state:
    st.session_state.motor_puzzle = RompecabezasMascara()

motor = st.session_state.motor_puzzle

# Botón para ejecutar el algoritmo de backtracking
if st.button("Buscar Soluciones", type="primary"):
    with st.spinner(f"Analizando combinaciones para despejar el color {color_seleccionado}..."):
        # El motor modificado ahora devuelve las soluciones y la letra interna calculada ('R', 'A', etc.)
        soluciones, letra_obj = motor.resolver(color_seleccionado)
        
        if soluciones:
            st.success(f"¡Búsqueda completada! Se encontraron **{len(soluciones)}** soluciones válidas.")
            
            # Guardar resultados en el estado de la sesión para la navegación
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

# Control de navegación y renderizado de mapas si existen soluciones calculadas
if 'soluciones' in st.session_state and st.session_state.soluciones:
    soluciones = st.session_state.soluciones
    letra_obj = st.session_state.letra_obj
    
    st.write("---")
    
    # Selector numérico para iterar entre las soluciones encontradas (Máximo 5)
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
        "Las celdas marcadas con ✨ corresponden a las ventanas del color expuesto."
    )
    
    # Reconstruir la matriz visual forzando las ventanas del color objetivo basado en la letra real
    matriz_visual = motor.reconstruir_matriz_solucion(soluciones[idx], letra_obj)
    
    # Renderizado de la cuadrícula de 8x8 usando contenedores nativos estilizados con HTML/CSS
    for f in range(8):
        cols = st.columns(8)
        for c in range(8):
            val_celda = matriz_visual[f][c]
            bg_color = PALETA_COLORES.get(val_celda, "#1e1e1e")
            
            # Formatear el contenido de la celda (Texto numérico o Destello indicador)
            if val_celda == 0:
                contenido_html = "<span style='color: #d35400; font-size: 18px