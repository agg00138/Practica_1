import numpy as np
from scipy.spatial.distance import cdist

class TSP:
    def __init__(self, archivo):
        self.archivo = archivo
        self.matriz_distancias = None
        self.tour_inicial = None

    def procesar(self):
        with open(self.archivo, 'r') as f:
            lineas = f.readlines()

        # Inicializa las coordenadas
        coordenadas = []

        # Procesa el archivo para construir la matriz de distancias y el tour inicial
        for i, linea in enumerate(lineas):
            if 'DIMENSION' in linea:
                dimension = int(linea.split(':')[1].strip())
                self.matriz_distancias = np.zeros((dimension, dimension))
            elif 'NODE_COORD_SECTION' in linea:
                for j in range(dimension):
                    ciudad, x, y = map(float, lineas[i + 1 + j].split())
                    coordenadas.append((x, y))  # Guarda las coordenadas
            elif 'EOF' in linea:
                break

        # Calcula la matriz de distancias usando scipy
        self.matriz_distancias = cdist(coordenadas, coordenadas, metric='euclidean')

        # Inicializa el tour inicial (puedes ajustar esto según tu lógica)
        self.tour_inicial = list(range(dimension))
        return self.matriz_distancias, self.tour_inicial
