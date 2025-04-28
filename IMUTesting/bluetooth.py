import bluetooth
import time

def connect_to_esp32(target_name):
    target_address = None

    # Search for nearby devices
    print("Searching for devices...")
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True)

    for addr, name in nearby_devices:
        print(f"Found device: {name} - {addr}")
        if target_name == name:
            target_address = addr
            break

    if target_address is None:
        print(f"Could not find target device: {target_name}")
        return None

    print(f"Connecting to {target_name} at {target_address}...")
    try:
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((target_address, 1))
        print("Connected successfully!")
        return sock
    except bluetooth.BluetoothError as e:
        print(f"Failed to connect: {e}")
        return None

if __name__ == "__main__":
    esp32_name = "ESP32_DEVKIT"  # Replace with your ESP32's Bluetooth name
    connection = connect_to_esp32(esp32_name)

    if connection:
        try:
            # Example: Send a message to the ESP32
            connection.send("Hello ESP32!")
            print("Message sent!")
            time.sleep(2)
        finally:
            connection.close()
            print("Connection closed.")