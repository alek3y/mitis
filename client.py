from connection import *
from gui import Gui
from threading import Thread
import time
import sys
import logging

SERVER_ADDRESS = ("localhost", 4444)

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
client = Connection()

# TODO: C'è un altro modo? :I
join_request = None
has_joined = False

def send(packet_type, content):
	global client
	client.send(Packet(packet_type, content), SERVER_ADDRESS)

def packets_chat(receiver):
	while True:
		(client_id, _), content = receiver.next(Packet.Type.CHAT)

		#print(f"<{client_id}> {content}")

def packets_hello(receiver):
	global has_joined, join_request
	while True:
		try:
			(client_id, _), content = receiver.next(Packet.Type.HELLO, timeout=1)

			if not has_joined:
				logging.debug(f"Connected with client ID '{client_id}'")
				has_joined = True
				# TODO: Salvare l'ID e cambiare schermata sulla GUI
			else:
				# TODO: Aggiungere la webcam di un nuovo client
				pass
		except Receiver.TimeoutError:
			if join_request != None and time.time() - join_request >= 2 and not has_joined:
				# TODO: Riportare l'errore di connessione sulla GUI
				logging.error("Cannot connect to server")
				join_request = None
				pass

def request_join(room):
	global join_request

	send(Packet.Type.JOIN, room)
	join_request = time.time()

if __name__ == "__main__":
	receiver = Receiver(client)
	receiver.start()

	Thread(target=packets_chat, args=(receiver,)).start()
	Thread(target=packets_hello, args=(receiver,)).start()

	gui = Gui(request_join)
	gui.root.mainloop()
