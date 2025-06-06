import socket
import json
import http.client
from datetime import datetime, timezone, timedelta

LISTEN_ADDRESS = '0.0.0.0'
JS8CALL_PORT = 2242
LOG_PATH = 'log.txt'
TAK_SERVER_ADDRESS = '192.168.5.14'
TAK_SERVER_PORT = 8087


def log_message(message):
	with open(LOG_PATH, 'a', encoding='utf-8') as f:
		f.write(f'{message}\n')


def create_udp_server(address, port):
	server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server.bind((address, port))
	print(f'UDP server is listening on {address}:{port}')
	log_message('Decoder Starting...')
	return server


def receive_remote_message(server_socket):
	message, remote_address = server_socket.recvfrom(1024)
	return remote_address[0], remote_address[1], message

def maidenhead_to_latlon(grid):
	"""
	Convert Maidenhead grid (2 to 10 characters) to (latitude, longitude) in decimal degrees.
	Returns the center point of the grid square.
	"""
	if len(grid) < 2 or len(grid) % 2 != 0 or len(grid) > 10:
		raise ValueError("Maidenhead grid must be 2, 4, 6, 8, or 10 characters long.")

	grid = grid.upper()

	lon = -180 + (ord(grid[0]) - ord('A')) * 20
	lat = -90 + (ord(grid[1]) - ord('A')) * 10

	if len(grid) >= 4:
		lon += int(grid[2]) * 2
		lat += int(grid[3]) * 1

	if len(grid) >= 6:
		lon += (ord(grid[4]) - ord('A')) * (5.0 / 60)
		lat += (ord(grid[5]) - ord('A')) * (2.5 / 60)

	if len(grid) >= 8:
		lon += int(grid[6]) * (5.0 / 600)
		lat += int(grid[7]) * (2.5 / 600)

	if len(grid) == 10:
		print(f'\n\n***** 10 DIGIT GRID: {grid} *****\n\n')
		lon += (ord(grid[8]) - ord('A')) * (5.0 / 600 / 24)
		lat += (ord(grid[9]) - ord('A')) * (2.5 / 600 / 24)

	# Grid precision lookup for adding half-cell offset
	precision = {
		2: (10, 20),
		4: (1, 2),
		6: (2.5 / 60, 5.0 / 60),
		8: (2.5 / 600, 5.0 / 600),
		10: (2.5 / 600 / 24, 5.0 / 600 / 24),
	}

	lat_prec, lon_prec = precision[len(grid)]
	lat += lat_prec / 2
	lon += lon_prec / 2

	return round(lat, 6), round(lon, 6)



def process_packet(remote_ip, remote_port, data):
	try:
		decoded = data.decode()
		json_data = json.loads(decoded)
	except Exception:
		print(f"Decode error in: {data}")
		log_message(f"Decode error in: {data}")
		return

	log_message(str(json_data))
	print(f"JS8 UDP CONNECTION: {remote_ip}:{remote_port}")
	print(f"json_data: {json_data.get('params', {})}")

	params = json_data.get('params', {})

	call = params.get('CALL')
	grid = params.get('GRID')
	text = params.get('TEXT')
	snr = params.get('SNR')

	if call and grid:
		lat, lon = maidenhead_to_latlon(grid.strip())
		print(f"Callsign: {call} - Maidenhead: {grid} - Lat: {lat} - Lon: {lon}")
		send_to_tak(call, lat, lon, snr)

	if text:
		print(f"Text received: {text}")

def send_to_tak(call, lat, lon, snr):

	try:

		type = "F"

		if type == "F":
			icontype = "a-n-g"
			iconsetpath = "COT_MAPPING_2525B/a-n/a-n-G"
		else:
			icontype = "a-h-g"
			iconsetpath = "COT_MAPPING_2525B/a-h/a-h-G"

		# Get the current time and format it as required
		current_time = datetime.now(timezone.utc)
		current_time_str = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')

		# Calculate the stale time as 24 hours after the current time
		stale_time = current_time + timedelta(hours=1)
		stale_time_str = stale_time.strftime('%Y-%m-%dT%H:%M:%SZ')

		# Define the XML payload using the parsed values, current time, and stale time
		cot_xml = f"""<?xml version="1.0" encoding="utf-16"?>
			<COT>
			  <event version="2.0" uid="{call}" type="{icontype}" how="h-g-i-g-o" time="{current_time_str}" start="{current_time_str}" stale="{stale_time_str}">
				<point lat="{lat}" lon="{lon}" hae="0" le="9999999" ce="9999999" />
				<detail>
				  <contact callsign="{call}" />
				  <link type="a-f-G-E-V-A" uid="S-1-5-21-621230609-327008285-3454491554-500" parent_callsign="2JCS - B" relation="p-p" production_time="{current_time_str}" />
				  <archive />
				  <usericon iconsetpath="{iconsetpath}" />
				  <remarks>SNR: {snr}</remarks>
				</detail>
			  </event>
			</COT>"""

		# Create an HTTP connection to the server
		conn = http.client.HTTPConnection(TAK_SERVER_ADDRESS, TAK_SERVER_PORT)

		# Define the headers for the request
		headers = {"Content-type": "application/xml"}

		# Send an HTTP POST request with the XML payload
		print(cot_xml)
		conn.request("POST", "/", body=cot_xml, headers=headers)

		# Return a success status code (e.g., 200) to indicate that the request was sent
		return 200

	except Exception as e:
		# Handle exceptions here
		print("Error in SendCot:", str(e))
		# Return an error status code (e.g., 500) to indicate that an exception occurred
		return 500

	finally:
		if conn is not None:
			# Close the connection if it was created
			conn.close()
			print("Success!")


# Future expansion:
	# if 'GRID' in message text:
	#     convert to lat/lon
	#     create and send CoT to TAK server


def main():
	server = create_udp_server(LISTEN_ADDRESS, JS8CALL_PORT)

	while True:
		remote_ip, remote_port, message = receive_remote_message(server)
		process_packet(remote_ip, remote_port, message)


if __name__ == '__main__':
	main()
