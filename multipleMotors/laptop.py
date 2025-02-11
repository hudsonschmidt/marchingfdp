import sys
import termios
import tty
import asyncio
from bleak import BleakClient

# "ONE": "0B95303D-D096-EA9E-48E0-75059113EA47"
# "TWO": "F06E54A8-4E0E-D456-1D3E-BD2FC4CA4B41"
# "THREE": "6BA09D3D-3AE0-9AC2-64DB-109ACF01FC21"

# Motor numbers and respective pins
MOTOR_ONE = 5
MOTOR_TWO = 19
MOTOR_THREE = 21
MOTOR_FOUR = 4

# Board numbers and respective BLE addresses
BLE_ADDRESSES = {
    "ONE": "0B95303D-D096-EA9E-48E0-75059113EA47",
    "TWO": "F06E54A8-4E0E-D456-1D3E-BD2FC4CA4B41"
}

# Characteristic ID
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-123456789abc"

clients = {}

def get_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        char = sys.stdin.read(1)  # Read a single character
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return char

# Connects to all boards in dictionary
async def connect():
    global clients
    clients = {}
    for name, addr in BLE_ADDRESSES.items():
        try:
            client = BleakClient(addr)
            await client.connect()
            if await client.is_connected():
                print(f"Connected to {name} ({addr})")
                clients[name] = client
            else:
                print(f"Failed to connect to {name} ({addr})")
        except Exception as e:
            print(f"Error connecting to {name} ({addr}): {e}")
    
    return len(clients) > 0

# Monitors connection and reconnects if connection is lost
async def monitor():
    global clients
    while True:
        for name, client in list(clients.items()):
            try:
                if not await client.is_connected():
                    print(f"Lost connection to {name}. Reconnecting...")
                    await client.connect()
            except Exception as e:
                print(f"Error monitoring {name}: {e}")
        await asyncio.sleep(5)

# Send command to board
async def send(board_name, selected_pin, command):
    global clients
    if board_name in clients:
        client = clients[board_name]
        if await client.is_connected():
            try:
                command_str = f"{selected_pin}:{command}".encode('utf-8')
                await client.write_gatt_char(CHARACTERISTIC_UUID, command_str)
                print(f"Sent command to {board_name}: {selected_pin}:{command}")
            except Exception as e:
                print(f"Error sending command to {board_name}: {e}")
        else:
            print(f"Not connected to {board_name}")
    else:
        print(f"No client found for {board_name}")

async def main():
    if not await connect():
        print("No devices connected. Exiting.")
        return
    asyncio.create_task(monitor())
    
    while True:
        pin_choice = get_char().strip()
        print(f"You entered: {pin_choice}")
        # BOARD 1 ---------------------------------
        if pin_choice == "a":
            await send("ONE", MOTOR_ONE, 1)
            await asyncio.sleep(0.5)
            await send("ONE", MOTOR_ONE, 0)
        elif pin_choice == "d":
            await send("ONE", MOTOR_TWO, 1)
            await asyncio.sleep(0.5)
            await send("ONE", MOTOR_TWO, 0)
        # BOARD 2 ---------------------------------
        elif pin_choice == "h":
            await send("TWO", MOTOR_ONE, 1)
            await asyncio.sleep(0.5)
            await send("TWO", MOTOR_ONE, 0)
        elif pin_choice == "j":
            await send("TWO", MOTOR_TWO, 1)
            await asyncio.sleep(0.5)
            await send("TWO", MOTOR_TWO, 0)
        elif pin_choice == "k":
            await send("TWO", MOTOR_THREE, 1)
            await asyncio.sleep(0.5)
            await send("TWO", MOTOR_THREE, 0)
        elif pin_choice == "l":
            await send("TWO", MOTOR_FOUR, 1)
            await asyncio.sleep(0.5)
            await send("TWO", MOTOR_FOUR, 0)
        else:
            print("Invalid pin selection.")

if __name__ == "__main__":
    asyncio.run(main())
