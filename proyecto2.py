# Importar librerías
import RPi.GPIO as GPIO
import time
import cv2
import os
from datetime import datetime
import Adafruit_DHT

# Función para reiniciar pines y evitar conflictos
def reiniciar_pines():
    GPIO.cleanup()

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)

# Pines del sensor ultrasónico
GPIO_TRIGGER = 18
GPIO_ECHO = 24

# Pines del botón, buzzer y LEDs
GPIO_BUTTON = 17
GPIO_BUZZER = 22
GPIO_LED_GREEN = 27   # LED verde: usuario reconocido
GPIO_LED_RED = 23     # LED rojo: usuario desconocido
GPIO_LED_YELLOW = 25  # LED amarillo: sistema en espera

# Pin del sensor DHT11
pin_sensor = 4

# Reiniciar pines antes de usarlos para evitar conflictos
reiniciar_pines()

# Configuración de pines como salida o entrada
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_BUZZER, GPIO.OUT)
GPIO.setup(GPIO_LED_GREEN, GPIO.OUT)
GPIO.setup(GPIO_LED_RED, GPIO.OUT)
GPIO.setup(GPIO_LED_YELLOW, GPIO.OUT)

# Inicializar LEDs apagados
GPIO.output(GPIO_LED_GREEN, GPIO.LOW)
GPIO.output(GPIO_LED_RED, GPIO.LOW)
GPIO.output(GPIO_LED_YELLOW, GPIO.HIGH)  # LED amarillo encendido inicialmente

# Verificar si los archivos necesarios existen
if not os.path.exists('modelo_LBPH.xml'):
    raise FileNotFoundError("El archivo 'modelo_LBPH.xml' no se encontró.")
if not os.path.exists('nombres.txt'):
    raise FileNotFoundError("El archivo 'nombres.txt' no se encontró.")

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
def distance():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    startTime = time.time()
    stopTime = time.time()

    while GPIO.input(GPIO_ECHO) == 0:
        startTime = time.time()

    while GPIO.input(GPIO_ECHO) == 1:
        stopTime = time.time()

    timeElapsed = stopTime - startTime
    distance = (timeElapsed * 34300) / 2
    return distance

# Función para leer la temperatura del sensor DHT11
def leer_temperatura():
    humedad, temperatura = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, pin_sensor)
    if humedad is not None and temperatura is not None:
        return temperatura
    else:
        print("Error al leer el sensor DHT11")
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

            # Encender LED verde y hacer sonar el buzzer (2 pitidos cortos)
            GPIO.output(GPIO_LED_GREEN, GPIO.HIGH)
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
        # Medir la distancia
        dist = distance()
        print(f"Distancia medida: {dist:.1f} cm")
        
        # Si alguien está cerca (menos de 50 cm)
        if dist < 50:
            print("Persona detectada. Esperando botón para captura...")

            # Esperar a que se pulse el botón
            button_state = GPIO.input(GPIO_BUTTON)
            if button_state == GPIO.LOW:  # Si el botón está presionado
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
                
                if usuario_reconocido:
                    # Usuario reconocido, encender LED verde
                    GPIO.output(GPIO_LED_GREEN, GPIO.HIGH)
                    GPIO.output(GPIO_LED_RED, GPIO.LOW)
                else:
                    # Usuario desconocido, encender LED rojo y hacer sonar el buzzer (2 pitidos largos)
                    GPIO.output(GPIO_LED_RED, GPIO.HIGH)
                    GPIO.output(GPIO_LED_GREEN, GPIO.LOW)
                    GPIO.output(GPIO_BUZZER, GPIO.HIGH)
                    time.sleep(0.5)
                    GPIO.output(GPIO_BUZZER, GPIO.LOW)
                    time.sleep(0.5)
                    GPIO.output(GPIO_BUZZER, GPIO.HIGH)
                    time.sleep(0.5)
                    GPIO.output(GPIO_BUZZER, GPIO.LOW)

                # Apagar todos los LEDs después de 2 segundos
                time.sleep(2)
                GPIO.output(GPIO_LED_GREEN, GPIO.LOW)
                GPIO.output(GPIO_LED_RED, GPIO.LOW)
                GPIO.output(GPIO_LED_YELLOW, GPIO.HIGH)  # Volver al estado de espera
        else:
            # Nadie cerca, mantener el sistema en espera (LED amarillo encendido)
            GPIO.output(GPIO_LED_GREEN, GPIO.LOW)
            GPIO.output(GPIO_LED_RED, GPIO.LOW)
            GPIO.output(GPIO_LED_YELLOW, GPIO.HIGH)

        time.sleep(1)

# Limpiar GPIO en caso de interrupción
except KeyboardInterrupt:
    print("Medición detenida por el usuario")
    reiniciar_pines()
