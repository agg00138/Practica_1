import random

from utils.utilidades import Utilidades

class BusquedaLocal:
    def __init__(self, tour_inicial, distancia_inicial, matriz_distancias, params):
        """
        Inicializa el algoritmo Búsqueda Local del Mejor

        :param tour_inicial: Solución del algoritmo Greedy Aleatorio.
        :param distancia_inicial: Distancia de la ruta.
        :param matriz_distancias: Matriz de distancias entre las ciudades.
        :param params: Parámetros del archivo de configuración.
        """
        self.tour_actual = tour_inicial
        self.matriz_distancias = matriz_distancias
        self.distancia_actual = distancia_inicial
        self.params = params

    def resolver(self, semilla, logger=None):
        """
        Resuelve el problema utilizando el algoritmo Búsqueda Local del Mejor con una semilla específica.

        :param semilla: Semilla para el generador aleatorio.
        :return: Lista de ciudades en el orden del tour y la distancia total del tour.
        """
        random.seed(semilla)  # Establece la semilla para la aleatoriedad
        tamanio_entorno = int(self.params['iteraciones'] * self.params['per_tamanio'])
        cont = int(self.params['iteraciones'] * self.params['per_iteraciones'])
        ite = 0

        if logger: logger.registrar_evento(f"Partimos de la solución del Greedy Aleatorio: {self.distancia_actual}")

        for iteracion in range(self.params['iteraciones']):
            # Generar vecinos
            vecinos = Utilidades.generar_vecinos(tamanio_entorno, self.tour_actual, self.matriz_distancias, self.distancia_actual)

            if logger: logger.registrar_evento(f"Iteración: {iteracion}, Tamaño del entorno: {tamanio_entorno}, Vecinos generados: {tamanio_entorno}")

            # Buscar la mejor solución en los vecinos
            mejor_vecino = min(vecinos, key=lambda x: x[1], default=(None, float('inf'), None))
            nuevo_tour, nueva_distancia, movimiento = mejor_vecino

            if logger: logger.registrar_evento(f"Mejor vecino (movimiento): {movimiento}, Distancia: {nueva_distancia}")

            # Si encontramos un mejor vecino
            if nueva_distancia < self.distancia_actual:
                self.tour_actual = nuevo_tour
                self.distancia_actual = nueva_distancia
            else:
                if logger: logger.registrar_evento(f"Ninguno de los vecinos mejora la solución actual.")
                break

            if logger: logger.registrar_evento(f"¡Mejora encontrada! Distancia actual: {nueva_distancia}")

            # Reducimos el tamaño del entorno
            tamanio_entorno, cont, ite = Utilidades.reducir_entorno(tamanio_entorno, cont, iteracion, self.params['per_disminucion'], self.params['per_iteraciones'], ite)
            if tamanio_entorno < (self.params['per_disminucion'] * 100):
                break

        return self.tour_actual, self.distancia_actual