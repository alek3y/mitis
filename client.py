from connection import *
from gui import Gui
from audio import AudioPlayer, AudioHandler
from threading import Thread, Semaphore
from queue import Queue
import cv2, imutils
import pygame
import sys
import logging
import time

SERVER_ADDRESS = (socket.gethostbyname("dev.alek3y.com"), 4444)
SERVER_REPLY_TIMEOUT = 5
PACKET_TIMEOUT = 0.1
HEARTBEAT_INTERVAL = 4

WEBCAM_WIDTH = 400
WEBCAM_QUALITY = 80
VIDEO_MISSING = open("assets/video_missing.png", "rb").read()

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
logging.getLogger("PIL").setLevel(logging.WARNING)

client = Connection()

webcam = cv2.VideoCapture(0)
webcam_disabled = False

webcam.set(cv2.CAP_PROP_FRAME_WIDTH, WEBCAM_WIDTH)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, WEBCAM_WIDTH*9/16)

audio_incoming = {
	# client_id: (audio_queue, player)
}

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
	global join_response, webcam_disabled

	join_response.acquire()
	gui.addCam(None)
	gui.updateCam(None, VIDEO_MISSING)

	video_disabled_sent = False
	while True:
		success, frame = webcam.read()
		if not success:
			break

		if webcam_disabled:
			if not video_disabled_sent:
				send(Packet.Type.VIDEO, VIDEO_MISSING)
				gui.updateCam(None, VIDEO_MISSING)
				video_disabled_sent = True
			continue
		video_disabled_sent = False

		frame = imutils.resize(frame, width=WEBCAM_WIDTH)
		frame_bytes = cv2.imencode(
			".jpg", frame,
			(cv2.IMWRITE_JPEG_QUALITY, WEBCAM_QUALITY)
		)[1].tobytes()

		send(Packet.Type.VIDEO, frame_bytes)
		gui.updateCam(None, frame_bytes)

	logging.info("Webcam stream stopped")
	webcam.release()

def packets_hello(gui, recorder, receiver):
	global join_request, join_response, join_timeout
	global audio_queue

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

				logging.debug("Starting audio recorder")
				recorder.start()
			else:
				gui.addCam(client_id)
				gui.updateCam(client_id, VIDEO_MISSING)
				audio_queue = Queue()
				player = AudioPlayer(audio_queue)
				player.start()
				audio_incoming[client_id] = (audio_queue, player)
				logging.debug(f"Client '{client_id}' joined the room")

def packets_generic(gui, receiver):
	global audio_queue

	while True:
		for t in (Packet.Type.CHAT, Packet.Type.QUIT):
			try:
				(client_id, _), content = receiver.next(t, timeout=PACKET_TIMEOUT)
			except Receiver.TimeoutError:
				continue

			if t == Packet.Type.CHAT:
				gui.receiveMessage(client_id, content)
			elif t == Packet.Type.QUIT:
				gui.removeCam(client_id)
				player = audio_incoming[client_id][1]
				player.stop()
				#player.join()	# TODO: Sull'AudioPlayer il while si blocca su queue.get()
				audio_incoming.pop(client_id)
				logging.debug(f"Client '{client_id}' left the room")

def packets_video(gui, receiver):
	while True:
		(client_id, _), frame_bytes = receiver.next(Packet.Type.VIDEO)
		gui.updateCam(client_id, frame_bytes)

def packets_audio(receiver):
	while True:
		(client_id, _), audio_bytes = receiver.next(Packet.Type.AUDIO)

		if client_id in audio_incoming:
			audio_incoming[client_id][0].put(audio_bytes)

def ask_join(room):
	global join_request

	send(Packet.Type.JOIN, room)
	join_request.release()

def video_disable():
	global webcam_disabled

	webcam_disabled = not webcam_disabled

if __name__ == "__main__":
	receiver = Receiver(client)
	receiver.start()

	recorder = AudioHandler(
		lambda stream: send(Packet.Type.AUDIO, stream)
	)

	logging.debug("Building graphical user interface")
	gui = Gui(
		ask_join,
		lambda text: send(Packet.Type.CHAT, text),
		recorder.mute,
		video_disable
	)

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
		args=(gui, recorder, receiver),
		daemon=True
	).start()
	Thread(
		target=packets_generic,
		args=(gui, receiver),
		daemon=True
	).start()
	Thread(
		target=packets_video,
		args=(gui, receiver),
		daemon=True
	).start()
	Thread(
		target=packets_audio,
		args=(receiver,),
		daemon=True
	).start()

	logging.info("Showing interface")
	gui.root.mainloop()

	logging.info("Quitting")

	# Informa il server del quit se il collegamento è già avvenuto
	if not join_timeout:
		send(Packet.Type.QUIT)
