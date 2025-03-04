import socket
import asyncio
import sys
import termios
import tty
import time

def get_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        char = sys.stdin.read(1)  # Read a single character
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return char

def send_message(message, server_ip="192.168.4.1", server_port=80):
    try:
        # Create a TCP/IP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            print(f"Connecting to {server_ip}:{server_port}...")
            sock.connect((server_ip, server_port))
            print("Connected.")

            # Append newline to match the ESP32's readStringUntil('\n')
            full_message = message + "\n"
            sock.sendall(full_message.encode('utf-8'))
            print(f"Sent message: {message}")

            # Optionally, receive an acknowledgement from the ESP32
            response = sock.recv(1024)
            if response:
                print("Received response:", response.decode('utf-8'))
            else:
                print("No response received.")
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    print("Enter command: (p to quit)")
    while True:
        pin_choice = get_char().strip()
        print(f"You entered: {pin_choice}")
        # All (Pin 5 only) -------------------------------------
        if pin_choice == "a":
            send_message("0;5:1")
            send_message("1;5:1")
            send_message("2;5:1")
            time.sleep(0.3)
            send_message("0;5:0")
            send_message("1;5:0")
            send_message("2;5:0")

        # Timed by row (Pin 5 only) ----------------------------
        elif pin_choice == "s":
            # send_message("0;5:1")
            # time.sleep(0.3)
            # send_message("0;5:0")

            # time.sleep(0.7)

            send_message("1;5:1")
            time.sleep(0.3)
            send_message("1;5:0")

            time.sleep(0.7) 

            send_message("2;5:1")
            time.sleep(0.3) 
            send_message("2;5:0")

        # Row 0 only (Hub) ----------------------------
        elif pin_choice == "q":
            send_message("0;5:1")
            time.sleep(0.3)
            send_message("0;5:0")

        # Row 1 only ----------------------------
        elif pin_choice == "w":
            send_message("1;5:1")
            time.sleep(0.3)
            send_message("1;5:0")

        # Row 2 only ----------------------------
        elif pin_choice == "e":
            send_message("2;5:1")
            time.sleep(0.3)
            send_message("2;5:0")

        # Row 2 only (2 Buzz) ----------------------------
        elif pin_choice == "d":
            send_message("2;5:1")
            time.sleep(0.1)
            send_message("2;5:0")
            time.sleep(0.05)
            send_message("2;5:1")
            time.sleep(0.1)
            send_message("2;5:0")

        # Emergency STOP ----------------------------
        elif pin_choice == "z":
            send_message("0;5:0")
            send_message("1;5:0")
            send_message("2;5:0")

        # BREAK -----------------------------------
        elif pin_choice == "p":
            break
        else:
            print("Invalid pin selection.")
