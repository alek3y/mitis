from connection import *
from gui import Gui
from audio import AudioPlayer, AudioHandler, SpeechRecognition
from threading import Thread, Semaphore
from queue import Queue
import tools
import cv2, imutils
import pygame
import sys
import logging
import time

SERVER_ADDRESS = (socket.gethostbyname("dev.alek3y.com"), 4444)
#SERVER_ADDRESS = ("13.79.39.161", 4444)

SERVER_REPLY_TIMEOUT = 5
PACKET_TIMEOUT = 0.1	# Tempo di attesa di un pacchetto generico
HEARTBEAT_INTERVAL = 4

WEBCAM_WIDTH = 400
WEBCAM_QUALITY = 80
VIDEO_MISSING = open("assets/video_missing.jpg", "rb").read()

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

	join_response.acquire()	# Attesa della conferma di join dal server
	gui.addCam(None)
	gui.updateCam(None, VIDEO_MISSING)

	video_disabled_sent = False
	while True:
		success, frame = webcam.read()
		if not success:
			break

		if webcam_disabled:

			# Invia una volta a tutti l'immagine della webcam spenta
			if not video_disabled_sent:
				send(Packet.Type.VIDEO, VIDEO_MISSING)
				gui.updateCam(None, VIDEO_MISSING)
				video_disabled_sent = True

			continue	# Ignora completamente il frame della webcam
		video_disabled_sent = False

		if gui.mask:
			frame = tools.face_mask(frame, gui.mask)

		for enabled_filter in gui.filters:
			frame = tools.apply_filter(enabled_filter, frame)

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
	global audio_incoming

	while True:
		join_request.acquire()	# Attesa dell'invio della richiesta di join
		while True:
			try:
				(client_id, _), _ = receiver.next(Packet.Type.HELLO, timeout=join_timeout)
			except Receiver.TimeoutError:
				logging.error("Cannot connect to remote server")
				gui.failJoin()
				break

			# Un HELLO senza ID del client sorgente indica l'avvenuta
			# connessione al server
			if not client_id:
				gui.createWindow()
				logging.info("Successfully connected to remote server")
				join_timeout = None	# Attesa indeterminata per il prossimo pacchetto

				# Annuncia a tutti i thread l'avvenuta connessione
				for i in range(JOIN_WAITING):
					join_response.release()

				logging.debug("Starting audio recorder")
				recorder.start()

			# Un HELLO con client ID indica il join di un client
			else:
				gui.addCam(client_id)
				gui.updateCam(client_id, VIDEO_MISSING)

				# Avvio del thread audio per questo client
				audio_queue = Queue()
				player = AudioPlayer(audio_queue)
				player.start()
				audio_incoming[client_id] = (audio_queue, player)

				logging.debug(f"Client '{client_id}' joined the room")

# Thread per l'attesa di pacchetti generici che non hanno bisogno di
# controllo e gestione immediata
def packets_generic(gui, receiver):
	global audio_incoming

	while True:
		for t in (Packet.Type.CHAT, Packet.Type.QUIT, Packet.Type.CAPTIONS):
			try:
				(client_id, _), content = receiver.next(t, timeout=PACKET_TIMEOUT)
			except Receiver.TimeoutError:
				continue

			if t == Packet.Type.CHAT:
				gui.receiveMessage(client_id, content)

			elif t == Packet.Type.CAPTIONS:
				gui.placeSubtitle(client_id, content)

			elif t == Packet.Type.QUIT:
				gui.removeCam(client_id)

				# Rimozione del player audio del client in uscita
				audio_incoming[client_id][1].stop()
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
			audio_incoming[client_id][0].put(audio_bytes)	# Aggiunta del chunk alla coda audio del client

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
		ask_join,	# Gestione textbox per entrare in una stanza
		lambda text: send(Packet.Type.CHAT, text),	# Gestione messaggi in uscita
		recorder.mute,	# Mute
		video_disable	# Disattivazione la webcam
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

	logging.debug("Starting captions engine")
	SpeechRecognition(
		recorder,	# Thread per la registrazione audio
		lambda caption: send(Packet.Type.CAPTIONS, caption)	# Gestione sottotitoli
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
