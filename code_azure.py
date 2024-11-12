from azure.storage.blob import BlobServiceClient

# Cadena de conexión a tu cuenta de almacenamiento de Azure
connect_str = os.getenv("AZURE_STORAGE_KEY")

# Nombre del contenedor y ruta del archivo dentro del contenedor
container_name = "raspberryprueba" #Nombre del contenedor
folder_path = "pruebas" #Carpeta a crear
local_file = "/home/ausencio/Desktop/deere2.jpg" #Ruta del archivo a mandar

# Crear un cliente para interactuar con Azure Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

# Construir la ruta completa del blob en el contenedor
blob_name = f"{folder_path}/{local_file.split('/')[-1]}"

# Subir el archivo al blob
try:
    with open(local_file, "rb") as data:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(data)
        print(f"Archivo {local_file} subido exitosamente a {blob_name}")
except Exception as e:
    print(f"Error al subir el archivo: {e}")

# Validar la conexión (opcional)
try:
    blob_service_client.get_container_client(container_name)
    print("Conexión a Azure Storage exitosa")
except Exception as e:
    print("Error al conectar:", e)