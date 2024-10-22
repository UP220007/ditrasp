# # Importar librerías
# import RPi.GPIO as GPIO
# import time
# import cv2
# import os
# from datetime import datetime
# import Adafruit_DHT
# import socket

# # Create a UDP socket
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# # Define the server address and port
# server_address = ('192.168.1.120', 8888)

# # Función para reiniciar pines y evitar conflictos
# def reiniciar_pines():
#     GPIO.cleanup()

# # Configuración de GPIO
# GPIO.setmode(GPIO.BCM)

# # Pin del sensor DHT11
# pin_sensor = 4
# # Función para leer la temperatura del sensor DHT11
# def leer_temperatura():
#     humedad, temperatura = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, pin_sensor)
#     if humedad is not None and temperatura is not None:
#         return temperatura
#     else:
#         print("Error al leer el sensor DHT11")
#         return None
    
# while True:
#     # Get input from the user and send it to the server
#     message = input("Enter message: ")
#     if message == "temp":
#             # Leer temperatura
#             temperatura = leer_temperatura()
#             if temperatura:
#                 print(f"Temperatura ambiente: {temperatura:.1f}°C")
#     s.sendto(message.encode('utf-8'), server_address)


# Importar librerías
import RPi.GPIO as GPIO
import Adafruit_DHT
import socket

# Configurar el sensor DHT11 en el pin GPIO 4
pin_sensor = 4

# Crear un socket UDP para recibir comandos
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Dirección de la Raspberry Pi y puerto en el que escucha
raspberry_address = ('0.0.0.0', 8888)

# Asociar el socket con la dirección y puerto de la Raspberry Pi
s.bind(raspberry_address)

# Función para reiniciar los pines GPIO y evitar conflictos
def reiniciar_pines():
    GPIO.cleanup()

# Función para leer la temperatura del sensor DHT11
def leer_temperatura():
    humedad, temperatura = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, pin_sensor)
    if humedad is not None and temperatura is not None:
        return temperatura
    else:
        print("Error al leer el sensor DHT11")
        return None

try:
    print("Esperando comandos UDP...")
    while True:
        # Esperar a recibir un comando
        data, address = s.recvfrom(1024)  # Espera un mensaje de la computadora
        command = data.decode('utf-8')    # Decodificar el mensaje recibido
        print(f"Comando recibido de {address}: {command}")

        # Procesar el comando recibido
        if command == "temp":
            # Leer la temperatura
            temperatura = leer_temperatura()
            if temperatura is not None:
                # Enviar la temperatura de vuelta al cliente (computadora)
                response = f"Temperatura: {temperatura:.1f}°C"
                s.sendto(response.encode('utf-8'), address)
                print(f"Respuesta enviada a {address}: {response}")
            else:
                error_message = "Error al leer la temperatura"
                s.sendto(error_message.encode('utf-8'), address)
                print(f"Error enviado a {address}")
        else:
            # Responder si se recibe un comando desconocido
            error_message = "Comando no reconocido"
            s.sendto(error_message.encode('utf-8'), address)
            print(f"Comando desconocido recibido de {address}")

except KeyboardInterrupt:
    # Limpiar los pines GPIO al finalizar
    reiniciar_pines()

finally:
    # Cerrar el socket
    s.close()
