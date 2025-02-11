import asyncio
from bleak import BleakClient

# 1: 0B95303D-D096-EA9E-48E0-75059113EA47
# 2: F06E54A8-4E0E-D456-1D3E-BD2FC4CA4B41
# 3: 6BA09D3D-3AE0-9AC2-64DB-109ACF01FC21
# C: B3B439D5-0EA0-1CD2-5BD3-F1D07F419E8B

BLE_ADDRESS = "0B95303D-D096-EA9E-48E0-75059113EA47"
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-123456789abc"

async def monitor_connection(client):
    while True:
        try:
            if await client.is_connected():
                print("Connection is active.")
            else:
                print("Connection lost.")
                break
        except Exception as e:
            print(f"Error monitoring connection: {e}")
            break
        await asyncio.sleep(5)  # Check connection every 5 seconds

async def esp_communication():
    try:
        async with BleakClient(BLE_ADDRESS) as client:
            print(f"Attempting to connect to {BLE_ADDRESS}...")
            if await client.is_connected():
                print(f"Connected to {BLE_ADDRESS}")
                # Start monitoring connection
                asyncio.create_task(monitor_connection(client))

                while True:
                    state = input("Enter '1' to enable blinking or '0' to disable blinking: ").strip()
                    if state in ["1", "0"]:
                        await client.write_gatt_char(CHARACTERISTIC_UUID, state.encode())
                        print(f"Command '{state}' sent successfully!")
                    else:
                        print("Invalid input. Please enter '1' or '0'.")
                    # state = "1"
                    # await client.write_gatt_char(CHARACTERISTIC_UUID, state.encode())
                    # state = "0"
                    # await client.write_gatt_char(CHARACTERISTIC_UUID, state.encode())
                    # #     print(f"Command '{state}' sent successfully!")
            else:
                print("Failed to connect.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(esp_communication())
