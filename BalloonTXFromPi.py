import socket
import json
import time
import serial

#As built the formatted message takes 30 seconds to send at the normal rate

LOG_PATH = 'log.txt'
JS8CALL_PORT = 2242
LISTEN_ADDRESS = '0.0.0.0'


def log_message(message):
    with open(LOG_PATH, 'a') as log_file:
        log_file.write(f'{message}\n')


def create_udp_server(address, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((address, port))
    print(f'UDP server is listening on {address}:{port}')
    log_message('Decoder Starting...')
    return server


def receive_initial_contact(server):
    data, remote_address = server.recvfrom(1024)
    return remote_address[0], remote_address[1], data

def get_gps_coordinates(port='/dev/serial0', baudrate=9600, timeout=1):
    def nmea_to_decimal(degrees_minutes, direction):
        if not degrees_minutes or not direction:
            return None
        if '.' not in degrees_minutes:
            return None
        if direction in ['N', 'S']:
            degrees = int(degrees_minutes[:2])
            minutes = float(degrees_minutes[2:])
        else:  # E or W
            degrees = int(degrees_minutes[:3])
            minutes = float(degrees_minutes[3:])
        decimal = degrees + minutes / 60.0
        if direction in ['S', 'W']:
            decimal *= -1
        return decimal

    ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)

    try:
        while True:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
                parts = line.split(',')
                if line.startswith('$GPGGA') and len(parts) >= 6:
                    lat = nmea_to_decimal(parts[2], parts[3])
                    lon = nmea_to_decimal(parts[4], parts[5])
                elif line.startswith('$GPRMC') and len(parts) >= 7:
                    lat = nmea_to_decimal(parts[3], parts[4])
                    lon = nmea_to_decimal(parts[5], parts[6])
                else:
                    continue

                if lat is not None and lon is not None:
                    return (lat, lon)
    except Exception as e:
        print(f"Error reading GPS: {e}")
        return None
    finally:
        ser.close()

def latlon_to_maidenhead(lat, lon):
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Latitude must be between -90 and 90, and longitude between -180 and 180.")

    lat += 90.0
    lon += 180.0
    A = ord('A')
    a = ord('a')

    maiden = ""

    # Field (2)
    maiden += chr(A + int(lon // 20))
    maiden += chr(A + int(lat // 10))

    # Square (2)
    maiden += str(int((lon % 20) // 2))
    maiden += str(int(lat % 10))

    # Subsquare (2)
    maiden += chr(a + int((lon % 2) * 12))
    maiden += chr(a + int((lat % 1) * 24))

    # Extended 1 (2)
    maiden += str(int((((lon % 2) * 12) % 1) * 10))
    maiden += str(int((((lat % 1) * 24) % 1) * 10))

    # Extended 2 (2)
    maiden += chr(a + int(((((lon % 2) * 12) % 1) * 10 % 1) * 24))
    maiden += chr(a + int(((((lat % 1) * 24) % 1) * 10 % 1) * 24))

    return maiden



def build_aprs_message(maidenhead):
    return f'@APRSIS GRID {maidenhead}'


def send_udp_message(host, port, message):
    timestamp_ms = int(time.time() * 1000)

    payload = {
        'type': 'TX.SEND_MESSAGE',
        'value': message,
        'params': timestamp_ms
    }

    json_payload = json.dumps(payload).encode()
    blank = "".encode()

    udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_client.sendto(blank, (host, port))           # clear window
    udp_client.sendto(json_payload, (host, port))    # send message
    udp_client.close()

    print(f"{json_payload.decode()} sent to {host}:{port}")
    log_message(f"Sent: {json_payload.decode()} to {host}:{port}")


def main():
    server = create_udp_server(LISTEN_ADDRESS, JS8CALL_PORT)

    remote_ip, remote_port, _ = receive_initial_contact(server)

    latlon = get_gps_coordinates()
    maidenhead = latlon_to_maidenhead(latlon[0],latlon[1])
    # In production, fetch real GPS and convert to Maidenhead
    #maidenhead = 'EM83WL07UI'
    message = build_aprs_message(maidenhead)

    print(f"Sending {message} to {remote_ip}:{remote_port}")
    send_udp_message(remote_ip, remote_port, message)


if __name__ == '__main__':
    main()
