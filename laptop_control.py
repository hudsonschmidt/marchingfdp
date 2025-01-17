import asyncio
from bleak import BleakClient, BleakScanner

# UUIDs for BLE communication
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"  # Replace with ESP32 BLE service UUID
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"  # Replace with characteristic UUID

# Motor control command
MOTOR_COMMAND = "ACTIVATE_MOTOR"

async def connect_and_send(address):
    async with BleakClient(address) as client:
        print(f"Connected to {address}")

        # Send motor control command
        await client.write_gatt_char(CHARACTERISTIC_UUID, MOTOR_COMMAND.encode())
        print(f"Sent command: {MOTOR_COMMAND}")

        # Wait for acknowledgment (if implemented on ESP32)
        response = await client.read_gatt_char(CHARACTERISTIC_UUID)
        print(f"Response from ESP32: {response.decode()}")

async def main():
    print("Scanning for devices...")
    devices = await BleakScanner.discover()

    # Display discovered devices
    for i, device in enumerate(devices):
        print(f"{i}: {device.name} ({device.address})")

    # Prompt user to select device
    choice = int(input("Select the device number to connect: "))
    address = devices[choice].address

    # Connect to the selected device
    await connect_and_send(address)

# Run the BLE communication script
asyncio.run(main())
