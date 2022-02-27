from connection import *
import random
import logging
import time

BINDING = ("0.0.0.0", 4444)
HEARTBEAT_CHECK_INTERVAL = 3
HEARTBEAT_FAIL_DELAY = 12	# Dopo questi secondi il client viene disconnesso

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)

logging.info(f"Binding server connection to {BINDING}")
server = Connection(BINDING)

clients = {
	# client_id: (address, port)
}
rooms = {
	# room_id: {client_id, ...}
}
heartbeats = {
	# client_id: last_time
}

def client_new_id(clients):
	assert len(clients) < len(CLIENTID_CHARS)**CLIENTID_LENGTH

	while True:
		client_id = "".join([
			random.choice(CLIENTID_CHARS) for i in range(CLIENTID_LENGTH)
		])

		if client_id not in clients:
			break

	return client_id

def client_get_id(client_address):
	global clients

	client_id = None
	for remote_client_id in clients:
		if clients[remote_client_id] == client_address:
			client_id = remote_client_id
			break
	return client_id

def client_get_room(client_id):
	global rooms

	room_id = None
	for room in rooms:
		if client_id in rooms[room]:
			room_id = room
			break
	assert room_id	# Un client registrato è per forza in una stanza

	return room_id

def client_get_all(client_address):
	client_id = client_get_id(client_address)
	if not client_id:
		return (None, None)

	room_id = client_get_room(client_id)
	return (client_id, room_id)

def packet_heartbeat(client_id):
	global heartbeats
	heartbeats[client_id] = time.time()

def packet_join(source_address, room_id):
	global clients, rooms, server, heartbeats

	if source_address in clients.values():
		return

	client_id = client_new_id(clients)

	# Segnala al client l'avvenuta ricezione della richiesta
	server.send(Packet(Packet.Type.HELLO), source_address, None)

	logging.info(f"Client '{client_id}' joined the room '{room_id}'")
	if room_id not in rooms:
		rooms[room_id] = set()
	else:
		for remote_client in rooms[room_id]:

			# Annuncia ad ogni partecipante della stanza la presenza di un nuovo client
			server.send(Packet(Packet.Type.HELLO), clients[remote_client], client_id)

			# Annuncia al nuovo client la presenza di ogni partecipante
			server.send(Packet(Packet.Type.HELLO), source_address, remote_client)

	clients[client_id] = source_address
	rooms[room_id].add(client_id)
	packet_heartbeat(client_id)

def packet_forward(client_id, room_id, packet):
	global clients, rooms, server

	for remote_client_id in rooms[room_id] - {client_id,}:
		server.send(packet, clients[remote_client_id], client_id)

def packet_quit(source_client_id, room_id):
	global clients, rooms, heartbeats

	rooms[room_id].remove(source_client_id)
	clients.pop(source_client_id)
	heartbeats.pop(source_client_id)

	logging.info(f"Client '{source_client_id}' left the room '{room_id}'")
	if len(rooms[room_id]) < 1:
		logging.debug(f"Deleting empty room '{room_id}'")
		rooms.pop(room_id)
	else:
		packet_forward(source_client_id, room_id, Packet(Packet.Type.QUIT))

def packet_handler(source_client, packet):
	source_address = source_client[1]

	if packet.type == Packet.Type.JOIN:
		packet_join(source_address, packet.content)
	else:
		source_client_id, room_id = client_get_all(source_address)
		if not source_client_id:
			return

		if packet.type == Packet.Type.HEARTBEAT:
			packet_heartbeat(source_client_id)

		elif packet.type == Packet.Type.QUIT:
			packet_quit(source_client_id, room_id)

		elif packet.type in (
			Packet.Type.VIDEO, Packet.Type.AUDIO,
			Packet.Type.CHAT, Packet.Type.CAPTIONS
		):
			packet_forward(source_client_id, room_id, packet)

		else:
			logging.error(f"Received unsupported packet {packet.type}")

def heartbeat_monitor():
	global clients, heartbeats

	while True:
		for client_id in list(heartbeats.keys()):
			if client_id not in heartbeats:
				continue

			if time.time() - heartbeats[client_id] >= HEARTBEAT_FAIL_DELAY:
				logging.debug(f"Removing client '{client_id}' for interrupted heartbeat")
				room_id = client_get_room(client_id)
				packet_quit(client_id, room_id)

		time.sleep(HEARTBEAT_CHECK_INTERVAL)

if __name__ == "__main__":
	receiver = Receiver(server, packet_handler)

	logging.debug("Starting heartbeat monitor")
	Thread(
		target=heartbeat_monitor,
		daemon=True
	).start()

	logging.info("Starting packets receiver")
	receiver.start()
	receiver.join()
