from machine import Pin
from time import sleep
import bluetooth

# Motor setup
MOTOR_PIN = 2  # GPIO pin connected to the motor
motor = Pin(MOTOR_PIN, Pin.OUT)

# BLE setup
ble = bluetooth.BLE()
ble.active(True)

# UUIDs for BLE communication
SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"  # Replace with ESP32 BLE service UUID
CHARACTERISTIC_UUID = "abcdef01-1234-5678-1234-56789abcdef0"  # Replace with characteristic UUID

# BLE service and characteristic
service = (SERVICE_UUID, (CHARACTERISTIC_UUID,))
services = (service,)
ble.gatts_register_services(services)

def motor_control(command):
    if command == "ACTIVATE_MOTOR":
        print("Activating motor...")
        motor.on()
        sleep(1)  # Motor stays on for 1 second
        motor.off()
    else:
        print(f"Unknown command: {command}")

def ble_callback(event, data):
    if event == bluetooth._IRQ_GATTS_WRITE:
        conn_handle, attr_handle = data
        command = ble.gatts_read(attr_handle).decode()
        print(f"Received command: {command}")
        motor_control(command)

# Register BLE callback
ble.irq(ble_callback)

# Advertise the BLE service
ble.gap_advertise(100, b"\x02\x01\x06" + bytes(SERVICE_UUID, 'utf-8'))
print("BLE service is running...")

while True:
    pass
