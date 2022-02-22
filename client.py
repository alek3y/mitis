from connection import *
from gui import Gui
from threading import Thread, Semaphore
import cv2, imutils
import sys
import logging
import time

SERVER_ADDRESS = ("localhost", 4444)
SERVER_REPLY_TIMEOUT = 5
PACKET_TIMEOUT = 0.1
HEARTBEAT_INTERVAL = 4

WEBCAM_WIDTH = 400
WEBCAM_QUALITY = 80

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
client = Connection()
webcam = cv2.VideoCapture(0)

# TODO: https://github.com/PyImageSearch/imutils/pull/237
#streaming = True

JOIN_WAITING = 2	# Thread che aspettano per la conferma di accesso
join_timeout = SERVER_REPLY_TIMEOUT

join_request = Semaphore(0)
join_response = Semaphore(0)

def send(packet_type, content=None):
	global client
	client.send(Packet(packet_type, content), SERVER_ADDRESS)

def heartbeat():
	global join_response

	join_response.acquire()
	while True:
		send(Packet.Type.HEARTBEAT)
		time.sleep(HEARTBEAT_INTERVAL)

def streaming_video(gui, webcam):
	global join_response

	join_response.acquire()
	gui.addCam(None)
	while True:
		frame = imutils.resize(
			webcam.read()[1],
			width=WEBCAM_WIDTH
		)

		frame_bytes = cv2.imencode(
			".jpg", frame,
			(cv2.IMWRITE_JPEG_QUALITY, WEBCAM_QUALITY)
		)[1].tobytes()

		send(Packet.Type.VIDEO, frame_bytes)
		gui.updateCam(None, frame_bytes)

def packets_hello(gui, receiver):
	global join_request, join_response, join_timeout

	while True:
		join_request.acquire()
		while True:
			try:
				(client_id, _), _ = receiver.next(Packet.Type.HELLO, timeout=join_timeout)
			except Receiver.TimeoutError:
				logging.error("Cannot connect to remote server")
				gui.failJoin()
				break

			if not client_id:
				gui.createWindow()
				logging.info("Successfully connected to remote server")
				join_timeout = None

				for i in range(JOIN_WAITING):
					join_response.release()
			else:
				gui.addCam(client_id)
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
				gui.removeCam(client_id)
				logging.debug(f"Client '{client_id}' left the room")

def packets_video(gui, receiver):
	while True:
		(client_id, _), frame_bytes = receiver.next(Packet.Type.VIDEO)
		gui.updateCam(client_id, frame_bytes)

def ask_join(room):
	global join_request

	send(Packet.Type.JOIN, room)
	join_request.release()

if __name__ == "__main__":
	receiver = Receiver(client)
	receiver.start()

	logging.debug("Building graphical user interface")
	gui = Gui(ask_join)

	logging.debug("Starting heartbeat periodic signal")
	Thread(
		target=heartbeat,
		daemon=True
	).start()

	logging.debug("Starting streaming threads")
	Thread(
		target=streaming_video,
		args=(gui, webcam),
		daemon=True
	).start()

	logging.debug("Starting packets handler threads")
	Thread(
		target=packets_hello,
		args=(gui, receiver),
		daemon=True
	).start()
	Thread(
		target=packets_video,
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
