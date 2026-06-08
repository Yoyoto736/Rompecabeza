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
        if fila < 0 or col < 0 or fila + h > 8 or col + w > 8:
            return False
        
        sub_tablero = tablero[fila:fila+h, col:col+w]
        if np.any((pieza == 1) & (sub_tablero != 0)):
            return False
        return True

    def _tiene_huecos_muertos(self, tablero):
        """Poda de ramas muertas: Detecta si hay celdas vacías completamente aisladas."""
        # Si una celda vacía (0) no tiene vecinos vacíos, es imposible llenarla (ya que la pieza más pequeña tiene 2 celdas)
        for f in range(8):
            for c in range(8):
                if tablero[f][c] == 0:
                    # Contar vecinos válidos/vacíos
                    vecinos = 0
                    if f > 0 and tablero[f-1][c] == 0: vecinos += 1
                    if f < 7 and tablero[f+1][c] == 0: vecinos += 1
                    if c > 0 and tablero[f][c-1] == 0: vecinos += 1
                    if c < 7 and tablero[f][c+1] == 0: vecinos += 1
                    
                    if vecinos == 0:
                        return True # Encontró un callejón sin salida, abortar rama
        return False

    def resolver(self, color_objetivo):
        tablero_inicial = np.zeros((8, 8), dtype=int)
        tablero_inicial[self.tablero_colores == color_objetivo] = -1
        
        soluciones = []
        piezas_usadas = set()
        
        self._backtracking(tablero_inicial, piezas_usadas, soluciones, [])
        return soluciones

    def _backtracking(self, tablero, piezas_usadas, soluciones, historial):
        # Límite de seguridad para pruebas iniciales: si encuentra 5 soluciones, frena para no congelar la UI
        if len(soluciones) >= 5:
            return

        if len(piezas_usadas) == 10:
            soluciones.append(copy.deepcopy(historial))
            return

        # Poda activa por callejones sin salida geométricos
        if self._tiene_huecos_muertos(tablero):
            return
        
        # Encontrar la primera celda vacía de arriba a abajo, izquierda a derecha
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
                                # Colocar pieza
                                mask = (p == 1)
                                tablero[f_orig:f_orig+h, c_orig:c_orig+w][mask] = (idx_pieza + 1)
                                piezas_usadas.add(idx_pieza)
                                
                                historial.append({
                                    'pieza': idx_pieza + 1,
                                    'coords': (f_orig, c_orig),
                                    'matriz': p.tolist()
                                })
                                
                                # Siguiente nivel
                                self._backtracking(tablero, piezas_usadas, soluciones, historial)
                                
                                # Deshacer
                                piezas_usadas.remove(idx_pieza)
                                historial.pop()
                                tablero[f_orig:f_orig+h, c_orig:c_orig+w][mask] = 0

    def reconstruir_matriz_solucion(self, solucion):
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
                        
        # Sincronizar las ventanas transparentes (0)
        for f in range(8):
            for c in range(8):
                if matriz_visual[f][c] == -1 and self.tablero_colores[f][c] != '0':
                    matriz_visual[f][c] = 0
                    
        return matriz_visual