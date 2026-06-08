import numpy as np
import copy
from src.configuracion import TABLERO_COLORES, PIEZAS_BASE

class RompecabezasMascara:
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

    def _puede_colocarse(self, pieza, tablero, fila, col):
        h, w = pieza.shape
        if fila + h > 8 or col + w > 8:
            return False
        sub_tablero = tablero[fila:fila+h, col:col+w]
        if np.any((pieza == 1) & (sub_tablero != 0)):
            return False
        return True

    def resolver(self, color_objetivo):
        tablero_inicial = np.zeros((8, 8), dtype=int)
        tablero_inicial[self.tablero_colores == color_objetivo] = -1
        
        soluciones = []
        piezas_usadas = set()
        
        self._backtracking(tablero_inicial, piezas_usadas, soluciones, [])
        return soluciones

    def _backtracking(self, tablero, piezas_usadas, soluciones, historial):
        if len(piezas_usadas) == 10:
            soluciones.append(copy.deepcopy(historial))
            return
        
        encontrado = False
        for f in range(8):
            for c in range(8):
                if tablero[f][c] == 0:
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
                            
                            if self._puede_colocarse(p, tablero, f_orig, c_orig):
                                tablero[f_orig:f_orig+h, c_orig:c_orig+w] += (p * (idx_pieza + 1))
                                piezas_usadas.add(idx_pieza)
                                
                                historial.append({
                                    'pieza': idx_pieza + 1,
                                    'coords': (f_orig, c_orig),
                                    'matriz': p.tolist()
                                })
                                
                                self._backtracking(tablero, piezas_usadas, soluciones, historial)
                                
                                piezas_usadas.remove(idx_pieza)
                                historial.pop()
                                tablero[f_orig:f_orig+h, c_orig:c_orig+w] -= (p * (idx_pieza + 1))

    def reconstruir_matriz_solucion(self, solucion):
        matriz_visual = np.zeros((8, 8), dtype=int)
        for paso in solucion:
            p_id = paso['pieza']
            f, c = paso['coords']
            forma = np.array(paso['matriz'])
            h, w = forma.shape
            matriz_visual[f:f+h, c:c+w] += (forma * p_id)
        return matriz_visual