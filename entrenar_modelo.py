import cv2
import os
import numpy as np

# Crear el reconocedor facial usando LBPH
face_recognizer = cv2.face.LBPHFaceRecognizer_create()

# Leer las imágenes capturadas
data_path = 'imagenes/'
people = os.listdir(data_path)

labels = []
faces_data = []
label = 0

for person in people:
    person_path = data_path + person

    for file_name in os.listdir(person_path):
        print(f"Entrenando con imagen {file_name}")
        image_path = person_path + '/' + file_name
        image = cv2.imread(image_path, 0)  # Cargar en escala de grises
        faces_data.append(image)
        labels.append(label)
    
    label += 1

# Entrenar el reconocedor con los datos de los rostros y sus etiquetas
face_recognizer.train(faces_data, np.array(labels))

# Guardar el modelo entrenado
face_recognizer.write('modelo_LBPH.xml')

# Guardar los nombres y sus etiquetas en un archivo
with open('nombres.txt', 'w') as f:
    for i, person in enumerate(people):
        f.write(f"{i},{person}\n")

print("Modelo entrenado y guardado con éxito.")
