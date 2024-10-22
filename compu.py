from socket import *

# Crear un socket UDP para enviar el comando y recibir la respuesta
s = socket(AF_INET, SOCK_DGRAM)

# Dirección IP y puerto de la Raspberry Pi
raspberry_address = ('192.168.1.120', 8888)  # Cambia esta IP a la de tu Raspberry Pi

# Comando a enviar ("temp" para obtener la temperatura)
command = "temp"

# Enviar el comando "temp" a la Raspberry Pi
s.sendto(command.encode('utf-8'), raspberry_address)

# Esperar la respuesta de la Raspberry Pi
data, address = s.recvfrom(1024)  # Recibe la respuesta
print(f"Respuesta de la Raspberry Pi: {data.decode('utf-8')}")

# Cerrar el socket
s.close()
