from connection import *
from threading import Thread
import sys
import logging

SERVER_ADDRESS = ("localhost", 4444)

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
client = Connection()

def send(packet_type, content):
	global client
	client.send(Packet(packet_type, content), SERVER_ADDRESS)

def chat(receiver):
	while True:
		(client_id, client_address), content = receiver.next(Packet.Type.CHAT)

		print(f"<{client_id}> {content}")

if __name__ == "__main__":
	receiver = Receiver(client)
	receiver.start()

	Thread(target=chat, args=(receiver,)).start()

	send(Packet.Type.JOIN, "th3g3ntl3man")
	while True:
		message = input()
		send(Packet.Type.CHAT, message)
