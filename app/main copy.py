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

st.set_page_config(page_title="Editor Visual 3D", layout="centered")

st.title("🎨 Editor de Mosaico 3D")
st.write("Configura y visualiza el tablero con el acabado de relieve físico.")

# Diccionario de colores (Los mismos de tu app base)
PALETA_COLORES = {
    -1: "#1e1e1e", 0: "#ffffff", 1: "#ff4b4b", 2: "#4bfa4b", 
    3: "#1f77b4", 4: "#f1c40f", 5: "#9b59b6", 6: "#1abc9c", 
    7: "#e67e22", 8: "#f39c12", 9: "#e74c3c", 10: "#34495e"
}

# Estilos CSS para el look "Relieve Físico"
st.markdown("""
    <style>
    .celda-3d {
        height: 54px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        margin: 3px 1px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), inset 0 -3px 0 rgba(0,0,0,0.2);
        font-weight: bold;
        color: white;
    }
    [data-testid="column"] { padding: 0px 1px !important; }
    </style>
""", unsafe_allow_html=True)

# Lógica del motor (Copia de tu script base)
if 'motor_puzzle' not in st.session_state:
    st.session_state.motor_puzzle = RompecabezasMascara()
motor = st.session_state.motor_puzzle

# (Aquí puedes mantener tu lógica de botones y navegación tal cual estaba)
# Ejemplo de renderizado de una fila de ejemplo con el nuevo estilo:
st.subheader("Mapa de Colocación (Estilo 3D)")
for f in range(8):
    cols = st.columns(8)
    for c in range(8):
        # Ejemplo: bg_color obtenido de tu paleta
        bg_color = PALETA_COLORES.get(1, "#3498db")
        
        cols[c].markdown(
            f"""
            <div class="celda-3d" style="background-color: {bg_color};">
                {c+1}
            </div>
            """, 
            unsafe_allow_html=True
        )