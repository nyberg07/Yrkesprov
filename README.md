# Yrkesprov

logga in på ssh med: ssh debian@192.168.7.2
skriv: By8Hq2Ze

Steg 1: Förbered BeagleBone Green
1.1 Material du behöver:

BeagleBone Green (BBG) med Debian Linux installerat.

SHT35-sensor (temperatur och fuktighet).

Kablar:

Röd (VCC)

Svart (GND)

Gul (SDA)

Vit (SCL)

1.2 Uppdatera systemet:

Öppna terminalen och kör följande kommandon för att uppdatera alla paket:
sudo apt update
sudo apt upgrade
sudo apt full-upgrade

1.3 Installera nödvändiga paket:

För att läsa data från sensorn via I2C och använda Python, installera följande:
sudo apt install python3-pip
sudo pip3 install smbus2
sudo apt install python3-smbus

Steg 2: Koppla SHT35-sensorn till BeagleBone Green
2.1 Koppla SHT35-sensorn:

Koppla SHT35-sensorn till BeagleBone Green enligt följande pin-konfiguration:

Sensor kabel	BeagleBone Green pin	Kommentar
Röd (VCC)	P9_3 (3.3V)	Strömförsörjning
Svart (GND)	P9_1 (GND)	Jord
Gul (SDA)	P9_18 (I2C2 SDA)	I2C Data
Vit (SCL)	P9_17 (I2C2 SCL)	I2C Clock

sudo config-pin P9_17 i2c
sudo config-pin P9_18 i2c

3.1 Kontrollera att sensorn är ansluten via I2C

För att kontrollera om sensorn är korrekt ansluten, använd i2cdetect:

För I2C-buss 2 (den vanliga på BeagleBone Green):

sudo i2cdetect -y 2

Om sensorn är korrekt ansluten bör du se en adress (t.ex. 0x44 eller 0x45) på tabellen.

Steg 4: Installera och Testa med Python
4.1 Skapa ett Python-skript för att läsa från SHT35:

Skapa ett Python-skript för att läsa temperatur och fuktighet från sensorn via I2C:


import smbus2
import time

SHT35_ADDR = 0x44  # SHT35 sensorens I2C-adress
CMD_MEASURE = [0x24, 0x00]  # Kommando för mätning

# Anslut till I2C-buss 2
bus = smbus2.SMBus(2)  # För I2C-buss 2 (ändra till 0 om du använder I2C-buss 0)

# Skriv kommando till sensorn
bus.write_i2c_block_data(SHT35_ADDR, CMD_MEASURE[0], [CMD_MEASURE[1]])

time.sleep(0.015)  # Vänta på att mätningen slutförs

# Läs data från sensorn
data = bus.read_i2c_block_data(SHT35_ADDR, 0, 6)
temp_raw = data[0] << 8 | data[1]
humidity_raw = data[3] << 8 | data[4]

temperature = -45 + (175 * temp_raw / 65535.0)
humidity = 100 * humidity_raw / 65535.0

print(f"Temperatur: {temperature:.2f} °C, Luftfuktighet: {humidity:.2f} %")

bus.close()



4.2 Kör Python-skriptet:

Spara skriptet som test_sht35.py och kör det med:

sudo python3 test_sht35.py


Om sensorn fungerar korrekt bör du få temperatur- och luftfuktighetsvärden som utskrift.

Steg 5: Skapa TCP-klient för att skicka data till server
5.1 Skapa TCP-klientskriptet:

Skapa filen tcp_client.py som ska läsa från SHT35-sensorn och skicka dessa data till servern via TCP:


import socket
import json
import time
import smbus2
from datetime import datetime

SERVER_IP = '192.168.21.75'  # Serverns IP
SERVER_PORT = 5000

SHT35_ADDR = 0x44  # SHT35 sensorens I2C-adress
CMD_MEASURE = [0x24, 0x00]

def read_temperature_and_humidity():
    bus = smbus2.SMBus(2)
    bus.write_i2c_block_data(SHT35_ADDR, CMD_MEASURE[0], [CMD_MEASURE[1]])
    time.sleep(0.015)
    data = bus.read_i2c_block_data(SHT35_ADDR, 0, 6)
    temp_raw = data[0] << 8 | data[1]
    humidity_raw = data[3] << 8 | data[4]

    temperature = -45 + (175 * temp_raw / 65535.0)
    humidity = 100 * humidity_raw / 65535.0
    bus.close()

    return temperature, humidity

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, SERVER_PORT))
    print(f"[CLIENT] Ansluten till servern på {SERVER_IP}:{SERVER_PORT}")

    while True:
        temperature, humidity = read_temperature_and_humidity()
        message = {
            "client_ip": "BBG_VIRTUAL",
            "timestamp": datetime.now().isoformat(),
            "temperature": temperature,
            "humidity": humidity
        }

        client.sendall(json.dumps(message).encode())
        print(f"[CLIENT] Skickade sensorvärden: {message}")
        time.sleep(5)

if __name__ == "__main__":
    main()


5.2 Kör TCP-klienten:

För att köra klienten och skicka sensorvärden till servern, kör:
sudo python3 tcp_client.py


Servern kommer nu att ta emot de kontinuerligt skickade sensorvärdena.

Steg 6: Felsökning

Om sensorn inte syns i i2cdetect eller om Python-skriptet inte fungerar:

Kontrollera kablarna: Dubbelkolla att kablarna är ordentligt anslutna till både sensorn och BeagleBone.

Kör om i2cdetect efter att ha aktiverat I2C-pinnarna med config-pin.

Kontrollera systemloggarna: Kör dmesg | grep i2c för att få information om eventuella I2C-fel.

Byt plats på SDA och SCL: Testa att byta kablarna för SDA och SCL.

Testa med en annan I2C-buss: Kör sudo i2cdetect -y 1 eller sudo i2cdetect -y 2 för att testa olika I2C-bussar.


Jag hann inte utföra allt i yrkesprovet på grund av tekniska hinder med I2C-kommunikationen och sensorinstallationerna, vilket fördröjde framstegen och gjorde att jag inte hann slutföra alla uppgifter inom tidsramen.
