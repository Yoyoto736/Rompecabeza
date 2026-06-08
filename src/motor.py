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
        # 1. Validar límites del tablero
        if fila < 0 or col < 0 or fila + h > 8 or col + w > 8:
            return False
        
        # 2. Validar colisión con otras piezas ya colocadas
        sub_tablero_piezas = tablero_piezas[fila:fila+h, col:col+w]
        if np.any((pieza == 1) & (sub_tablero_piezas != 0)):
            return False
            
        # 3. CRÍTICO: Validar que la pieza NO tape el color objetivo
        sub_tablero_colores = self.tablero_colores[fila:fila+h, col:col+w]
        if np.any((pieza == 1) & (sub_tablero_colores == color_objetivo)):
            return False
            
        return True

    def _tiene_huecos_muertos(self, tablero_piezas, color_objetivo):
        """Poda si quedan celdas vacías que no sean el color objetivo y estén aisladas."""
        for f in range(8):
            for c in range(8):
                # Una celda está realmente vacía si no tiene pieza Y no es del color objetivo
                if tablero_piezas[f][c] == 0 and self.tablero_colores[f][c] != color_objetivo:
                    vecinos = 0
                    # Contar vecinos que no tengan piezas y no sean el color objetivo
                    if f > 0 and tablero_piezas[f-1][c] == 0: vecinos += 1
                    if f < 7 and tablero_piezas[f+1][c] == 0: vecinos += 1
                    if c > 0 and tablero_piezas[f][c-1] == 0: vecinos += 1
                    if c < 7 and tablero_piezas[f][c+1] == 0: vecinos += 1
                    
                    if vecinos == 0:
                        return True
        return False

    def resolver(self, color_objetivo):
        # Matriz limpia para el control de las piezas de madera
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
        
        # Encontrar la siguiente celda que necesita obligatoriamente ser llenada
        # (No tiene pieza y NO es del color objetivo)
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
                                # Colocar pieza con máscara limpia
                                mask = (p == 1)
                                tablero_piezas[f_orig:f_orig+h, c_orig:c_orig+w][mask] = (idx_pieza + 1)
                                piezas_usadas.add(idx_pieza)
                                
                                historial.append({
                                    'pieza': idx_pieza + 1,
                                    'coords': (f_orig, c_orig),
                                    'matriz': p.tolist()
                                })
                                
                                self._backtracking(tablero_piezas, color_objetivo, piezas_usadas, soluciones, historial)
                                
                                # Deshacer de forma segura
                                piezas_usadas.remove(idx_pieza)
                                historial.pop()
                                tablero_piezas[f_orig:f_orig+h, c_orig:c_orig+w][mask] = 0

    def reconstruir_matriz_solucion(self, solucion):
        # El mapa visual base son todas las piezas colocadas
        matriz_visual = np.ones((8, 8), dtype=int) * -1
        
        for paso in solucion:
            p_id = paso['pieza']
            f, c = paso['coords']
            forma = np.array(paso['matriz'])
            h, w = forma.shape
            
            for i in range(h):
                for j in range(w):
                    if forma[i][j] == 1:
                        matriz_visual[f + i][c + j] = p_id
                        
        # Forzar que donde sea el color objetivo, se muestre la ventana transparente (0)
        # Esto garantiza concordancia perfecta con el tablero real
        for f in range(8):
            for c in range(8):
                if matriz_visual[f][c] == -1:
                    # Si quedó un espacio sin pieza, mapeamos su color real
                    color_real = self.tablero_colores[f][c]
                    if color_real != '0':
                        matriz_visual[f][c] = 0 # Ventana expuesta
                        
        return matriz_visual