import cv2
import os
from datetime import datetime

# Cargar el modelo previamente entrenado
face_recognizer = cv2.face.LBPHFaceRecognizer_create()
face_recognizer.read('modelo_LBPH.xml')

# Verificar la versión de OpenCV
opencv_version = cv2.__version__

# Determinar la ruta del Haar Cascade según la versión de OpenCV
if int(opencv_version.split('.')[0]) >= 4 and hasattr(cv2, 'data'):
    haar_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
else:
    haar_cascade_path = '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'

# Verificar si el archivo Haar Cascade existe
if not os.path.exists(haar_cascade_path):
    raise FileNotFoundError(f"No se encontró el archivo Haar Cascade en {haar_cascade_path}")

# Cargar el Haar Cascade para detección de rostros
face_cascade = cv2.CascadeClassifier(haar_cascade_path)

# Cargar los nombres desde el archivo
people = {}
with open('nombres.txt', 'r') as f:
    for line in f.readlines():
        label, name = line.strip().split(',')
        people[int(label)] = name

# Iniciar la cámara
camara = "http://192.168.1.100:8080/video"  # Cambia esta URL si es necesario
cap = cv2.VideoCapture(camara)

# Capturar una imagen
ret, frame = cap.read()
if not ret:
    print("Error: No se pudo leer el frame.")
else:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        print("No se detectó ningún rostro.")
    else:
        for (x, y, w, h) in faces:
            rostro = gray[y:y+h, x:x+w]
            rostro = cv2.resize(rostro, (200, 200))

            # Intentar reconocer el rostro
            label, confidence = face_recognizer.predict(rostro)

            # Mostrar el nombre de la persona si se reconoce con confianza suficiente
            if confidence < 70:
                nombre = people[label]
                print(f"¡Bienvenido, {nombre}! Con confianza: {confidence:.2f}")

                # Ajustar las coordenadas para incluir el área de los hombros
                margen_hombros = int(h * 1.5)  # Aumenta la altura a 1.5 veces la altura del rostro
                x_margen = max(x - 20, 0)  # Ajustar horizontalmente con un margen
                y_margen = max(y - int(margen_hombros * 0.5), 0)  # Ajustar verticalmente

                # Guardar el área incluyendo los hombros
                imagen_area = frame[y_margen:y_margen + margen_hombros, x_margen:x_margen + w + 40]

                # Guardar la imagen
                ahora = datetime.now()
                fecha = ahora.strftime("%Y-%m-%d")
                hora = ahora.strftime("%H-%M-%S")
                folder_path = os.path.join('entradas', fecha)

                # Crear la carpeta si no existe
                os.makedirs(folder_path, exist_ok=True)

                # Guardar la imagen con el nombre del usuario
                image_path = os.path.join(folder_path, f"{nombre}_{hora}.jpg")
                cv2.imwrite(image_path, imagen_area)
            else:
                print("Desconocido con confianza: {:.2f}".format(confidence))

# Liberar la cámara y cerrar las ventanas
cap.release()
cv2.destroyAllWindows()
