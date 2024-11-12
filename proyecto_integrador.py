# Importar librerías
import RPi.GPIO as GPIO
import time
import cv2
import os
from datetime import datetime
from dotenv import load_dotenv
import Adafruit_DHT
from azure.storage.blob import BlobServiceClient

# Cadena de conexión a tu cuenta de almacenamiento de Azure
connect_str = os.getenv("AZURE_STORAGE_KEY")
container_name = "pruebasrasp"  # Nombre del contenedor

# Crear un cliente para interactuar con Azure Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)

# Pines del botón, buzzer y LEDs
GPIO_BUTTON = 17
GPIO_BUZZER = 22

# Configuración de pines como salida o entrada
GPIO.setup(GPIO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_BUZZER, GPIO.OUT)

# Cargar el modelo entrenado de reconocimiento facial
face_recognizer = cv2.face.LBPHFaceRecognizer_create()
face_recognizer.read('modelo_LBPH.xml')

# Cargar Haar Cascade para detección de rostros
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Cargar los nombres desde el archivo
people = {}
with open('nombres.txt', 'r') as f:
    for line in f.readlines():
        label, name = line.strip().split(',')
        people[int(label)] = name

# Función para medir la distancia con el sensor ultrasónico
def disparador():
    button_state = GPIO.input(GPIO_BUTTON)
    if button_state == GPIO.LOW:
            return True
    else:
        return False

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

# Función para reconocimiento facial
def reconocimiento_facial(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        rostro = gray[y:y+h, x:x+w]
        rostro = cv2.resize(rostro, (200, 200))

        label, confidence = face_recognizer.predict(rostro)
        
        if confidence < 70:
            nombre = people[label]
            print(f"¡Bienvenido, {nombre}! Confianza: {confidence:.2f}")

            # Leer temperatura
            temperatura = leer_temperatura()
            if temperatura:
                print(f"Temperatura ambiente: {temperatura:.1f}°C")
            
            # Guardar la imagen del usuario reconocido
            ahora = datetime.now()
            fecha = ahora.strftime("%Y-%m-%d")
            hora = ahora.strftime("%H-%M-%S")
            folder_path = os.path.join('entradas', fecha)
            os.makedirs(folder_path, exist_ok=True)
            image_path = os.path.join(folder_path, f"{nombre}_{hora}.jpg")
            cv2.imwrite(image_path, frame)
            folder_path = "pruebas"  # Carpeta principal en Azure Blob Storage
            upload_to_azure(folder_path, image_path)

            # Encender LED verde y hacer sonar el buzzer (2 pitidos cortos)
            GPIO.output(GPIO_BUZZER, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(GPIO_BUZZER, GPIO.LOW)
            time.sleep(0.1)
            GPIO.output(GPIO_BUZZER, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(GPIO_BUZZER, GPIO.LOW)
            
            return True  # Usuario reconocido
        
        else:
            print(f"Desconocido con confianza: {confidence:.2f}")
            return False  # Usuario desconocido

# Bucle principal
try:
    while True:

        # Si alguien está cerca (menos de 50 cm)
        if disparador == True:
            print("Persona detectada. Esperando botón para captura...")

            print("Botón presionado. Capturando imagen...")

            # Capturar la imagen desde la cámara
            camara = "http://192.168.1.100:8080/video"  # Cambiar esta URL si es necesario
            cap = cv2.VideoCapture(camara)
            ret, frame = cap.read()
            cap.release()

            if not ret:
                print("Error al capturar la imagen")
                continue
                
            # Realizar el reconocimiento facial
            usuario_reconocido = reconocimiento_facial(frame)
            # Ejemplo de uso
                
            if usuario_reconocido:
                # Usuario reconocido, encender LED verde
                # Usuario desconocido, encender LED rojo y hacer sonar el buzzer (2 pitidos largos)
                GPIO.output(GPIO_BUZZER, GPIO.HIGH)
                time.sleep(0.25)
                GPIO.output(GPIO_BUZZER, GPIO.LOW)
                time.sleep(0.25)
                GPIO.output(GPIO_BUZZER, GPIO.HIGH)
                time.sleep(0.25)
                GPIO.output(GPIO_BUZZER, GPIO.LOW)
            else:
                # Usuario desconocido, encender LED rojo y hacer sonar el buzzer (2 pitidos largos)
                GPIO.output(GPIO_BUZZER, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(GPIO_BUZZER, GPIO.LOW)
                time.sleep(0.5)
                GPIO.output(GPIO_BUZZER, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(GPIO_BUZZER, GPIO.LOW)

        #deternme aqui 
        else:
            # Nadie cerca, mantener el sistema en espera (LED amarillo encendido)
            print("esperando")
        time.sleep(1)

# Limpiar GPIO en caso de interrupción
except KeyboardInterrupt:
    print("Medición detenida por el usuario")
    GPIO.cleanup()
