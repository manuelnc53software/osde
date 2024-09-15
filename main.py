import requests
import json
import csv
import os
import shutil
from tqdm import tqdm

# Endpoints
PLANS_URL = "https://www.osde.com.ar/Cartilla/PlanRemote.ashx?metodo=ObtenerPlanesParaCartillaMedicaConNoComercial&r=0.13880617927273597"
PROVINCIAS_URL = "https://www.osde.com.ar/Cartilla/ProvinciaRemote.ashx?metodo=ObtenerParaCartillaMedica&busquedaActual=especialidad"
LOCALIDADES_URL = "https://www.osde.com.ar/Cartilla/LocalidadRemote.ashx?metodo=ObtenerParaCartillaMedica&tipoProvincia={provinciaTipo}&provinciaId={provinciaId}&planId={planId}"
PRESTADORES_URL = "https://www.osde.com.ar/Cartilla/consultaPorEspecialidadRemote.ashx"

# Especialidades de psicología
ESPECIALIDADES_PSICOLOGIA = [
    ('1025', 'PSICODIAGNÓSTICO'),
    ('810', 'PSICOLOGÍA ADULTOS'),
    ('870', 'PSICOLOGÍA NIÑOS Y ADOLESCENTES'),
    ('850', 'PSICOLOGÍA PAREJA Y FAMILIA'),
    ('841', 'PSICOPEDAGOGÍA'),
    ('808', 'PSIQUIATRÍA ADULTOS'),
    ('809', 'PSIQUIATRÍA NIÑOS Y ADOLESCENTES'),
    ('1026', 'EVALUACIÓN NEUROCOGNITIVA PSICOLÓGICA'),
    ('1027', 'EVALUACIÓN NEUROPSICOPEDAGÓGICA')
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

def obtener_planes():
    try:
        response = requests.get(PLANS_URL, headers=HEADERS)
        if response.status_code == 200:
            return parsear_respuesta_como_json(response)
        else:
            print(f"Error al obtener planes. Código de estado: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión al obtener planes: {e}")
        return []

def obtener_provincias():
    try:
        response = requests.get(PROVINCIAS_URL, headers=HEADERS)
        if response.status_code == 200:
            return parsear_respuesta_como_json(response)
        else:
            print(f"Error al obtener provincias. Código de estado: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión al obtener provincias: {e}")
        return []


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
    try:
        response = requests.get(PRESTADORES_URL, params=params, headers=HEADERS)
        if response.status_code == 200:
            return parsear_respuesta_como_json(response)
        else:
            print(f"Error al obtener prestadores para provincia {provinciaNombre} y especialidad {especialidadId}. Código de estado: {response.status_code}")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión al obtener prestadores: {e}")
        return {}

def escribir_prestadores_csv(plan_nombre, especialidad_nombre, prestadores):
    # Nombre de la carpeta donde se guardarán los archivos CSV
    carpeta_csv = CARPETA_CV
    
    # Crear la carpeta si no existe
    if not os.path.exists(carpeta_csv):
        os.makedirs(carpeta_csv)
    
    # Crear el nombre del archivo CSV con la ruta de la carpeta
    nombre_archivo = os.path.join(carpeta_csv, f"prestadores_plan_{plan_nombre}_especialidad_{especialidad_nombre}.csv")
    
    # Definir los encabezados del CSV
    headers = ['Nombre', 'Dirección', 'Email', 'Teléfono', 'Localidad', 'Provincia', 'Latitud', 'Longitud', 'Barrio']
    
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
                    barrios[i]
                ])


def calcular_porcentaje(total_planes, total_provincias, total_especialidades, plan_index, provincia_index, especialidad_index):
    total_combinaciones = total_planes * total_provincias * total_especialidades  # Total de combinaciones posibles
    progreso_actual = ((plan_index - 1) * total_provincias * total_especialidades) + ((provincia_index - 1) * total_especialidades) + especialidad_index
    porcentaje = (progreso_actual / total_combinaciones) * 100
    return porcentaje


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
        for plan_index, plan in enumerate(planes, start=1):
            plan_id = plan["id"]
            plan_nombre = plan["nombre"].replace(' ', '_')
            
            for provincia_index, provincia in enumerate(provincias, start=1):
                provincia_id = provincia["id"]
                provincia_nombre = provincia["nombre"]
                provincia_tipo = provincia["tipo"]
                
                for especialidad_index, (especialidad_id, especialidad_nombre) in enumerate(ESPECIALIDADES_PSICOLOGIA, start=1):
                    
                    # Calcular el porcentaje de proceso
                    porcentaje = calcular_porcentaje(total_planes, total_provincias, total_especialidades, plan_index, provincia_index, especialidad_index)

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

if __name__ == "__main__":
    eliminar_carpeta_csv()
    buscar_prestadores_psicologia()
