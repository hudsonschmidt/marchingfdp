import serial
import time

arduino = serial.Serial(port = "COM6", baudrate=9600,timeout = 1)

def send_command(command):
    arduino.write(command.encode())
    time.sleep(0.1)
    response = arduino.readline().decode().strip()  
    return response

for i in range(5):
    print("Turning buzz1 ON")
    send_command('1')
    time.sleep(.5)
    print("Turning buzz1 OFF")
    send_command('2')
    time.sleep(.05)
    print("Turning buzz2 ON")
    send_command('3')
    print("Turning buzz1 ON")
    send_command('1')
    time.sleep(.05)
    print("Turning buzz2 OFF")
    send_command('4')
    print("Turning buzz1 OFF")
    send_command('2')
    time.sleep(.05)
    