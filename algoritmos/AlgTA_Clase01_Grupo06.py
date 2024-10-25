import random
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

        # La lista circular mantendrá los últimos 20 movimientos
        self.mcp_lista_tabu = deque(maxlen=params['tamano_lista_circular'])  # Lista circular para la MCP
        self.mcp_tenencias = {}  # Diccionario para las tenencias de cada movimiento
        self.mlp = {}  # Diccionario para la MLP

        # Inicializa las variables para el seguimiento de las mejores soluciones
        self.mejor_momento_actual = tour_inicial.copy()  # Copia del tour inicial
        self.mejor_global = tour_inicial.copy()  # Copia del tour inicial
        self.distancia_mejor_momento_actual = self.distancia_actual
        self.distancia_mejor_global = self.distancia_actual

    def resolver(self, semilla, logger=None):
        """
        Resuelve el problema utilizando el Algoritmo Tabú con una semilla específica.

        :param semilla: Semilla para el generador aleatorio.
        :return: Lista de ciudades en el orden del tour y la distancia total del tour.
        """
        random.seed(semilla)  # Establece la semilla para la aleatoriedad
        tamanio_entorno = int(self.params['iteraciones'] * self.params['per_tamanio'])
        cont = int(self.params['iteraciones'] * self.params['per_iteraciones'])
        ite = 0
        estancamiento_contador = 0

        if logger: logger.registrar_evento(f"Partimos de la solución del Greedy Aleatorio: {self.distancia_actual}")
        if logger: logger.registrar_evento(f"Solucion actual = {self.distancia_actual} | Mejor momento actual = {self.distancia_mejor_momento_actual} | Mejor Global = {self.distancia_mejor_global}\n")

        for iteracion in range(self.params['iteraciones']):
            # Generar vecinos
            vecinos_filtrados = []
            for _ in range(tamanio_entorno):
                vecino, nueva_distancia, i, j = Utilidades.generar_vecino(self.tour_actual, self.matriz_distancias, self.distancia_actual)
                if self.movimiento_no_tabu((i, j)):
                    vecinos_filtrados.append((vecino, nueva_distancia, (i, j)))

            if logger: logger.registrar_evento(f"Iteración: {iteracion}, Tamaño del entorno: {tamanio_entorno}, Vecinos generados: {tamanio_entorno}")

            # Buscar el mejor vecino
            mejor_vecino = min(vecinos_filtrados, key=lambda x: x[1], default=(None, float('inf'), None))
            nuevo_tour, nueva_distancia, movimiento = mejor_vecino

            if logger: logger.registrar_evento(f"Mejor vecino (movimiento): {movimiento}, Distancia: {nueva_distancia}")

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

                if logger: logger.registrar_evento(f"¡Mejora encontrada! Distancia actual: {nueva_distancia}")

                self.actualizar_mcp(nuevo_tour, movimiento)
                self.actualizar_mlp(nuevo_tour)
                estancamiento_contador = 0  # Reiniciar el contador de estancamiento
            else:
                estancamiento_contador += 1

            # Verificar si hay estancamiento
            if estancamiento_contador >= self.params['per_estancamiento'] * self.params['iteraciones']:
                if logger: logger.registrar_evento("Estancamiento detectado, generando nueva solución...")
                self.generar_nueva_solucion(logger)
                estancamiento_contador = 0  # Reiniciar el contador de estancamiento

            # Reducir el tamaño del entorno cada 10% de iteraciones del total
            tamanio_entorno, cont, ite = Utilidades.reducir_entorno(tamanio_entorno, cont, iteracion, self.params['per_disminucion'], self.params['per_iteraciones'], ite)
            if tamanio_entorno < (self.params['per_disminucion'] * 100):
                break

            if logger: logger.registrar_evento(f"Solucion actual = {self.distancia_actual} | Mejor momento actual = {self.distancia_mejor_momento_actual} | Mejor Global = {self.distancia_mejor_global} | Estancamiento: {estancamiento_contador}\n")

        return self.mejor_global, self.distancia_mejor_global

    def movimiento_no_tabu(self, movimiento):
        """
        Comprueba si un movimiento no está en la lista tabú (MCP).

        :param movimiento: El par de índices a intercambiar (i, j).
        :return: True si el movimiento no es tabú, False en caso contrario.
        """
        i, j = movimiento

        # El par siempre se guarda en un orden consistente (i, j)
        movimiento_tabu = (min(i, j), max(i, j))

        # Verificar si el movimiento está en la lista tabú (circular)
        for tabu in self.mcp_lista_tabu:
            if tabu == movimiento_tabu:
                # Si el movimiento está en la lista tabú, se considera prohibido
                return False

        # Si no está en la lista tabú, el movimiento no es tabú
        return True

    def actualizar_mcp(self, nuevo_tour, movimiento):
        """
        Actualiza la MCP (Memoria de Control de Prohibición) mediante la lista circular y el diccionario de tenencias.

        :param nuevo_tour: El nuevo tour generado.
        :param movimiento: El movimiento realizado (índices i, j).
        """
        # Reducir la tenencia de todos los movimientos prohibidos en la MCP
        movimientos_a_eliminar = []
        for casilla, tenencia in self.mcp_tenencias.items():
            # Decrementar la tenencia de cada movimiento
            self.mcp_tenencias[casilla] -= 1
            # Si la tenencia llega a 0 o menos, marcar para eliminación
            if self.mcp_tenencias[casilla] <= 0:
                movimientos_a_eliminar.append(casilla)

        # Eliminar los movimientos cuya tenencia ha caducado
        for movimiento_eliminar in movimientos_a_eliminar:
            del self.mcp_tenencias[movimiento_eliminar]
            # También eliminar de la lista circular si está presente
            if movimiento_eliminar in self.mcp_lista_tabu:
                self.mcp_lista_tabu.remove(movimiento_eliminar)

        # Actualizar la tenencia para el nuevo movimiento en la MCP
        i, j = movimiento
        ciudad_1, ciudad_2 = nuevo_tour[i], nuevo_tour[j]

        # Crear las casillas que representan los pares (índice, ciudad) en la MCP
        casilla_1 = (min(i, ciudad_1), max(i, ciudad_1))
        casilla_2 = (min(j, ciudad_2), max(j, ciudad_2))

        # Establecer el valor de tenencia tabú para estos movimientos
        tenencia_tabu = self.params['tenencia']
        self.mcp_tenencias[casilla_1] = tenencia_tabu
        self.mcp_tenencias[casilla_2] = tenencia_tabu

        # Añadir los movimientos a la lista circular (lista tabú)
        self.mcp_lista_tabu.append(casilla_1)
        self.mcp_lista_tabu.append(casilla_2)

        # Si la lista tabú excede el tamaño máximo, eliminar los movimientos más antiguos
        while len(self.mcp_lista_tabu) > self.params['tamano_lista_circular']:
            movimiento_mas_antiguo = self.mcp_lista_tabu.popleft()
            # También eliminar la tenencia correspondiente si existe en el diccionario
            if movimiento_mas_antiguo in self.mcp_tenencias:
                del self.mcp_tenencias[movimiento_mas_antiguo]

    def actualizar_mlp(self, nuevo_tour):
        """
        Actualiza la MLP (Memoria a Largo Plazo) incrementando los arcos visitados en el tour actual.
        Utiliza un diccionario para almacenar los conteos de los arcos.

        :param nuevo_tour: La lista de ciudades del tour actual.
        """
        # Recorrer el tour e incrementar el conteo de los arcos en el diccionario de la MLP
        for k in range(len(nuevo_tour)):
            origen = nuevo_tour[k]
            destino = nuevo_tour[(k + 1) % len(nuevo_tour)]  # Asegura que el destino sea cíclico

            # Crear la clave para el arco (ordenado de menor a mayor para consistencia)
            arco = (min(origen, destino), max(origen, destino))

            # Incrementar el conteo del arco en el diccionario
            if arco in self.mlp:
                self.mlp[arco] += 1
            else:
                self.mlp[arco] = 1

    def generar_nueva_solucion(self, logger=None):
        """
        Genera una nueva solución mediante oscilación estratégica (diversificación o intensificación).
        Utiliza la información de la MLP para influir en la estrategia elegida.
        """
        if random.random() < self.params['oscilacion_estrategica']:
            if logger: logger.registrar_evento("Ejecutando diversificación.")
            self.tour_actual = self.estrategia_diversificacion()
        else:
            if logger: logger.registrar_evento("Ejecutando intensificación.")
            self.tour_actual = self.estrategia_intensificacion()

        # Reiniciar solo la MCP
        self.mcp_lista_tabu.clear()  # Limpiar la lista tabú
        self.mcp_tenencias.clear()  # Limpiar el diccionario de tenencias

        # Reiniciar la distancia
        self.distancia_actual = Utilidades.calcular_distancia_total(self.tour_actual, self.matriz_distancias)
        if logger: logger.registrar_evento(f"NUEVA SOLUCIÓN: {self.distancia_actual}")

    def estrategia_diversificacion(self):
        """
        Implementa la lógica de diversificación utilizando la información de la MLP.
        Busca los arcos menos utilizados en mlp_diccionario para generar una nueva solución.
        """
        # Obtener los arcos menos utilizados
        arcos_menos_usados = sorted(self.mlp.items(), key=lambda item: item[1])
        # Extraer las ciudades de los arcos menos utilizados utilizando conjuntos
        ciudades_utilizadas = {ciudad for arco in arcos_menos_usados[:10] for ciudad in arco[0]}

        # Crear un nuevo tour aleatorio utilizando las ciudades menos usadas
        nuevas_ciudades = list(ciudades_utilizadas)
        random.shuffle(nuevas_ciudades)

        # Completar el tour con las ciudades que no están en las ciudades menos usadas
        ciudades_restantes = set(self.tour_actual) - ciudades_utilizadas
        nuevo_tour = nuevas_ciudades + list(ciudades_restantes)

        return nuevo_tour

    def estrategia_intensificacion(self):
        """
        Implementa la lógica de intensificación utilizando la información de la MLP.
        Busca los arcos más utilizados en mlp_diccionario para generar una nueva solución.
        """
        # Obtener los arcos más utilizados
        arcos_mas_usados = sorted(self.mlp.items(), key=lambda item: item[1], reverse=True)
        # Extraer las ciudades de los arcos más utilizados utilizando conjuntos
        ciudades_utilizadas = {ciudad for arco in arcos_mas_usados[:10] for ciudad in arco[0]}

        # Crear un nuevo tour aleatorio utilizando las ciudades más usadas
        nuevas_ciudades = list(ciudades_utilizadas)
        random.shuffle(nuevas_ciudades)

        # Completar el tour con las ciudades que no están en las ciudades más usadas
        ciudades_restantes = set(self.tour_actual) - ciudades_utilizadas
        nuevo_tour = nuevas_ciudades + list(ciudades_restantes)

        return nuevo_tour