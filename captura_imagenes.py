import cv2
import os

# Crear la carpeta donde se almacenarán las imágenes
nombre = input("Introduce el nombre de la persona: ")
carpeta = f"imagenes/{nombre}"

# Crear la carpeta si no existe
if not os.path.exists(carpeta):
    os.makedirs(carpeta)

# Iniciar la captura de la cámara
camara = "http://192.168.1.100:8080/video"  # Cambia esta URL si es necesario
cap = cv2.VideoCapture(camara)

# Cargar el clasificador de caras
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
count = 0

while True:
    ret, frame = cap.read()  # Capturar un frame de la cámara
    
    if not ret:  # Comprobar si se capturó correctamente el frame
        print("No se pudo capturar el frame. Verifica la conexión de la cámara.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convertir a escala de grises
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)  # Detectar caras

    # Dibujar rectángulos alrededor de las caras detectadas
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)  # Dibujar el rectángulo
        rostro = frame[y:y+h, x:x+w]  # Extraer el rostro
        rostro = cv2.resize(rostro, (200, 200))  # Redimensionar el rostro
        cv2.imwrite(f"{carpeta}/rostro_{count}.jpg", rostro)  # Guardar el rostro
        count += 1  # Incrementar el contador de rostros guardados

    cv2.imshow("Capturando imagenes", frame)  # Mostrar el feed de video en tiempo real

    # Salir del bucle si se presiona 'q' o se han capturado 100 imágenes
    if cv2.waitKey(1) & 0xFF == ord('q') or count >= 100:
        break

# Liberar la cámara y cerrar todas las ventanas
cap.release()
cv2.destroyAllWindows()
