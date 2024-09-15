# README
## Introducción
Este script extrae datos del sitio web de OSDE Argentina (https://www.osde.com.ar/index1.html#!cartilla.html), específicamente de su directorio de prestadores médicos, con el objetivo de generar una lista completa de psicólogos registrados en el sistema. A través de consultas automatizadas a la cartilla médica de OSDE, el script genera archivos CSV con la información de todos los psicólogos disponibles por provincia, plan y especialidad. Finalmente, combina todos los datos en un archivo llamado `prestadores_<fecha_actual>.csv`

Un archivo de ejemplo` prestadores_15092024.csv` ([link](https://github.com/manuelnc53software/osde/blob/main/prestadores_15092024.csv "link")) se proporciona para ilustrar el formato del resultado final.

## Requisitos
Este proyecto está diseñado para ejecutarse con Python 3.x. A continuación, se detallan las dependencias necesarias y sus usos:

- **requests**: Para hacer solicitudes HTTP GET a las URLs de OSDE y extraer los datos.
- **json**: Para manejar las respuestas en formato JSON que provienen de las solicitudes HTTP.
- **csv**: Para escribir los resultados de las consultas en archivos CSV.
- **os**: Para la manipulación de directorios y archivos dentro del sistema operativo.
- **shutil**: Para eliminar directorios completos, incluyendo su contenido.
- **tqdm**: Para mostrar una barra de progreso mientras se ejecuta el script.
- **pandas**: Para leer, manipular y combinar los datos de varios archivos CSV.
- **datetime**: Para agregar marcas de tiempo al nombre de los archivos de salida.
- **time**: Para agregar pausas entre reintentos en caso de error de conexión o timeout.

##Instalación de dependencias:
Puedes instalar todas las dependencias necesarias utilizando `pip`. Aquí te mostramos cómo hacerlo:

```bash
pip install requests tqdm pandas
```

Este comando instalará las siguientes librerías:

- `requests:` Para manejar solicitudes HTTP.
- `tqdm: ` Para mostrar una barra de progreso.
-  `pandas:  `Para la manipulación y combinación de archivos CSV.


## Cómo ejecutar el script
Asegúrate de que tienes Python 3.x instalado en tu sistema.
Descarga este repositorio o clona el proyecto en tu máquina local.
Instala las dependencias como se indicó anteriormente.
Ejecuta el script desde la terminal:

```bash
py main.py
```

## Explicación del Código
### Secciones Principales

1. Configuración inicial: Aquí se definen URLs de los distintos endpoints de OSDE para extraer información sobre planes, provincias, localidades y prestadores.

2. Headers: Los encabezados HTTP incluyen un `User-Agent` para evitar bloqueos o restricciones por parte del servidor.

3. Manejo de solicitudes HTTP:

	-  `hacer_solicitud_con_reintentos: `Realiza solicitudes HTTP y maneja errores de conexión o tiempos de espera. Si la solicitud falla, intenta hasta 3 veces antes de detenerse.

4. Extracción de datos:

	-  `obtener_planes, obtener_provincias, obtener_prestadores: `Estas funciones hacen llamadas a los respectivos endpoints de OSDE para obtener información sobre planes de salud, provincias y prestadores médicos.

5. Escritura en CSV:

	- `escribir_prestadores_csv: `Guarda los prestadores de salud en archivos CSV específicos, organizados por plan y especialidad. Cada archivo incluye información como el nombre del prestador, dirección, email, teléfono, entre otros.

6. Combinar archivos CSV:

 	- `combinar_csvs:` Lee todos los archivos CSV generados y combina los datos en un archivo único, eliminando duplicados y asegurando que las columnas 'Plan' y 'Especialidad' contengan todos los valores posibles sin redundancias.

7. Eliminación de la carpeta:

	- `eliminar_carpeta_csv:` Si existe una carpeta con archivos CSV generados previamente, la elimina antes de ejecutar nuevamente el script, asegurando que los datos sean actuales.

## Ejecución Principal
En la sección `if __name__ == "__main__":`, el código ejecuta las siguientes acciones en orden:

1. **Eliminar CSV previos:** Si existe la carpeta de prestadores con archivos previos, la elimina.
2. **Buscar prestadores:** Extrae todos los prestadores de psicología para cada plan y provincia y los guarda en archivos CSV.
3. **Combinar archivos CSV:** Todos los archivos CSV generados se combinan en uno solo.

## Archivo CSV de ejemplo
El archivo `prestadores_15092024.csv` contiene un ejemplo de la salida final del script, con información como:

- Nombre del prestador
- Dirección
- Email
- Teléfono
- Localidad
- Provincia
- Latitud
- Longitud
- Barrio
- Plan
- Especialidad

Este archivo se genera automáticamente con la fecha actual en el nombre para mantener un registro actualizado.