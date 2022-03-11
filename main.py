import RPi.GPIO as GPIO
import sys
import time
import socket
from gpiozero import LED

s = socket.socket()
port = 4444
address = "169.254.242.78"

s.bind((address, port))
print("Socket created at ip " + address)

sensor_trig = 18
sensor_echo = 24
led1 = LED(22)

GPIO.setmode(GPIO.BCM)

GPIO.setup(sensor_trig, GPIO.OUT)
GPIO.setup(sensor_echo, GPIO.IN)


def get_distance():
    # turn on/off the sensor trigger
    GPIO.output(sensor_trig, True)
    GPIO.output(sensor_trig, False)

    # Save the start and stop time  to current time
    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(sensor_echo) == 0:
        start_time = time.time()

    while GPIO.input(sensor_echo) == 1:
        stop_time = time.time()

    total_time = stop_time - start_time
    # Operation to get the distance in cm between the sensor and the object
    distance = (total_time * 34300) / 2  # sonic speed= 34300 cm/s

    return distance


if __name__ == '__main__':
    s.listen(1)
    print("Waiting for a connection");
    connection, client_address = s.accept()
    print("Connection from", client_address)
    try:
        while True:
            data = connection.recv(1024).decode('utf-8')
            print("Received {!r}".format(data))
            if data == "distance":
                dist = get_distance()
                print("Sending the distance of the sensor back to the client. Value is: " + str(dist) + ".")
                connection.sendall(str(dist).encode('utf-8'))
            elif data == "ledon":
                print("Setting led to ON")
                led1.on()
            elif data == "ledoff":
                print("Setting led to OFF")
                led1.off()
            elif data == "exit":
                break;
            else:
                print("Ignoring message")

            data = ""
    finally:
        print("Closing connection")
        connection.close()
        sys.exit()
