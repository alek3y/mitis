from connection import *
import random
import logging

BINDING = ("0.0.0.0", 4444)

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)

logging.info(f"Binding server connection to {BINDING}")
server = Connection(BINDING)

clients = {
	# client_id: (address, port)
}
rooms = {
	# room_id: [client_id, ...]
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

def client_join(client_address, room):
	global clients, rooms

	if client_address in clients.values():
		return

	client_id = client_new_id(clients)
	if room not in rooms:
		logging.debug(f"Creating room '{room}' for client {client_id, client_address}")
		rooms[room] = []
	else:
		logging.debug(f"Broadcasting new joined client {client_id, client_address} to room '{room}'")
		for remote_client in rooms[room]:

			# Annuncia ad ogni partecipante della stanza la presenza di un nuovo client
			server.send(Packet(Packet.Type.HELLO), clients[remote_client], client_id)

			# Annuncia al nuovo client la presenza di ogni partecipante
			server.send(Packet(Packet.Type.HELLO), client_address, remote_client)

	clients[client_id] = client_address
	rooms[room].append(client_id)

def packet_handler(source_client, packet):
	if packet.type == Packet.Type.JOIN:
		client_join(source_client[1], packet.content)
	else:
		logging.error(f"Received unsupported packet {packet.type}")

if __name__ == "__main__":
	receiver = Receiver(server, packet_handler)

	logging.info("Starting packets receiver")
	receiver.start()
	receiver.join()
