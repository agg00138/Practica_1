import re


class Configuracion:
    def __init__(self, archivo):
        self.archivo = archivo
        self.params = {}

    def procesar(self):
        """Lee el archivo de configuración y llena el diccionario de parámetros."""
        with open(self.archivo, 'r') as file:
            contenido = file.readlines()

        # Procesar cada línea
        for linea in contenido:
            linea = linea.strip()  # Limpiar espacios
            if linea.startswith('#') or not linea:  # Ignorar comentarios y líneas vacías
                continue

            # Usar expresiones regulares para capturar clave y valor
            match = re.match(r'(\w+)\s*=\s*(.+)', linea)
            if match:
                clave = match.group(1)
                valor = match.group(2).strip()

                # Convertir el valor a la tipo adecuado
                if valor.startswith('[') and valor.endswith(']'):  # Es una lista
                    valor = [x.strip() for x in valor[1:-1].split(',')]
                elif valor.isdigit():  # Es un número entero
                    valor = int(valor)
                elif valor.replace('.', '', 1).isdigit():  # Es un número decimal
                    valor = float(valor)
                elif valor.lower() in ['yes', 'no']:  # Es un booleano
                    valor = valor.lower() == 'yes'

                # Almacenar en el diccionario de parámetros
                self.params[clave] = valor

        return self.params