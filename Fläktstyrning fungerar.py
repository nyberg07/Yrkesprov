import socket
import json
import time
import gpiod
from datetime import datetime

SERVER_IP = '192.168.21.75'
SERVER_PORT = 5000

def setup_gpio():
    chip = gpiod.Chip('gpiochip0')
    line = chip.get_line(4)  # GPIO4 (använd den pin som behövs)
    line.request(consumer='fan_control', type=gpiod.LINE_REQ_DIR_OUT)
    return line

def read_temperature():
    # Simulerad temperatur, ersätt med riktig sensorläsning
    return 22.0

def read_humidity():
    # Simulerad fuktighet, ersätt med riktig sensorläsning
    return 40.0

def main():
    fan_line = setup_gpio()
    fan_line.set_value(0)  # Fläkten av från start
    fan_state = False

    while True:
        try:
            print(f"[CLIENT] Försöker ansluta till servern {SERVER_IP}:{SERVER_PORT}...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((SERVER_IP, SERVER_PORT))
                print("[CLIENT] Ansluten till servern")

                while True:
                    # Skicka sensorvärden
                    message = {
                        "client_ip": "BBG_VIRTUAL",
                        "timestamp": datetime.now().isoformat(),
                        "temperature": read_temperature(),
                        "humidity": read_humidity(),
                        "fan_state": fan_state
                    }
                    client.sendall(json.dumps(message).encode())
                    print(f"[CLIENT] Skickade sensorvärden: {message}")

                    # Ta emot kommando från servern
                    try:
                        client.settimeout(1)  # 1 sek timeout på recv
                        data = client.recv(1024)
                        if data:
                            msg = data.decode()
                            print(f"[CLIENT] Mottaget kommando: {msg}")

                            try:
                                cmd = json.loads(msg)
                                command = cmd.get("command", "").upper()
                                pin = cmd.get("pin", "")

                                if command == "LED_ON" and pin == "P9_12":
                                    if not fan_state:
                                        fan_line.set_value(1)
                                        fan_state = True
                                        print("[CLIENT] Fläkten TÄND (GPIO4)")
                                    else:
                                        print("[CLIENT] Fläkten är redan TÄND")
                                elif command == "LED_OFF" and pin == "P9_12":
                                    if fan_state:
                                        fan_line.set_value(0)
                                        fan_state = False
                                        print("[CLIENT] Fläkten SLÄCK (GPIO4)")
                                    else:
                                        print("[CLIENT] Fläkten är redan SLÄCK")
                                else:
                                    print(f"[CLIENT] Okänt kommando eller pin: {msg}")
                            except json.JSONDecodeError:
                                print("[CLIENT] Kunde inte tolka kommandot som JSON")

                    except socket.timeout:
                        # Ingen data mottagen, fortsätt skicka sensorvärden
                        pass

                    time.sleep(5)

        except (ConnectionRefusedError, TimeoutError) as e:
            print(f"[CLIENT] Anslutningsfel eller server stängde anslutning: {e}")
            print("[CLIENT] Försöker återansluta om 5 sekunder...")
            time.sleep(5)
        except KeyboardInterrupt:
            print("[CLIENT] Avslutar...")
            break

if __name__ == "__main__":
    main()

