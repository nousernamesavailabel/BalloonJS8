import socket
import json
import time

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

    # In production, fetch real GPS and convert to Maidenhead
    maidenhead = 'EM83WL07UI'
    message = build_aprs_message(maidenhead)

    print(f"Sending {message} to {remote_ip}:{remote_port}")
    send_udp_message(remote_ip, remote_port, message)


if __name__ == '__main__':
    main()
