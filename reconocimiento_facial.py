import cv2
import matplotlib.pyplot as plt
import os

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

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: No se pudo leer el frame.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        rostro = gray[y:y+h, x:x+w]
        rostro = cv2.resize(rostro, (200, 200))

        # Intentar reconocer el rostro
        label, confidence = face_recognizer.predict(rostro)

        # Mostrar el nombre de la persona si se reconoce con confianza suficiente
        if confidence < 70:
            print(f"Reconocido: {people[label]} con confianza: {confidence:.2f}")
            cv2.putText(frame, f"{people[label]} ({confidence:.2f})", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            print(f"Desconocido con confianza: {confidence:.2f}")
            cv2.putText(frame, "Desconocido", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # Mostrar el video con las detecciones usando Matplotlib
    plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    plt.axis('off')  # Ocultar ejes
    plt.pause(0.001)  # Breve pausa para permitir la visualización
    plt.clf()  # Limpiar la figura para la siguiente iteración

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
