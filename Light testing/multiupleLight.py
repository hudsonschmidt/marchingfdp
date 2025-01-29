import asyncio
from bleak import BleakClient

# List all of your BLE addresses here
BLE_ADDRESSES = [
    "0B95303D-D096-EA9E-48E0-75059113EA47",
    "F06E54A8-4E0E-D456-1D3E-BD2FC4CA4B41",
    "6BA09D3D-3AE0-9AC2-64DB-109ACF01FC21",
]

CHARACTERISTIC_UUID = "87654321-4321-4321-4321-123456789abc"

async def monitor_connection(client):
    """
    Periodically check if the client is still connected.
    """
    while True:
        try:
            if await client.is_connected():
                print(f"[{client.address}] Connection is active.")
            else:
                print(f"[{client.address}] Connection lost.")
                break
        except Exception as e:
            print(f"[{client.address}] Error monitoring connection: {e}")
            break
        await asyncio.sleep(5)  # Check connection every 5 seconds

async def connect_and_monitor(address):
    """
    Connect to a single ESP32 device and start monitoring.
    Return the BleakClient if successful, else return None.
    """
    print(f"Attempting to connect to {address}...")
    client = BleakClient(address)
    try:
        await client.connect()
        if await client.is_connected():
            print(f"[{address}] Connected.")
            # Start monitoring in the background
            asyncio.create_task(monitor_connection(client))
            return client
        else:
            print(f"[{address}] Failed to connect.")
    except Exception as e:
        print(f"[{address}] Connection error: {e}")
    return None

async def main():
    # Create tasks to connect to all addresses simultaneously
    clients = await asyncio.gather(*(connect_and_monitor(addr) for addr in BLE_ADDRESSES))
    # Filter out any that failed to connect (None)
    clients = [c for c in clients if c is not None]

    if not clients:
        print("No devices connected. Exiting.")
        return

    print("\nAll connection attempts completed. Enter commands below.")
    print("Type '1' to enable blinking, '0' to disable blinking, or 'q' to quit.\n")

    # Command loop (user input)
    while True:
        state = input("Enter command ('1', '0', or 'q' to quit): ").strip()
        if state.lower() == 'q':
            break
        if state not in ['1', '0']:
            print("Invalid input. Please enter '1', '0', or 'q' to quit.")
            continue

        # Send command to each connected client
        for client in clients:
            if await client.is_connected():
                try:
                    await client.write_gatt_char(CHARACTERISTIC_UUID, state.encode())
                    print(f"[{client.address}] Command '{state}' sent successfully.")
                except Exception as e:
                    print(f"[{client.address}] Failed to send command: {e}")
            else:
                print(f"[{client.address}] Not connected.")

    # Clean up: disconnect from devices
    for client in clients:
        print(f"Disconnecting from {client.address}")
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
