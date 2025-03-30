import serial
import json
import os

# === KONFIGURACJA ===
UART_PORT = '/dev/serial0'
BAUDRATE = 100000
TIMEOUT = 0.05
JSON_PATH = "shared.json"
TMP_PATH = "shared.tmp"

# === INICJALIZACJA ===
ser = serial.Serial(
    port=UART_PORT,
    baudrate=BAUDRATE,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_TWO,
    timeout=TIMEOUT
)

frame = bytearray()

def parse_sbus(data):
    channels = []
    channels.append((data[1] | data[2] << 8) & 0x07FF)
    channels.append((data[2] >> 3 | data[3] << 5) & 0x07FF)
    channels.append((data[3] >> 6 | data[4] << 2 | data[5] << 10) & 0x07FF)
    channels.append((data[5] >> 1 | data[6] << 7) & 0x07FF)
    channels.append((data[6] >> 4 | data[7] << 4) & 0x07FF)
    channels.append((data[7] >> 7 | data[8] << 1 | data[9] << 9) & 0x07FF)
    channels.append((data[9] >> 2 | data[10] << 6) & 0x07FF)
    channels.append((data[10] >> 5 | data[11] << 3) & 0x07FF)
    channels.append((data[12] | data[13] << 8) & 0x07FF)
    channels.append((data[13] >> 3 | data[14] << 5) & 0x07FF)
    channels.append((data[14] >> 6 | data[15] << 2 | data[16] << 10) & 0x07FF)
    channels.append((data[16] >> 1 | data[17] << 7) & 0x07FF)
    channels.append((data[17] >> 4 | data[18] << 4) & 0x07FF)
    channels.append((data[18] >> 7 | data[19] << 1 | data[20] << 9) & 0x07FF)
    channels.append((data[20] >> 2 | data[21] << 6) & 0x07FF)
    channels.append((data[21] >> 5 | data[22] << 3) & 0x07FF)

    lost_frame = (data[23] >> 2) & 0x01
    failsafe = (data[23] >> 3) & 0x01

    return channels, lost_frame, failsafe

print("SBUS sniffer started...")

while True:
    byte = ser.read(1)
    if byte:
        frame += byte
        if len(frame) >= 25:
            if frame[0] == 0x0F:
                channels, lost, failsafe = parse_sbus(frame)
                shared_data = {
                    "channels": channels,
                    "lost_frame": lost,
                    "failsafe": failsafe
                }

                # --- Zapis bezpieczny ---
                try:
                    with open(TMP_PATH, "w") as f:
                        json.dump(shared_data, f)
                    os.replace(TMP_PATH, JSON_PATH)
                except Exception as e:
                    print(f"Write error: {e}")

                # --- Debug print ---
                print(f"Channels written: {channels} | Lost: {lost} | Failsafe: {failsafe}")

            frame = frame[1:]