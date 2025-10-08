import socket
import json
import threading
import time
from datetime import datetime
import random

HOST = "192.168.21.75"  # Serverns IP (ändrad till lärarens IP)
PORT = 5000             # Porten enligt ditt exempel (ändra om läraren säger annat)

LED_STATE = False  # Placeholder för LED

def handle_command(msg):
    global LED_STATE
    command = msg.get("command", "")
    if command == "LED_ON":
        LED_STATE = True
        print("[CLIENT] LED tänd (simulerad)")
    elif command == "LED_OFF":
        LED_STATE = False
        print("[CLIENT] LED släckt (simulerad)")
    else:
        print("[CLIENT] Okänt kommando:", command)

def listen_server(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            msg = json.loads(data.decode())
            handle_command(msg)
        except Exception as e:
            print("[CLIENT] Lyssnar: fel", e)
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    print(f"[CLIENT] Ansluten till servern på {HOST}:{PORT}")

    # Starta bakgrundstråd för att lyssna på servern
    threading.Thread(target=listen_server, args=(client,), daemon=True).start()

    try:
        while True:
            # Simulerade sensorvärden
            temperature = 20.0 + random.uniform(-2.0, 2.0)
            humidity = 40.0 + random.uniform(-5.0, 5.0)

            message = {
                "client_ip": "BBG_VIRTUAL",
                "timestamp": datetime.now().isoformat(),
                "temperature": temperature,
                "humidity": humidity,
                "led_state": LED_STATE
            }

            client.sendall(json.dumps(message).encode())
            print("[CLIENT] Skickade sensorvärden:", message)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n[CLIENT] Avslutar...")
    finally:
        client.close()

if __name__ == "__main__":
    main()
