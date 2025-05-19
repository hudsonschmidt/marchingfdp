import socket
import sys
import termios
import tty
import time

# 35.307628
# -120.658569

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

def splitGPS(lat, long):
    for i in range(0,4):
        pass

if __name__ == "__main__":
    print("Enter command: (q to quit)")
    while True:
        pin_choice = get_char().strip()
        print(f"You entered: {pin_choice}")
        # FORMAT: "ROW:COL:LAT:LONG"

        # GPS Option 1()
        if pin_choice == "a":
            send_message("0;5:1")
            send_message("1;5:1")
            send_message("2;5:1")
            

        # Emergency STOP ----------------------------
        elif pin_choice == "z":
            send_message("0;5:0")
            send_message("1;5:0")
            send_message("2;5:0")

        # BREAK -----------------------------------
        elif pin_choice == "q":
            break
        else:
            print("Invalid pin selection.")
