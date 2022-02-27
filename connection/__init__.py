from enum import Enum
from threading import Thread
import queue
import socket
import re
import string

# Parametri per generare il codice identificativo dei client
CLIENTID_CHARS = string.ascii_letters + string.digits
CLIENTID_LENGTH = 5

class Packet:

	# Tipi di contenuti trasmissibili
	class Type(Enum):
		RAW = (0, bytes)

		# Stream dei client
		CHAT = (1, str)
		CAPTIONS = (2, str)
		AUDIO = (3, bytes)
		VIDEO = (4, bytes)

		# Gestione della connessione
		HELLO = (5, type(None))
		QUIT = (6, type(None))
		HEARTBEAT = (7, type(None))
		JOIN = (8, str)

	def __init__(self, packet_type, content=None):
		if packet_type.value[1] != type(content):
			raise TypeError(f"expected data type {packet_type.value[1]}")

		self.content = content
		self.type = packet_type

	# Conversione di un Packet a bytes
	def pack(self):
		packet_bytes = self.type.value[0].to_bytes(1, "little")	# ID del pacchetto in bytes

		data = None
		if self.type.value[1] == str:
			data = self.content.encode("utf-8")
		elif self.type.value[1] != type(None):
			data = self.content

		if data:
			packet_bytes += data

		return packet_bytes

	# Conversione di bytes ad un Packet
	@staticmethod
	def unpack(packet_bytes):
		if len(packet_bytes) < 1:
			raise ValueError("missing packet type")

		# Trova il tipo di pacchetto dall'enum Type
		type_id = packet_bytes[0]
		packet_type = None
		for t in Packet.Type:
			if t.value[0] == type_id:
				packet_type = t
				break

		if not packet_type:
			raise ValueError("content type not recognized")

		# Decodifica del contenuto in base al tipo
		data = packet_bytes[1:]
		content = None
		if packet_type.value[1] == str:
			content = data.decode("utf-8")
		elif packet_type.value[1] != type(None):
			content = data

		return Packet(packet_type, content)

class Connection:
	def __init__(self, binding=None):
		self.socket = socket.socket(type=socket.SOCK_DGRAM)

		if binding:
			self.socket.bind(binding)

	def send(self, packet, ip, client_id=None):
		if not client_id:
			packed_packet = bytes(CLIENTID_LENGTH)	# Imposta il campo sorgente a vuoto
		else:
			packed_packet = client_id[:CLIENTID_LENGTH].encode("utf-8")

		packed_packet += packet.pack()
		length = len(packed_packet)

		# Invia all'IP i bytes composti da lunghezza, ID del client e pacchetto
		return self.socket.sendto(
			length.to_bytes(4, "little") + packed_packet,
			ip
		)

	def receive(self):

		# Per i socket UDP la lettura del messaggio cancella i successivi bytes,
		# di conseguenza per poter leggere la lunghezza precisa esiste il flag MSG_PEEK
		length_bytes, address = self.socket.recvfrom(4, socket.MSG_PEEK)

		length = int.from_bytes(length_bytes, "little")
		data = self.socket.recvfrom(4 + length)[0][4:]	# Salva i dati successivi alla lunghezza

		if len(data) < length:
			raise ValueError("invalid packet length")

		client_id = None
		client_id_bytes = data[:CLIENTID_LENGTH]

		# Trova l'ID nel caso i bytes non siano nulli
		if client_id_bytes != bytes(CLIENTID_LENGTH):
			client_id = client_id_bytes.decode("utf-8")

			# Controllo che l'ID sia nel formato corretto
			if not re.match(f"[{CLIENTID_CHARS}]{{{CLIENTID_LENGTH}}}", client_id):
				raise ValueError("invalid client identifier")

		packed_packet = data[CLIENTID_LENGTH:]

		return ((client_id, address), Packet.unpack(packed_packet))

class Receiver(Thread):
	class TimeoutError(Exception):
		pass

	def __init__(self, connection, handler=None):
		Thread.__init__(self, daemon=True)
		self.connection = connection

		self.handler = handler
		self.received = {

			# Una coda di pacchetti per ogni tipo
			t: queue.Queue()
			for t in Packet.Type
		}

	def run(self):
		while True:
			try:
				client, packet = self.connection.receive()
			except (ValueError, TypeError, UnicodeDecodeError):
				continue	# Ignora i pacchetti invalidi

			# Salva il pacchetto nella coda se non è specificata una
			# funzione per la gestione dei pacchetti in arrivo
			if not self.handler:
				self.received[packet.type].put((client, packet.content))

			else:
				self.handler(client, packet)

	def next(self, packet_type, timeout=None):
		try:
			return self.received[packet_type].get(timeout=timeout)	# Richiesta bloccante
		except queue.Empty:
			raise self.TimeoutError("packet request timed out")
