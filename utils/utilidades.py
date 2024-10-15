import numpy as np
import random

class Utilidades:
    @staticmethod
    def generar_semillas(dni_alumno, cantidad, offset=0):
        """
        Genera una lista de semillas pseudoaleatorias basadas en el DNI del alumno.

        :param dni_alumno: Número del DNI del alumno.
        :param cantidad: Cantidad de semillas que se desean generar.
        :param offset: Número que indica el desplazamiento para la semilla.
        :return: Lista de semillas generadas.
        """
        random.seed(dni_alumno + offset)
        return [random.randint(1, 100000) for _ in range(cantidad)]

    @staticmethod
    def calcular_distancia_total(tour, matriz_distancias):
        """
        Calcula la distancia total del tour.

        :param tour: Lista de ciudades en el orden de la ruta.
        :param matriz_distancias: Matriz de distancias entre las ciudades.
        :return: Distancia total del tour.
        """
        distancia = np.sum(matriz_distancias[tour[:-1], tour[1:]])  # Distancia entre ciudades consecutivas
        distancia += matriz_distancias[tour[-1], tour[0]]  # Vuelta a la ciudad inicial
        return distancia

    @staticmethod
    def generar_vecino(tour_actual, matriz_distancias, distancia_actual):
        """
        Genera un nuevo vecino aplicando el operador 2-opt.

        :param tour_actual: Lista de ciudades en el orden de la ruta.
        :param matriz_distancias: Matriz de distancias entre las ciudades.
        :param distancia_actual: Distancia de la ruta.
        :return: Nuevo vecino, nueva distancia, i, j.
        """
        n = len(tour_actual)
        i, j = sorted(random.sample(range(1, n - 1), 2))  # Seleccionar dos índices aleatorios

        # Crear una copia del tour y hacer el intercambio de posiciones
        nuevo_vecino = tour_actual[:]
        nuevo_vecino[i], nuevo_vecino[j] = tour_actual[j], tour_actual[i]

        # Calcular nueva distancia
        desaparecen, nuevos = Utilidades.factorizacion(tour_actual, matriz_distancias, i, j)
        nueva_distancia = distancia_actual - (desaparecen) + (nuevos)

        # Comprobación de la solución (igual que con factorización)
        # nueva_distancia = Utilidades.calcular_distancia_total(nuevo_vecino, matriz_distancias)

        return nuevo_vecino, nueva_distancia, i, j

    @staticmethod
    def generar_vecinos(tamanio_entorno, tour_actual, matriz_distancias, distancia_actual):
        """
        Genera un conjunto de vecinos utilizando el operador 2-opt.

        :param tamanio_entorno: Tamaño del entorno para la generación de vecinos.
        :param tour_actual: Lista de ciudades en el orden de la ruta.
        :param matriz_distancias: Matriz de distancias entre las ciudades.
        :param distancia_actual: Distancia de la ruta.
        :return: Lista de vecinos generados con sus respectivas distancias.
        """
        vecinos = []

        for _ in range(tamanio_entorno):
            nuevo_vecino, nueva_distancia, i, j = Utilidades.generar_vecino(tour_actual, matriz_distancias, distancia_actual)
            vecinos.append((nuevo_vecino, nueva_distancia, (i, j)))

        return vecinos

    @staticmethod
    def reducir_entorno(tamanio_entorno, cont, iteracion, per_disminucion, per_iteraciones):
        """
        Reduce el tamaño del entorno cada un porcentaje de iteraciones un tanto por ciento

        :param tamanio_entorno: Tamaño del entorno para la generación de vecinos.
        :param iteracion: Iteración actual.
        :param cont: Contador para el cálculo del tamaño.
        :param per_disminucion: Porcentaje de disminución del entorno.
        :param per_iteraciones: Porcentaje de iteraciones a partir del cual se reduce el entorno.
        :return: tamanio_entorno, cont
        """
        if iteracion == (cont + int(tamanio_entorno * per_iteraciones) ):
            tamanio_entorno = max(1, int(tamanio_entorno * (1 - per_disminucion) ) )
            cont = iteracion

        return tamanio_entorno, cont

    @staticmethod
    def factorizacion(tour, matriz_distancias, i, j):
        """
        Realiza el cálculo de los arcos del nuevo tour.

        :param tour: Lista de ciudades en el orden de la ruta.
        :param matriz_distancias: Matriz de distancias entre las ciudades.
        :param i: Índice de la ciudad i
        :param j: Índice de la ciudad j
        :return: distancia_desaparecen, distancia_nuevos
        """
        # Determinamos los índices de los arcos originales
        n = len(tour)

        # Manejar el caso cuando las ciudades son consecutivas
        if abs(i - j) == 1 or (i == 0 and j == n - 1) or (i == n - 1 and j == 0):
            desaparecen = matriz_distancias[tour[i - 1], tour[i]] + matriz_distancias[tour[j], tour[(j + 1) % n]]
            nuevos = matriz_distancias[tour[i - 1], tour[j]] + matriz_distancias[tour[i], tour[(j + 1) % n]]
        else:
            desaparecen = (
                    matriz_distancias[tour[i - 1], tour[i]] + matriz_distancias[tour[i], tour[(i + 1) % n]] +
                    matriz_distancias[tour[j - 1], tour[j]] + matriz_distancias[tour[j], tour[(j + 1) % n]]
            )
            nuevos = (
                    matriz_distancias[tour[i - 1], tour[j]] + matriz_distancias[tour[j], tour[(i + 1) % n]] +
                    matriz_distancias[tour[j - 1], tour[i]] + matriz_distancias[tour[i], tour[(j + 1) % n]]
            )

        return desaparecen, nuevos