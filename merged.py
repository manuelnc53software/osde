import pandas as pd
import os

# Directorio donde están los archivos CSV
carpeta_csv = "prestadores"

# Obtener la lista de archivos CSV en la carpeta
archivos_csv = [f for f in os.listdir(carpeta_csv) if f.endswith('.csv')]

# Lista donde se almacenarán los DataFrames
dataframes = []

# Leer todos los archivos CSV y almacenarlos en la lista de DataFrames
for archivo in archivos_csv:
    ruta_archivo = os.path.join(carpeta_csv, archivo)
    df = pd.read_csv(ruta_archivo)
    dataframes.append(df)

# Combinar todos los DataFrames en uno solo
df_combinado = pd.concat(dataframes, ignore_index=True)

# Eliminar filas duplicadas
df_sin_duplicados = df_combinado.drop_duplicates()

# Guardar el resultado en un nuevo archivo CSV
archivo_salida = os.path.join(carpeta_csv, 'prestadores_merged.csv')
df_sin_duplicados.to_csv(archivo_salida, index=False)

print(f"Archivo combinado guardado como {archivo_salida}")
