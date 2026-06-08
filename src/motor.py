import numpy as np
import copy
from src.configuracion import TABLERO_COLORES, PIEZAS_BASE

class RompecabezasMascara:
    def __init__(self):
        # Aseguramos que la matriz de configuración se cargue limpia
        self.tablero_colores = np.array(TABLERO_COLORES)
        self.piezas_formas = self._inicializar_piezas()

    def _inicializar_piezas(self):
        piezas_transformadas = []
        for p in PIEZAS_BASE:
            orientaciones_unicas = self._generar_todas_orientaciones(p)
            piezas_transformadas.append(orientaciones_unicas)
        return piezas_transformadas

    def _generar_todas_orientaciones(self, pieza):
        transformaciones = []
        for i in range(4):
            rotada = np.rot90(pieza, i)
            transformaciones.append(rotada)
            transformaciones.append(np.fliplr(rotada))
            transformaciones.append(np.flipud(rotada))
            
        unicas = []
        for t in transformaciones:
            if not any(np.array_equal(t, u) for u in unicas):
                unicas.append(t)
        return unicas

    def _puede_colocarse(self, pieza, tablero_piezas, letra_objetivo, fila, col):
        h, w = pieza.shape
        # 1. Validar límites físicos del tablero
        if fila < 0 or col < 0 or fila + h > 8 or col + w > 8:
            return False
        
        # 2. Validar colisiones y restricciones de color celda por celda
        for i in range(h):
            for j in range(w):
                if pieza[i][j] == 1:
                    # Si ya hay otra pieza física encima
                    if tablero_piezas[fila + i][col + j] != 0:
                        return False
                    # Restricción sagrada: Si la casilla es del color objetivo, DEBE quedar vacía
                    if self.tablero_colores[fila + i][col + j] == letra_objetivo:
                        return False
        return True

    def _tiene_huecos_muertos(self, tablero_piezas, letra_objetivo):
        """Poda matemática: si queda un espacio vacío aislado que no es ventana, abortar."""
        for f in range(8):
            for c in range(8):
                if tablero_piezas[f][c] == 0 and self.tablero_colores[f][c] != letra_objetivo:
                    vecinos = 0
                    if f > 0 and (tablero_piezas[f-1][c] == 0 or self.tablero_colores[f-1][c] == letra_objetivo): vecinos += 1
                    if f < 7 and (tablero_piezas[f+1][c] == 0 or self.tablero_colores[f+1][c] == letra_objetivo): vecinos += 1
                    if c > 0 and (tablero_piezas[f][c-1] == 0 or self.tablero_colores[f][c-1] == letra_objetivo): vecinos += 1
                    if c < 7 and (tablero_piezas[f][c+1] == 0 or self.tablero_colores[f][c+1] == letra_objetivo): vecinos += 1
                    
                    if vecinos == 0:
                        return True
        return False

    def resolver(self, nombre_color):
        # Mapeo del string de Streamlit a las iniciales reales de tu matriz corregida
        mapeo_letras = {
            'Rojo': 'R',
            'Azul': 'A',
            'Amarillo': 'Y',
            'Verde': 'V',
            'Morado': 'M',
            'Naranja': 'N' 
        }
        letra_objetivo = mapeo_letras.get(nombre_color, 'A')
        
        tablero_piezas = np.zeros((8, 8), dtype=int)
        soluciones = []
        piezas_usadas = set()
        
        self._backtracking(tablero_piezas, letra_objetivo, piezas_usadas, soluciones, [])
        return soluciones, letra_objetivo

    def _backtracking(self, tablero_piezas, letra_objetivo, piezas_usadas, soluciones, historial):
        if len(soluciones) >= 5:
            return

        if len(piezas_usadas) == 10:
            soluciones.append(copy.deepcopy(historial))
            return

        if self._tiene_huecos_muertos(tablero_piezas, letra_objetivo):
            return
        
        # Buscar la primera celda vacía secuencial que no deba quedar expuesta
        fila_vacia, col_vacia = -1, -1
        encontrado = False
        for f in range(8):
            for c in range(8):
                if tablero_piezas[f][c] == 0 and self.tablero_colores[f][c] != letra_objetivo:
                    fila_vacia, col_vacia = f, c
                    encontrado = True
                    break
            if encontrado:
                break
        
        if not encontrado:
            return

        for idx_pieza in range(10):
            if idx_pieza in piezas_usadas:
                continue
                
            for p in self.piezas_formas[idx_pieza]:
                h, w = p.shape
                for pr_f in range(h):
                    for pr_c in range(w):
                        if p[pr_f][pr_c] == 1:
                            f_orig = fila_vacia - pr_f
                            c_orig = col_vacia - pr_c
                            
                            if self._puede_colocarse(p, tablero_piezas, letra_objetivo, f_orig, c_orig):
                                # Colocación real directa
                                for i in range(h):
                                    for j in range(w):
                                        if p[i][j] == 1:
                                            tablero_piezas[f_orig + i][c_orig + j] = (idx_pieza + 1)
                                
                                piezas_usadas.add(idx_pieza)
                                historial.append({
                                    'pieza': idx_pieza + 1,
                                    'coords': (f_orig, c_orig),
                                    'matriz': p.tolist()
                                })
                                
                                self._backtracking(tablero_piezas, letra_objetivo, piezas_usadas, soluciones, historial)
                                
                                # Deshacer jugada
                                piezas_usadas.remove(idx_pieza)
                                historial.pop()
                                for i in range(h):
                                    for j in range(w):
                                        if p[i][j] == 1:
                                            tablero_piezas[f_orig + i][c_orig + j] = 0

    def reconstruir_matriz_solucion(self, solucion, letra_objetivo):
        # Inicializar todo el tablero con fondo -1 (vacio)
        matriz_visual = np.ones((8, 8), dtype=int) * -1
        
        # Pintar las 10 piezas calculadas por el árbol
        for paso in solucion:
            p_id = paso['pieza']
            f, c = paso['coords']
            forma = np.array(paso['matriz'])
            h, w = forma.shape
            
            for i in range(h):
                for j in range(w):
                    if forma[i][j] == 1:
                        matriz_visual[f + i][c + j] = p_id
                        
        # Sincronizar de forma estricta las 4 ventanas del color objetivo
        for f in range(8):
            for c in range(8):
                if self.tablero_colores[f][c] == letra_objetivo:
                    matriz_visual[f][c] = 0  # 0 indica ventana con destellos (✨) en el frontend
                        
        return matriz_visual