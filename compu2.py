from socket import *

# Crear un socket UDP
s = socket(AF_INET, SOCK_DGRAM)

# Dirección IP y puerto de la Raspberry Pi
raspberry_address = ('192.168.1.121', 8888)  # Cambia esta IP a la de tu Raspberry Pi

# Bucle para permitir múltiples comandos
while True:
    # Solicitar entrada de comando desde el teclado
    command = input("Ingresa un comando ('exit' para salir): ")

    # Si el usuario ingresa "exit", terminamos el bucle
    if command == "exit":
        print("Saliendo del programa.")
        break

    # Enviar el comando ingresado a la Raspberry Pi
    s.sendto(command.encode('utf-8'), raspberry_address)

    # Esperar la respuesta de la Raspberry Pi
    data, address = s.recvfrom(1024)  # Recibir la respuesta de la Raspberry Pi
    print(f"Respuesta de la Raspberry Pi: {data.decode('utf-8')}")

# Cerrar el socket al terminar
s.close()
