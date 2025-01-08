from machine import Pin, UART
from bluetooth import BLE

# BLE Service and Characteristic UUIDs
SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHARACTERISTIC_UUID = "abcdef01-1234-5678-1234-56789abcdef0"

# BLE Initialization
ble = BLE()
ble.active(True)

# UART for debugging
uart = UART(1, baudrate=115200, tx=17, rx=16)
uart.write("BLE Server Starting\n")

# Define BLE callbacks
def on_write(handle, data):
    global ble
    uart.write(f"Data received: {data.decode()}\n")
    if data.decode() == "ACTIVATE_MOTOR":
        activate_motor()
        # Send acknowledgment
        ble.gatt_server_write(handle, b"Motor Activated")

# Function to activate the motor
def activate_motor():
    uart.write("Motor Activated!\n")
    motor_pin = Pin(2, Pin.OUT)
    motor_pin.on()
    time.sleep(1)
    motor_pin.off()

# Advertise BLE Service
def advertise():
    uart.write("Advertising BLE service...\n")
    ble.gap_advertise(100, b'\x02\x01\x06' + b'\x03\x03' + bytes.fromhex(SERVICE_UUID.replace('-', '')))

# Set up GATT server
ble.gatt_server_register_service({
    "uuid": SERVICE_UUID,
    "characteristics": [
        {
            "uuid": CHARACTERISTIC_UUID,
            "properties": 0x08,  # Write property
            "permissions": 0x01,  # Readable
            "on_write": on_write,
        },
    ],
})

advertise()
