import requests
import json
import csv
import os
import shutil
from tqdm import tqdm
import pandas as pd
from datetime import datetime
import time

# Número máximo de reintentos
MAX_REINTENTOS = 3
TIMEOUT_SEGUNDOS = 5

# Endpoints
PLANS_URL = "https://www.osde.com.ar/Cartilla/PlanRemote.ashx?metodo=ObtenerPlanesParaCartillaMedicaConNoComercial&r=0.13880617927273597"
PROVINCIAS_URL = "https://www.osde.com.ar/Cartilla/ProvinciaRemote.ashx?metodo=ObtenerParaCartillaMedica&busquedaActual=especialidad"
LOCALIDADES_URL = "https://www.osde.com.ar/Cartilla/LocalidadRemote.ashx?metodo=ObtenerParaCartillaMedica&tipoProvincia={provinciaTipo}&provinciaId={provinciaId}&planId={planId}"
PRESTADORES_URL = "https://www.osde.com.ar/Cartilla/consultaPorEspecialidadRemote.ashx"

# Especialidades de psicología
ESPECIALIDADES_PSICOLOGIA = [
    ('1025', 'psicodiagnostico'),
    ('810', 'psicologia_adultos'),
    ('870', 'psicologia_ninos_y_adolescentes'),
    ('850', 'psicologia_pareja_y_familia'),
    ('841', 'psicopedagogia'),
    ('808', 'psiquiatria_adultos'),
    ('809', 'psiquiatria_ninos_y_adolescentes'),
    ('1026', 'evaluacion_neurocognitiva_psicologica'),
    ('1027', 'evaluacion_neuropsicopedagogica')
]

# Headers para evitar que el servidor retorne 403
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

#Carpeta de prestadores
CARPETA_CV = "prestadores"

def parsear_respuesta_como_json(response):
    try:
        return response.json()
    except json.JSONDecodeError:
        print("La respuesta no es JSON, tratando de interpretarla como texto.")
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            print(f"Error al decodificar la respuesta: {response.text}")
            return None

def hacer_solicitud_con_reintentos(url, params=None, headers=None):
    intentos = 0
    while intentos < MAX_REINTENTOS:
        try:
            response = requests.get(url, params=params, headers=headers, timeout=TIMEOUT_SEGUNDOS)
            if response.status_code == 200:
                return parsear_respuesta_como_json(response)
            else:
                print(f"Error en la solicitud. Código de estado: {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            intentos += 1
            print(f"Timeout en la solicitud. Reintentando ({intentos}/{MAX_REINTENTOS})...")
            time.sleep(2)  # Esperar 2 segundos antes de reintentar
        except requests.exceptions.RequestException as e:
            intentos += 1
            print(f"Error de conexión: {e}. Reintentando ({intentos}/{MAX_REINTENTOS})...")
            time.sleep(2)  # Esperar 2 segundos antes de reintentar
    print("Error tras múltiples reintentos.")
    return None

def obtener_planes():
    return hacer_solicitud_con_reintentos(PLANS_URL, headers=HEADERS)

def obtener_provincias():
    return hacer_solicitud_con_reintentos(PROVINCIAS_URL, headers=HEADERS)

def obtener_prestadores(provinciaId, provinciaNombre, provinciaTipo, planId, especialidadId):
    params = {
        "metodo": "ObtenerParaCartillaMedica",
        "rubros": 2,
        "rubroId": 2,
        "provinciaId": provinciaId,
        "provinciaTipo": provinciaTipo,
        "provinciaNombre": provinciaNombre,
        "localidadId": 0,
        "localidadNombre": "",
        "planId": planId,
        "especialidadId": especialidadId,
        "especialidadNombre": "",
        "filialId": 1,
        "modalidadAtencion": 2
    }
    return hacer_solicitud_con_reintentos(PRESTADORES_URL, params=params, headers=HEADERS)

def escribir_prestadores_csv(plan_nombre, especialidad_nombre, prestadores):
    # Nombre de la carpeta donde se guardarán los archivos CSV
    carpeta_csv = CARPETA_CV
    
    # Crear la carpeta si no existe
    if not os.path.exists(carpeta_csv):
        os.makedirs(carpeta_csv)
    
    # Crear el nombre del archivo CSV con la ruta de la carpeta
    nombre_archivo = os.path.join(carpeta_csv, f"prestadores_plan_{plan_nombre}_especialidad_{especialidad_nombre}.csv")
    
    # Definir los encabezados del CSV
    headers = [ 'Nombre', 'Dirección', 'Email', 'Teléfono', 'Localidad', 'Provincia', 'Latitud', 'Longitud', 'Barrio', 'Plan', 'Especialidad']
    
    # Si el archivo no existe, escribir los encabezados
    if not os.path.isfile(nombre_archivo):
        with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo_csv:
            escritor_csv = csv.writer(archivo_csv)
            escritor_csv.writerow(headers)
    
    # Crear y escribir en el archivo CSV en modo apéndice
    with open(nombre_archivo, mode='a', newline='', encoding='utf-8') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        
        # Escribir cada prestador en el CSV
        for prestador in prestadores:
            nombre = prestador.get("nombre", "Nombre no disponible")
            # Inicializar valores para un prestador
            direcciones = []
            emails = []
            telefonos = []
            localidades = []
            provincias = []
            latitudes = []
            longitudes = []
            barrios = []

            # Verificar y recoger información de todos los consultorios del prestador
            if prestador.get("consultorios"):
                for consultorio in prestador["consultorios"]:
                    direccion = consultorio.get("direccion", "Dirección no disponible")
                    email = consultorio.get("email", "Email no disponible").strip()
                    telefono = consultorio.get("telefono", "Teléfono no disponible")
                    localidad = consultorio.get("localidad", "Localidad no disponible")
                    provincia = consultorio.get("provincia", "Provincia no disponible")
                    geolocalizacion = consultorio.get("geolocalizacion", {})
                    
                    latitud = geolocalizacion.get("latitud", "Latitud no disponible") if geolocalizacion else "Latitud no disponible"
                    longitud = geolocalizacion.get("longitud", "Longitud no disponible") if geolocalizacion else "Longitud no disponible"
                    barrio = consultorio.get("barrio", "Barrio no disponible")
                    
                    # Agregar información a listas
                    direcciones.append(direccion)
                    emails.append(email)
                    telefonos.append(telefono)
                    localidades.append(localidad)
                    provincias.append(provincia)
                    latitudes.append(latitud)
                    longitudes.append(longitud)
                    barrios.append(barrio)
            
            # Si no hay consultorios, asignar valores por defecto
            if not direcciones:
                direcciones = ["Dirección no disponible"]
                emails = ["Email no disponible"]
                telefonos = ["Teléfono no disponible"]
                localidades = ["Localidad no disponible"]
                provincias = ["Provincia no disponible"]
                latitudes = ["Latitud no disponible"]
                longitudes = ["Longitud no disponible"]
                barrios = ["Barrio no disponible"]
            
            # Escribir la información en el CSV
            for i in range(len(direcciones)):
                escritor_csv.writerow([
                    nombre,
                    direcciones[i],
                    emails[i],
                    telefonos[i],
                    localidades[i],
                    provincias[i],
                    latitudes[i],
                    longitudes[i],
                    barrios[i],
                    plan_nombre,
                    especialidad_nombre
                ])

def buscar_prestadores_psicologia():
    planes = obtener_planes()
    if not planes:
        print("No se encontraron planes.")
        return
    
    provincias = obtener_provincias()
    if not provincias:
        print("No se encontraron provincias.")
        return
    
    total_planes = len(planes)
    total_provincias = len(provincias)
    total_especialidades = len(ESPECIALIDADES_PSICOLOGIA)

    # Calcular el total de iteraciones
    total_iteraciones = total_planes * total_provincias * total_especialidades

    # Usar tqdm para la barra de progreso
    with tqdm(total=total_iteraciones, desc="Progreso", unit="iter") as barra_progreso:
        for plan in planes:
            plan_id = plan["id"]
            plan_nombre = plan["nombre"].replace(' ', '_')
            
            for  provincia in provincias:
                provincia_id = provincia["id"]
                provincia_nombre = provincia["nombre"]
                provincia_tipo = provincia["tipo"]
                
                for especialidad_id, especialidad_nombre in ESPECIALIDADES_PSICOLOGIA:
                    
                    # Obtener prestadores
                    prestadores = obtener_prestadores(provincia_id, provincia_nombre, provincia_tipo, plan_id, especialidad_id)
                        
                    if prestadores and prestadores.get("ListaPrestador"):
                        # Escribir prestadores en el CSV
                        escribir_prestadores_csv(plan_nombre, especialidad_nombre, prestadores["ListaPrestador"])
                    else:
                        # Usar tqdm.write para mostrar el mensaje de error arriba de la barra de progreso
                        tqdm.write(f"No se encontraron prestadores en {provincia_nombre}, {provincia_tipo} para la especialidad {especialidad_nombre} del plan {plan_nombre}.")
                    
                    # Actualizar la barra de progreso
                    barra_progreso.update(1)

def eliminar_carpeta_csv():
    carpeta_csv = CARPETA_CV
    
    # Verificar si la carpeta existe
    if os.path.exists(carpeta_csv):
        # Eliminar la carpeta y todo su contenido
        shutil.rmtree(carpeta_csv)
        print(f"La carpeta {carpeta_csv} y su contenido han sido eliminados.")
    else:
        print(f"La carpeta {carpeta_csv} no existe.")

def combinar_csvs():
    carpeta_csv = CARPETA_CV
    
    # Verificar si la carpeta existe
    if not os.path.exists(carpeta_csv):
        print(f"Error: La carpeta '{carpeta_csv}' no existe.")
        return
    
    # Obtener la lista de archivos CSV en la carpeta
    archivos_csv = [f for f in os.listdir(carpeta_csv) if f.endswith('.csv')]
    
    # Verificar si hay archivos CSV en la carpeta
    if not archivos_csv:
        print(f"Error: No se encontraron archivos CSV en la carpeta '{carpeta_csv}'.")
        return

    # Lista donde se almacenarán los DataFrames
    dataframes = []

    # Leer todos los archivos CSV y almacenarlos en la lista de DataFrames
    for archivo in archivos_csv:
        ruta_archivo = os.path.join(carpeta_csv, archivo)
        try:
            df = pd.read_csv(ruta_archivo)
            dataframes.append(df)
        except Exception as e:
            print(f"Error al leer el archivo {archivo}: {e}")
            continue

    # Verificar si se cargaron DataFrames
    if not dataframes:
        print(f"Error: No se pudieron cargar archivos CSV de la carpeta '{carpeta_csv}'.")
        return

    # Combinar todos los DataFrames en uno solo
    df_combinado = pd.concat(dataframes, ignore_index=True)

    # Reemplazar valores vacíos en todas las columnas relevantes con una cadena vacía
    columnas_relevantes = ['Nombre', 'Dirección', 'Email', 'Teléfono', 'Localidad', 'Provincia', 'Latitud', 'Longitud', 'Barrio', 'Plan', 'Especialidad']
    df_combinado[columnas_relevantes] = df_combinado[columnas_relevantes].fillna('')

    # Agrupar por los campos clave y combinar las columnas 'Plan' y 'Especialidad'
    df_sin_duplicados = df_combinado.groupby(
        ['Nombre', 'Dirección', 'Email', 'Teléfono', 'Localidad', 'Provincia', 'Latitud', 'Longitud', 'Barrio']
    ).agg({
        'Plan': lambda x: ', '.join(sorted(set(x.dropna().astype(str)))),
        'Especialidad': lambda x: ', '.join(sorted(set(x.dropna().astype(str)))),
    }).reset_index()

    # Guardar el resultado en un nuevo archivo CSV en la raíz del proyecto
    nombre_archivo = f"prestadores_{datetime.now().strftime('%d%m%Y')}.csv"
    archivo_salida = os.path.join(os.getcwd(), nombre_archivo)
    df_sin_duplicados.to_csv(archivo_salida, index=False)

    print(f"Archivo combinado guardado como {archivo_salida}")

if __name__ == "__main__":
    eliminar_carpeta_csv()
    buscar_prestadores_psicologia() 
    combinar_csvs()
