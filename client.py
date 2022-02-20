from connection import *
from gui import Gui
from threading import Thread, Semaphore
import sys
import logging
import time

SERVER_ADDRESS = ("localhost", 4444)
SERVER_REPLY_TIMEOUT = 5
PACKET_TIMEOUT = 0.1
HEARTBEAT_INTERVAL = 4

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
client = Connection()

join_request_wait = Semaphore(0)
join_timeout = SERVER_REPLY_TIMEOUT

def send(packet_type, content=None):
	global client
	client.send(Packet(packet_type, content), SERVER_ADDRESS)

def heartbeat():
	global join_request_wait

	join_request_wait.acquire()
	while True:
		send(Packet.Type.HEARTBEAT)
		time.sleep(HEARTBEAT_INTERVAL)

def packets_hello(gui, receiver):
	global join_request_wait, join_timeout

	while True:
		join_request_wait.acquire()
		while True:
			try:
				(client_id, _), content = receiver.next(Packet.Type.HELLO, timeout=join_timeout)
			except Receiver.TimeoutError:
				logging.error("Cannot connect to remote server")
				gui.failJoin()
				break

			if not client_id:
				gui.createWindow()
				logging.info("Successfully connected to remote server")
				join_timeout = None
			else:
				# TODO: Aggiungere una webcam per il nuovo client
				logging.debug(f"Client '{client_id}' joined the room")

def packets_generic(gui, receiver):
	while True:
		for t in (Packet.Type.CHAT, Packet.Type.QUIT):
			try:
				(client_id, _), content = receiver.next(t, timeout=PACKET_TIMEOUT)
			except Receiver.TimeoutError:
				continue

			if t == Packet.Type.CHAT:
				logging.debug(f"Received message from '{client_id}': '{content}'")	# TODO: Da rimuovere
			elif t == Packet.Type.QUIT:
				# TODO: Rimuovere la webcam dalla GUI
				logging.debug(f"Client '{client_id}' left the room")

def join_request(room):
	global join_request_wait

	send(Packet.Type.JOIN, room)

	# Lascia partire il thread HELLO e HEARTBEAT
	join_request_wait.release()
	join_request_wait.release()

if __name__ == "__main__":
	receiver = Receiver(client)
	receiver.start()

	logging.debug("Building graphical user interface")
	gui = Gui(join_request)

	logging.debug("Starting heartbeat periodic signal")
	Thread(
		target=heartbeat,
		daemon=True
	).start()

	logging.debug("Starting packets handler threads")
	Thread(
		target=packets_hello,
		args=(gui, receiver),
		daemon=True
	).start()
	Thread(
		target=packets_generic,
		args=(gui, receiver),
		daemon=True
	).start()

	logging.info("Showing interface")
	gui.root.mainloop()

	logging.info("Quitting")

	# Informa il server del quit se il collegamento è già avvenuto
	if not join_timeout:
		send(Packet.Type.QUIT)
