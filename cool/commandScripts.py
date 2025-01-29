import serial
import time

arduino = serial.Serial(port = "COM6", baudrate=9600,timeout = 1)

def send_command(command):
    arduino.write(command.encode())
    time.sleep(0.1)
    response = arduino.readline().decode().strip()  
    return response

for i in range(5):
    print("Turning LED ON")
    send_command('1')
    time.sleep(.5)
    print("Turning LED OFF")
    send_command('0')
    time.sleep(.05)