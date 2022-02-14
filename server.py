from connection import *
import random

BINDING = ("0.0.0.0", 4444)

server = Connection(BINDING)

rooms = {
	# room_id: [(client_id, (address, port)), ...]}
}

def registrations(rooms):
	ids = set()
	addresses = set()
	for room in rooms:
		for client in rooms[room]:
			ids.add(client[0])
			addresses.add(client[1])

	return (ids, addresses)

def new_client_id(ids):
	while True:
		client_id = "".join([
			random.choice(CLIENTID_CHARS) for i in range(CLIENTID_LENGTH)
		])

		if client_id not in ids:
			break

	return client_id

def packet_handler(local_client, packet):
	if packet.type == Packet.Type.JOIN:
		used_ids, addresses = registrations(rooms)

		if local_client[1] in addresses:
			return

		if packet.content not in rooms:
			rooms[packet.content] = []

		client_id = new_client_id(used_ids)
		for remote_client in rooms[packet.content]:
			server.send(Packet(Packet.Type.HELLO), remote_client[1], client_id)
			server.send(Packet(Packet.Type.HELLO), local_client[1], remote_client[0])

		rooms[packet.content].append((client_id, local_client[1]))

	# TODO: Gli altri tipi di pacchetto

if __name__ == "__main__":
	receiver = Receiver(server, packet_handler)
	receiver.start()
	receiver.join()
