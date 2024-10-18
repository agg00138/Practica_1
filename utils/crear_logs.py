class Logger:
    def __init__(self, nombre_algoritmo, archivo_tsp, semilla, num_ejecucion, echo=True):
        self.log_file = None
        self.echo = echo

        # Si echo es False, generar el archivo de log
        if not self.echo:
            log_filename = f"logs/{nombre_algoritmo}_{archivo_tsp['nombre']}_{semilla}_ejecucion_{num_ejecucion}.log"
            self.log_file = open(log_filename, 'w')

    def registrar_evento(self, mensaje):
        """Registra un evento en el archivo de log o imprime en consola."""
        if self.echo:
            print(mensaje)
        elif self.log_file:
            self.log_file.write(mensaje + '\n')

    def cerrar_log(self):
        """Cierra el archivo de log, si existe."""
        if self.log_file:
            self.log_file.close()