import numpy as np
import copy
from src.configuracion import TABLERO_COLORES, PIEZAS_BASE

class RompecabezasMascara:
    def __init__(self):
        self.tablero_colores = TABLERO_COLORES
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

    def _puede_colocarse(self, pieza, tablero_piezas, color_objetivo, fila, col):
        h, w = pieza.shape
        # 1. Validar límites físicos del tablero
        if fila < 0 or col < 0 or fila + h > 8 or col + w > 8:
            return False
        
        # 2. Validar colisiones celda por celda
        for i in range(h):
            for j in range(w):
                if pieza[i][j] == 1:
                    # Si ya hay otra pieza encima
                    if tablero_piezas[fila + i][col + j] != 0:
                        return False
                    # Si interfiere con el color objetivo expuesto
                    if self.tablero_colores[fila + i][col + j] == color_objetivo:
                        return False
        return True

    def _tiene_huecos_muertos(self, tablero_piezas, color_objetivo):
        """Poda activa: si queda una celda vacía aislada que no es el color objetivo, abortar."""
        for f in range(8):
            for c in range(8):
                if tablero_piezas[f][c] == 0 and self.tablero_colores[f][c] != color_objetivo:
                    vecinos = 0
                    if f > 0 and (tablero_piezas[f-1][c] == 0 or self.tablero_colores[f-1][c] == color_objetivo): vecinos += 1
                    if f < 7 and (tablero_piezas[f+1][c] == 0 or self.tablero_colores[f+1][c] == color_objetivo): vecinos += 1
                    if c > 0 and (tablero_piezas[f][c-1] == 0 or self.tablero_colores[f][c-1] == color_objetivo): vecinos += 1
                    if c < 7 and (tablero_piezas[f][c+1] == 0 or self.tablero_colores[f][c+1] == color_objetivo): vecinos += 1
                    
                    if vecinos == 0:
                        return True
        return False

    def resolver(self, color_objetivo):
        # Matriz de control real e independiente
        tablero_piezas = np.zeros((8, 8), dtype=int)
        soluciones = []
        piezas_usadas = set()
        
        self._backtracking(tablero_piezas, color_objetivo, piezas_usadas, soluciones, [])
        return soluciones

    def _backtracking(self, tablero_piezas, color_objetivo, piezas_usadas, soluciones, historial):
        if len(soluciones) >= 5:
            return

        if len(piezas_usadas) == 10:
            soluciones.append(copy.deepcopy(historial))
            return

        if self._tiene_huecos_muertos(tablero_piezas, color_objetivo):
            return
        
        # Encontrar la primera celda vacía secuencial que deba ser rellenada por madera
        fila_vacia, col_vacia = -1, -1
        encontrado = False
        for f in range(8):
            for c in range(8):
                if tablero_piezas[f][c] == 0 and self.tablero_colores[f][c] != color_objetivo:
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
                            
                            if self._puede_colocarse(p, tablero_piezas, color_objetivo, f_orig, c_orig):
                                # COLOCACIÓN DIRECTA MODIFICANDO LA MATRIZ ORIGINAL
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
                                
                                # Avanzar recursión
                                self._backtracking(tablero_piezas, color_objetivo, piezas_usadas, soluciones, historial)
                                
                                # DESHACER LA JUGADA DIRECTAMENTE
                                piezas_usadas.remove(idx_pieza)
                                historial.pop()
                                for i in range(h):
                                    for j in range(w):
                                        if p[i][j] == 1:
                                            tablero_piezas[f_orig + i][c_orig + j] = 0

    def reconstruir_matriz_solucion(self, solucion):
        matriz_visual = np.ones((8, 8), dtype=int) * -1
        
        # Pintar las piezas fijas calculadas por el árbol
        for paso in solucion:
            p_id = paso['pieza']
            f, c = paso['coords']
            forma = np.array(paso['matriz'])
            h, w = forma.shape
            
            for i in range(h):
                for j in range(w):
                    if forma[i][j] == 1:
                        matriz_visual[f + i][c + j] = p_id
                        
        # Sincronizar celdas vacías con las ventanas correspondientes
        for f in range(8):
            for c in range(8):
                if matriz_visual[f][c] == -1:
                    if self.tablero_colores[f][c] != '0':
                        matriz_visual[f][c] = 0
                        
        return matriz_visual