#segundo codigo formateado para funcionar con sensor ultrasonico 
# Libraries
import RPi.GPIO as GPIO
import time

# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

# Set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24

# Set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def distance():
    # Set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # Set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    startTime = time.time()
    stopTime = time.time()

    # Save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        startTime = time.time()

    # Save StopTime
    while GPIO.input(GPIO_ECHO) == 1:
        stopTime = time.time()

    # Time difference between start and arrival
    timeElapsed = stopTime - startTime
    # Multiply with the sonic speed (34300 cm/s) and divide by 2 (for there and back)
    distance = (timeElapsed * 34300) / 2

    return distance

if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print("Measured Distance = %.1f cm" % dist)
            time.sleep(1)

    # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
