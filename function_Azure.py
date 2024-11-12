import os
from azure.storage.blob import BlobServiceClient

# Cadena de conexión a tu cuenta de almacenamiento de Azure
connect_str = os.getenv("AZURE_STORAGE_KEY")
container_name = "pruebasrasp"  # Nombre del contenedor

# Crear un cliente para interactuar con Azure Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

def upload_to_azure(folder_path, local_path):
    """
    Sube un archivo individual o todos los archivos en un directorio a Azure Blob Storage
    y guarda las URLs en un archivo .txt.

    Parameters:
    - folder_path: Nombre de la carpeta principal en Azure Blob Storage donde se subirán los archivos.
    - local_path: Ruta local del archivo o directorio a subir.
    """
    urls_info = []  # Lista para almacenar la información de cada archivo subido

    try:
        # Obtener el cliente del contenedor
        container_client = blob_service_client.get_container_client(container_name)
        
        # Crear el contenedor si no existe
        if not container_client.exists():
            container_client.create_container()
            print(f"Contenedor '{container_name}' creado.")

        # Extraer el nombre del usuario desde la ruta local
        user_name = os.path.basename(local_path)
        
        # Crear una subcarpeta para el usuario dentro de la carpeta principal
        user_folder_path = f"{folder_path}/{user_name}"

        # Subir archivo individual
        if os.path.isfile(local_path):
            url = upload_file(user_folder_path, local_path)
            urls_info.append(f"{user_name} {os.path.basename(local_path)} URL en Azure: {url}")
        # Subir todos los archivos en un directorio
        elif os.path.isdir(local_path):
            for root, _, files in os.walk(local_path):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(file_path, local_path)
                    blob_name = f"{user_folder_path}/{relative_path}".replace("\\", "/")
                    url = upload_file(user_folder_path, file_path)
                    urls_info.append(f"{user_name} {file_name} URL en Azure: {url}")
        else:
            print("Ruta especificada no válida.")

        # Guardar todas las URLs en un archivo .txt
        with open("urls_azure.txt", "w") as txt_file:
            for line in urls_info:
                txt_file.write(line + "\n")
        print("Archivo 'urls_azure.txt' generado con las URLs de los archivos subidos.")

    except Exception as e:
        print(f"Error al subir archivos: {e}")

def upload_file(folder_path, file_path):
    """
    Sube un archivo individual a Azure Blob Storage y retorna su URL.

    Parameters:
    - folder_path: Carpeta en Azure Blob Storage donde se subirá el archivo.
    - file_path: Ruta local del archivo a subir.

    Returns:
    - URL del archivo subido.
    """
    try:
        blob_name = f"{folder_path}/{os.path.basename(file_path)}"
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data)
        
        # Obtener URL del archivo subido
        url = blob_client.url
        print(f"Archivo '{file_path}' subido exitosamente a '{blob_name}'")
        return url
    except Exception as e:
        print(f"Error al subir el archivo {file_path}: {e}")
        return None

# Ejemplo de uso
folder_path = "pruebas"  # Carpeta principal en Azure Blob Storage
local_path = r"C:\Users\range\Desktop\pelayo_pelayo\imagenes\Juan Eduardo"  # Archivo o directorio local
upload_to_azure(folder_path, local_path)
