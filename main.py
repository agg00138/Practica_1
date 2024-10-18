import sys, os, time

from algoritmos.Alg01_Clase01_Grupo06 import GreedyAleatorio
from algoritmos.Alg02_Clase01_Grupo06 import BusquedaLocal
from algoritmos.Alg03_Clase01_Grupo06 import AlgoritmoTabu
from utils.procesar_configuracion import Configuracion
from utils.procesar_tsp import TSP
from utils.utilidades import Utilidades
from utils.crear_logs import Logger

if __name__ == "__main__":

    # Compruebo que el número de parámetros sea correcto
    if len(sys.argv) != 2:
        print("Uso: python ./main.py ./params.txt")
        sys.exit(1)

    # Procesar configuración
    archivo_configuracion = sys.argv[1]
    configuracion = Configuracion(archivo_configuracion)
    params = configuracion.procesar()

    print("Parámetros Procesados:")
    for clave, valor in params.items():
        print(f"{clave}: {valor}")

    # Generar las semillas a partir del DNI
    semillas = Utilidades.generar_semillas(params['dni'], params['num_ejecuciones'])

    print("Semillas generadas:", semillas)

    # Obtener la lista de archivos TSP desde la configuración
    archivos_tsp = params['archivos']

    # Crear logs solo si params['echo'] es False (antes era 'no')
    if not params['echo']:
        os.makedirs('logs', exist_ok=True)

    # Procesar cada archivo TSP
    for archivo_tsp in archivos_tsp:
        ruta_archivo = os.path.join('data', archivo_tsp)  # Construye la ruta completa
        tsp = TSP(ruta_archivo)  # Crea una instancia de TSP
        matriz_distancias, tour_inicial = tsp.procesar()  # Procesa el archivo
        print(f"\n===========================")
        print(f"Procesado {archivo_tsp}:")
        print(f"===========================")
        # print("Matriz de distancias:", matriz_distancias)
        # print("Tour inicial:", tour_inicial)

        # Ejecutar el algoritmo Greedy Aleatorio con cada semilla
        for i, semilla in enumerate(semillas, start=1):
            log_greedy = Logger(nombre_algoritmo="greedy_aleatorio", archivo_tsp={'nombre': archivo_tsp}, semilla=semilla, num_ejecucion=i, echo=params['echo'])
            log_greedy.registrar_evento(f"Ejecutando Greedy Aleatorio con la semilla {semilla}:")
            greedy_aleatorio = GreedyAleatorio(matriz_distancias, params)
            start_time = time.time()
            tour, distancia_total = greedy_aleatorio.resolver(semilla, logger=log_greedy)
            execution_time = time.time() - start_time
            log_greedy.registrar_evento(f"\nTour obtenido: {list(map(int, tour))}")
            log_greedy.registrar_evento(f"Distancia total: {distancia_total}, Tiempo: {execution_time}")
            log_greedy.cerrar_log()  # Solo cerrar si `echo` es False

            log_bl = Logger(nombre_algoritmo="busqueda_local", archivo_tsp={'nombre': archivo_tsp}, semilla=semilla, num_ejecucion=i, echo=params['echo'])
            log_bl.registrar_evento(f"Ejecutando Búsqueda Local del mejor con la semilla {semilla}:")
            busqueda_local = BusquedaLocal(tour, distancia_total, matriz_distancias, params)
            start_time = time.time()
            tour_busqueda, distancia_busqueda = busqueda_local.resolver(semilla, logger=log_bl)
            execution_time = time.time() - start_time
            log_bl.registrar_evento(f"\nTour obtenido: {list(map(int, tour_busqueda))}")
            log_bl.registrar_evento(f"Distancia total: {distancia_busqueda}, Tiempo: {execution_time}")
            log_bl.cerrar_log()  # Solo cerrar si `echo` es False

            # print(f"\nEjecutando Algoritmo Tabú con la semilla {semilla}:")
            # algoritmo_tabu = AlgoritmoTabu(tour, distancia_total, matriz_distancias, params)
            # start_time = time.time()
            # tour_tabu, distancia_tabu = algoritmo_tabu.resolver(semilla)
            # execution_time = time.time() - start_time
            # print("Distancia total:", distancia_tabu, ", Tiempo:", execution_time)