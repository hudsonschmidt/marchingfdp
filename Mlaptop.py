import socket
import keyboard
import time

def send_message(message, server_ip="192.168.4.1", server_port=80):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            print(f"Connecting to {server_ip}:{server_port}...")
            sock.settimeout(5)  # Set 5 seconds timeout
            sock.connect((server_ip, server_port))
            print("Connected.")

            full_message= message + "\n"
            sock.sendall(full_message.encode('utf-8'))
            print(f"Sent message: {message}")

            # WAIT for a response
            response = sock.recv(1024)
            if response:
                print("Received response:", response.decode('utf-8').strip())
            else:
                print("No response received.")
    except Exception as e:
        print("An error occurred:", e)


if __name__ == "__main__":
    print("Enter command: (p to quit)")
    while True:
        if keyboard.is_pressed("1"):
            send_message("1")

        # BREAK -----------------------------------
        elif keyboard.is_pressed("p"):
            break
        # else:
        #     print("Invalid pin selection.")
