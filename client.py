from connection import *
from gui import Gui
from threading import Thread, Semaphore
import sys
import logging

SERVER_ADDRESS = ("localhost", 4444)
SERVER_REPLY_TIMEOUT = 5

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
client = Connection()

join_request_wait = Semaphore(0)
join_timeout = SERVER_REPLY_TIMEOUT

def send(packet_type, content):
	global client
	client.send(Packet(packet_type, content), SERVER_ADDRESS)

def packets_chat(receiver):
	while True:
		(client_id, _), content = receiver.next(Packet.Type.CHAT)

		#print(f"<{client_id}> {content}")

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
				logging.debug("Successfully connected to remote server")
				join_timeout = None
			else:
				# TODO: Aggiungere una webcam per il nuovo client
				logging.debug(f"New client connected with ID '{client_id}'")

def join_request(room):
	global join_request_wait

	send(Packet.Type.JOIN, room)
	join_request_wait.release()

if __name__ == "__main__":
	receiver = Receiver(client)
	receiver.start()

	gui = Gui(join_request)

	Thread(target=packets_chat, args=(receiver,)).start()
	Thread(target=packets_hello, args=(gui, receiver)).start()

	gui.root.mainloop()
