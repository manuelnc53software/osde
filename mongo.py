from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['mtl']  # Nombre de tu base de datos

# Obtener todas las colecciones en la base de datos
collections = db.list_collection_names()

# Diccionario para almacenar el esquema de cada colección
schema_por_coleccion = {}

# Recorrer todas las colecciones
for collection_name in collections:
    collection = db[collection_name]
    docs = collection.find().limit(1000)  # Obtener los primeros 1000 documentos
    schema = {}

    # Extraer claves y tipos de cada documento
    for doc in docs:
        for key, value in doc.items():
            schema[key] = type(value).__name__

    # Asignar el esquema al nombre de la colección
    schema_por_coleccion[collection_name] = schema

# Imprimir el esquema de todas las colecciones
for collection_name, schema in schema_por_coleccion.items():
    print(f"Esquema para la colección '{collection_name}':")
    print(schema)
    print("\n")