import socket

# Create a UDP socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Define the server address and port
server_address = ('192.168.1.120', 8888)

while True:
    # Get input from the user and send it to the server
    message = input("Enter message: ")
    s.sendto(message.encode('utf-8'), server_address)
