# Importar librerías
import RPi.GPIO as GPIO
import Adafruit_DHT
import socket
import pymysql

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

# Función para conectarse a la base de datos MySQL
def conectar_db():
    return pymysql.connect(
        host='localhost',
        user='alquimista',      # Cambia esto por tu usuario
        password='RoyMustang',  # Cambia esto por tu contraseña
        database='sistenb',  # Cambia esto por tu base de datos
        cursorclass=pymysql.cursors.DictCursor
    )

# Función para formatear los datos en una tabla
def formatear_datos(datos):
    # Asume que las columnas son 'id', 'nombre' y 'valor', ajusta según tu tabla
    encabezado = f"{'ID':<5} {'Nombre':<20} {'Valor':<10}\n"
    tabla = encabezado + "-" * 40 + "\n"
    for dato in datos:
        fila = f"{dato['id']:<5} {dato['first_name']:<20}{dato['last_name']:<20} {dato['email']:<10}{dato['birth_date']:<20}{dato['enrollment_date']:<20}\n"
        tabla += fila
    return tabla

# Funciones CRUD para la base de datos
def crear_dato(nombre, valor):
    connection = conectar_db()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO students (nombre, valor) VALUES (%s, %s)"
            cursor.execute(sql, (nombre, valor))
        connection.commit()
    finally:
        connection.close()

def leer_datos():
    connection = conectar_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM students"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        connection.close()

def actualizar_dato(id, nuevo_valor):
    connection = conectar_db()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE students SET valor = %s WHERE id = %s"
            cursor.execute(sql, (nuevo_valor, id))
        connection.commit()
    finally:
        connection.close()

def eliminar_dato(id):
    connection = conectar_db()
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM students WHERE id = %s"
            cursor.execute(sql, (id,))
        connection.commit()
    finally:
        connection.close()

try:
    print("Esperando comandos UDP...")
    while True:
        # Esperar a recibir un comando
        data, address = s.recvfrom(1024)  # Espera un mensaje de la computadora
        command = data.decode('utf-8')    # Decodificar el mensaje recibido
        print(f"Comando recibido de {address}: {command}")

        # Procesar el comando recibido
        if command.startswith("temp"):
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
        elif command.startswith("crear"):
            _, nombre, valor = command.split()  # Se espera que el comando sea 'crear nombre valor'
            crear_dato(nombre, valor)
            s.sendto("Dato creado".encode('utf-8'), address)
        elif command.startswith("leer"):
            datos = leer_datos()
            tabla = formatear_datos(datos)  # Formatear los datos como una tabla
            s.sendto(tabla.encode('utf-8'), address)
        elif command.startswith("actualizar"):
            _, id, nuevo_valor = command.split()  # Se espera que el comando sea 'actualizar id nuevo_valor'
            actualizar_dato(int(id), nuevo_valor)
            s.sendto("Dato actualizado".encode('utf-8'), address)
        elif command.startswith("eliminar"):
            _, id = command.split()  # Se espera que el comando sea 'eliminar id'
            eliminar_dato(int(id))
            s.sendto("Dato eliminado".encode('utf-8'), address)
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
