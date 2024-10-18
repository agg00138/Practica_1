import random
import numpy as np

from utils.utilidades import Utilidades

class GreedyAleatorio:
    def __init__(self, matriz_distancias, params):
        """
        Inicializa el algoritmo Greedy Aleatorio.

        :param matriz_distancias: Matriz de distancias entre las ciudades.
        :param params: Parámetros del archivo de configuración.
        """
        self.matriz_distancias = matriz_distancias
        self.k = params['k']

    def resolver(self, semilla, logger=None):
        """
        Resuelve el problema utilizando el algoritmo Greedy Aleatorio con una semilla específica.

        :param semilla: Semilla para el generador aleatorio.
        :return: Lista de ciudades en el orden del tour y la distancia total del tour.
        """
        random.seed(semilla)  # Establece la semilla para la aleatoriedad
        num_ciudades = self.matriz_distancias.shape[0]  # Número de ciudades
        visitadas = np.zeros(num_ciudades, dtype=bool)  # Lista booleana de ciudades visitadas
        tour = []

        # Precomputar las sumas de distancias para todas las ciudades
        suma_distancias = np.sum(self.matriz_distancias, axis=1)

        # Ordenar las ciudades por la suma de sus distancias al resto
        sorted_indices = np.argsort(suma_distancias)

        # Seleccionar la ciudad inicial aleatoriamente entre las K más prometedoras
        ciudades_prometedoras = sorted_indices[:self.k]
        ciudad_actual = random.choice(ciudades_prometedoras)
        tour.append(ciudad_actual)
        visitadas[ciudad_actual] = True
        acumulada = 0

        if logger: logger.registrar_evento(f"Ciudad de Inicio: {ciudad_actual}, Distancia recorrida = {acumulada}")

        for _ in range(num_ciudades - 1):
            # Obtener las ciudades no visitadas
            no_visitadas = np.where(~visitadas)[0]

            # Obtener las K ciudades más prometedoras entre las no visitadas
            k_mejores_ciudades = sorted_indices[np.isin(sorted_indices, no_visitadas)][:self.k]
            if logger: logger.registrar_evento(f"{self.k} ciudades más prometedoras: {k_mejores_ciudades}")

            # Elegir aleatoriamente una ciudad de las K más prometedoras
            siguiente_ciudad = random.choice(k_mejores_ciudades)

            # Sumo la distancia acumulada
            acumulada += self.matriz_distancias[ciudad_actual][siguiente_ciudad]

            # Actualizar el tour y marcar la ciudad como visitada
            tour.append(siguiente_ciudad)
            visitadas[siguiente_ciudad] = True
            ciudad_actual = siguiente_ciudad

            if logger: logger.registrar_evento(f"Viajando a ciudad: {ciudad_actual}, Distancia recorrida = {acumulada}")

        # Calcular la distancia total del tour
        distancia_total = Utilidades.calcular_distancia_total(np.array(tour), self.matriz_distancias)
        if logger: logger.registrar_evento(f"Vuelta a ciudad de Inicio, Distancia recorrida = {distancia_total}")
        return tour, distancia_total