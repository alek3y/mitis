from connection import *
import random
import logging

# TODO: Garbage collector per i client disconnessi?

BINDING = ("0.0.0.0", 4444)

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)

logging.info(f"Binding server connection to {BINDING}")
server = Connection(BINDING)

clients = {
	# client_id: (address, port)
}
rooms = {
	# room_id: {client_id, ...}
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

def client_join(source_address, room):
	global clients, rooms

	if source_address in clients.values():
		return

	client_id = client_new_id(clients)
	if room not in rooms:
		logging.debug(f"Creating room '{room}' for client {client_id, source_address}")
		rooms[room] = set()
	else:
		logging.debug(f"Broadcasting new joined client {client_id, source_address} to room '{room}'")
		for remote_client in rooms[room]:

			# Annuncia ad ogni partecipante della stanza la presenza di un nuovo client
			server.send(Packet(Packet.Type.HELLO), clients[remote_client], client_id)

			# Annuncia al nuovo client la presenza di ogni partecipante
			server.send(Packet(Packet.Type.HELLO), source_address, remote_client)

	clients[client_id] = source_address
	rooms[room].add(client_id)

def client_chat(source_address, message):
	global clients, rooms

	source_client_id = None
	for client_id in clients:
		if clients[client_id] == source_address:
			source_client_id = client_id
			break

	if not source_client_id:
		return

	dest_room_id = None
	for room in rooms:
		if source_client_id in rooms[room]:
			dest_room_id = room
			break
	assert dest_room_id

	# Rinvia il messaggio a tutti i client nella stanza
	for client_id in rooms[dest_room_id]:
		server.send(
			Packet(Packet.Type.CHAT, message),
			clients[client_id],
			source_client_id
		)

def packet_handler(source_client, packet):
	if packet.type == Packet.Type.JOIN:
		client_join(source_client[1], packet.content)
	elif packet.type == Packet.Type.CHAT:
		client_chat(source_client[1], packet.content)
	else:
		logging.error(f"Received unsupported packet {packet.type}")

if __name__ == "__main__":
	receiver = Receiver(server, packet_handler)

	logging.info("Starting packets receiver")
	receiver.start()
	receiver.join()
