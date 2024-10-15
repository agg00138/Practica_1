import random
import numpy as np
from collections import deque  # Para la lista circular
from utils.utilidades import Utilidades

class AlgoritmoTabu:
    def __init__(self, tour_inicial, distancia_inicial, matriz_distancias, params):
        """
        Inicializa el Algoritmo Tabú

        :param tour_inicial: Solución del algoritmo Greedy Aleatorio.
        :param distancia_inicial: Distancia de la ruta.
        :param matriz_distancias: Matriz de distancias entre las ciudades.
        :param params: Parámetros del archivo de configuración.
        """
        self.tour_actual = tour_inicial
        self.matriz_distancias = matriz_distancias
        self.distancia_actual = distancia_inicial
        self.params = params

        # Inicializar la matriz (tamaño: número de ciudades x número de ciudades)
        self.matriz_mcp_mlp = np.zeros((len(tour_inicial), len(tour_inicial)))  # Matriz para MCP y MLP
        self.mcp_lista_circular = deque(maxlen=params['tamano_lista_circular'])  # Lista circular para la MCP
        # self.mcp_lista_circular = []  # Lista circular sin tamaño fijo
        self.mcp_mapa = {}  # Diccionario para el acceso rápido a la MCP

        # Inicializa las variables para el seguimiento de las mejores soluciones
        self.mejor_momento_actual = tour_inicial.copy()  # Copia del tour inicial
        self.mejor_global = tour_inicial.copy()  # Copia del tour inicial
        self.distancia_mejor_momento_actual = self.distancia_actual
        self.distancia_mejor_global = self.distancia_actual

    def resolver(self, semilla):
        """
        Resuelve el problema utilizando el Algoritmo Tabú con una semilla específica.

        :param semilla: Semilla para el generador aleatorio.
        :return: Lista de ciudades en el orden del tour y la distancia total del tour.
        """
        random.seed(semilla)  # Establece la semilla para la aleatoriedad
        tamanio_entorno = int(self.params['iteraciones'] * self.params['per_tamanio'])
        cont = 0
        estancamiento_contador = 0

        for iteracion in range(self.params['iteraciones']):
            # Generar vecinos
            vecinos_filtrados = []
            for _ in range(tamanio_entorno):
                vecino, nueva_distancia, i, j = Utilidades.generar_vecino(self.tour_actual, self.matriz_distancias, self.distancia_actual)
                if self.movimiento_no_tabu(vecino, (i, j)):
                    vecinos_filtrados.append((vecino, nueva_distancia, (i, j)))

            # Buscar el mejor vecino
            mejor_vecino = min(vecinos_filtrados, key=lambda x: x[1], default=(None, float('inf'), None))
            nuevo_tour, nueva_distancia, movimiento = mejor_vecino

            #print(f"Iteracion: {iteracion}, Distancia vecino generado: {nueva_distancia}, Tamaño Entorno: {tamanio_entorno}")

            # Actualizar memoria y manejar estancamiento
            if nueva_distancia < self.distancia_actual:
                self.tour_actual = nuevo_tour
                self.distancia_actual = nueva_distancia

                # Actualizar mejor momento actual
                self.mejor_momento_actual = nuevo_tour.copy()  # Copiar el nuevo tour
                self.distancia_mejor_momento_actual = nueva_distancia

                # Actualizar mejor global
                if nueva_distancia < self.distancia_mejor_global:
                    self.mejor_global = nuevo_tour.copy()  # Copiar el nuevo tour
                    self.distancia_mejor_global = nueva_distancia

                self.actualizar_mcp(nuevo_tour, movimiento)
                self.actualizar_mlp(nuevo_tour)
                estancamiento_contador = 0  # Reiniciar el contador de estancamiento
            else:
                estancamiento_contador += 1

            # Verificar si hay estancamiento
            if estancamiento_contador >= self.params['per_estancamiento'] * self.params['iteraciones']:
                print("Estancamiento detectado, generando nueva solución...")
                self.generar_nueva_solucion()
                estancamiento_contador = 0  # Reiniciar el contador de estancamiento

            # Reducir el tamaño del entorno cada 10% de iteraciones
            tamanio_entorno, cont = Utilidades.reducir_entorno(tamanio_entorno, cont, iteracion, self.params['per_disminucion'], self.params['per_iteraciones'])
            if tamanio_entorno < (self.params['per_disminucion'] * 100):
                break

        return self.mejor_global, self.distancia_mejor_global

    def movimiento_no_tabu(self, vecino, movimiento):
        """

        :param vecino:
        :param movimiento:
        :return:
        """
        # Verificar si el movimiento está en la MCP (movimiento prohibido)
        i, j = movimiento
        ciudad_1, ciudad_2 = vecino[i], vecino[j]

        casilla_1 = min(i, ciudad_1), max(i, ciudad_1)
        casilla_2 = min(j, ciudad_2), max(j, ciudad_2)

        # Verificar si el movimiento está en la MCP (movimiento prohibido)
        return self.matriz_mcp_mlp[casilla_1] <= 0 and self.matriz_mcp_mlp[casilla_2] <= 0  # Comprobación de ambos movimientos

    def actualizar_mcp(self, nuevo_tour, movimiento):
        """
        Actualiza la MCP (Memoria de Control de Prohibición) mediante la lista circular y el mapa.
        """
        # Reducir la tenencia de todos los movimientos prohibidos en el diccionario
        movimientos_a_eliminar = []
        for movimiento, tenencia in self.mcp_mapa.items():
            self.mcp_mapa[movimiento] -= 1
            if self.mcp_mapa[movimiento] <= 0:
                movimientos_a_eliminar.append(movimiento)  # Marcar para eliminar

        # Eliminar movimientos cuya tenencia ha caducado
        for movimiento in movimientos_a_eliminar:
            del self.mcp_mapa[movimiento]
            # Eliminar de la lista circular si está presente
            if movimiento in self.mcp_lista_circular:
                self.mcp_lista_circular.remove(movimiento)

        # Actualizar la tenencia tabú
        i, j = movimiento
        ciudad_1, ciudad_2 = nuevo_tour[i], nuevo_tour[j]

        casilla_1 = min(i, ciudad_1), max(i, ciudad_1)
        casilla_2 = min(j, ciudad_2), max(j, ciudad_2)

        # Establecer el valor de tenencia tabú en la matriz (diagonal superior)
        self.matriz_mcp_mlp[casilla_1] = self.params['tenencia']  # Asignar la tenencia tabú al movimiento
        self.matriz_mcp_mlp[casilla_2] = self.params['tenencia']
        self.mcp_lista_circular.append(casilla_1)  # Añadir el movimiento a la lista circular
        self.mcp_lista_circular.append(casilla_2)

    def actualizar_mlp(self, nuevo_tour):
        """
        Actualiza la MLP (Memoria a Largo Plazo) incrementando los arcos visitados en el tour actual.
        """
        for k in range(len(nuevo_tour)):
            origen = nuevo_tour[k]
            destino = nuevo_tour[(k + 1) % len(nuevo_tour)]  # Asegura que el destino sea cíclico
            # Incrementar el conteo del arco en la diagonal inferior
            if origen > destino:
                self.matriz_mcp_mlp[origen, destino] += 1  # Incrementar en la diagonal inferior
            else:
                self.matriz_mcp_mlp[destino, origen] += 1  # Incrementar en la diagonal inferior

    def generar_nueva_solucion(self):
        # Generar nueva solución mediante oscilación estratégica
        if random.random() < self.params['oscilacion_estrategica']:
            print("Ejecutando diversificación.")
            self.tour_actual = self.estrategia_diversificacion()
        else:
            print("Ejecutando intensificación.")
            self.tour_actual = self.estrategia_intensificacion()

        # Reiniciar solo la MCP
        self.mcp_lista_circular.clear()  # Limpiar la lista circular
        self.mcp_mapa.clear()  # Limpiar el diccionario de movimientos prohibidos

        # Reiniciar la distancia
        self.distancia_actual = Utilidades.calcular_distancia_total(self.tour_actual, self.matriz_distancias)

    def estrategia_diversificacion(self):
        # Implementar lógica para generar una solución nueva mediante diversificación
        ciudades = list(range(len(self.matriz_distancias)))
        random.shuffle(ciudades)  # Barajar las ciudades para crear un nuevo tour
        return ciudades

    def estrategia_intensificacion(self):
        # Implementar lógica para generar una solución nueva mediante intensificación
        mejores_vecinos = Utilidades.generar_vecinos(10, self.mejor_momento_actual, self.matriz_distancias, self.distancia_mejor_momento_actual)
        mejor_vecino = min(mejores_vecinos, key=lambda x: x[1])
        return mejor_vecino[0]