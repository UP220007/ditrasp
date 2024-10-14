import Adafruit_DHT
import time

sensor = Adafruit_DHT.DHT11
pin_sensor = 4
while True:
    # Este es el comando de la librería para leer del sensor
    humedad, temperatura = Adafruit_DHT.read_retry(sensor, pin_sensor)
    # Si hay valores del sensor (por que aveces puede no mandar nada si se lee muy seguido) los imprime en pantalla para saber a qué temperatura estamos
    if humedad is not None and temperatura is not None:
        print('Temp={0:0.1f}*C  humedad={1:0.1f}%'.format(temperatura, humedad))
    else:
        print('Hubo un fallo al leer del sensor. Intentalo de nuevo!')
    time.sleep(2)
    GPIO.cleanup()