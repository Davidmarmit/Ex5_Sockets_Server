import RPi.GPIO as GPIO
import sys
import time
import socket
from gpiozero import LED

# We setp the socket connection, with its address and port
s = socket.socket()
port = 4444
address = "169.254.242.78"

# We bind the address with the port
s.bind((address, port))
print("Socket created at ip " + address)

# Setting the pins for the led and HC-SR04
sensor_trig = 18
sensor_echo = 24
led1 = LED(22)

GPIO.setmode(GPIO.BCM)

GPIO.setup(sensor_trig, GPIO.OUT)
GPIO.setup(sensor_echo, GPIO.IN)


# Definition of function that gets the distance from the HC-SR04 and returns it
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

# Main function
if __name__ == '__main__':
    # We set the socket into listen mode for new connections
    s.listen(1)
    print("Waiting for a connection")
    # We wait for a connection to happen, this function blocks the code from running past this line
    connection, client_address = s.accept()
    # From here, a connection has been set, we know the client address.
    print("Connection from", client_address)
    try:
        while True:
            # We receive the message from the client and execute the option received
            data = connection.recv(1024).decode('utf-8')
            print("Received {!r}".format(data))
            # If the action requested is distance, we get the distance measured from the HC-SR04
            if data == "distance":
                dist = get_distance()
                print("Sending the distance of the sensor back to the client. Value is: " + str(dist) + ".")
                connection.sendall(str(dist).encode('utf-8'))
            # If the action requested is ledon, we light up the led
            elif data == "ledon":
                print("Setting led to ON")
                led1.on()
            # If the action requested is ledoff, we light up the led
            elif data == "ledoff":
                print("Setting led to OFF")
                led1.off()
            elif data == "exit":
                break
            # If the requested action doesn't match with any defined ones, we ignore the message.
            else:
                print("Ignoring message")
            # We reset the data string, waiting for the new request
            data = ""
    finally:
        # We close the connection when the user requests the exit command
        print("Closing connection")
        connection.close()
        sys.exit()
