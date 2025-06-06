import socket
import json

udp_server_info = ['0.0.0.0', 2242]
log_path = 'log.txt'

def udp_server(udp_server_info):
	global log_path
	#Create a UDP server socket
	udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#bind socket to port
	udp_server.bind((udp_server_info[0], int(udp_server_info[1])))
	print(f'UDP server is listening on port {udp_server_info[1]}')

	#open log file to write
	with open (log_path, 'a') as log_file:
		log_file.write('Decoder Starting...\n')
	while True:
		remote = receive_remote(udp_server)  # Update the global remote variable
		print(f"JS8 UDP CONNECTION: {remote[0]}:{remote[1]}")

		json_data = None  # Ensure it exists even if decoding fails

		try:
			json_data = json.loads(remote[2].decode())
		except:
			print(f"decode error in {remote[2]}")
			with open (log_path, 'a') as log_file:
				log_file.write(f'decode error in {remote[2]}\n')
			json_data = None

		if json_data:
			with open (log_path, 'a') as log_file:
				log_file.write(f'{json_data}\n')
			print(f"json_data: {json_data['params']}")
			if 'CALL' in json_data['params']:
				print(f"Callsign: {json_data['params']['CALL']}")


# print("Received message from JS8:", remote[2])

def receive_remote(udp_server):
	message, remote_address = udp_server.recvfrom(1024)
	#print(f"Received message from {remote_address[0]}:{remote_address[1]}: {message.decode()}")
	return (remote_address[0], remote_address[1], message)


if __name__ == '__main__':
	udp_server(udp_server_info)
