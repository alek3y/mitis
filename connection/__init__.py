from enum import Enum
from threading import Thread, Semaphore
import socket
import re
import string

CLIENTID_CHARS = string.ascii_letters + string.digits
CLIENTID_LENGTH = 5

class Packet:
	class Type(Enum):
		RAW = (0, bytes)

		# Stream dei client
		CHAT = (1, str)
		CAPTIONS = (2, str)
		AUDIO = (3, bytes)
		VIDEO = (4, bytes)

		# Gestione connessioni
		HELLO = (5, type(None))
		QUIT = (6, type(None))
		HEARTBEAT = (7, type(None))
		JOIN = (8, str)

	def __init__(self, packet_type, content=None):
		if packet_type.value[1] != type(content):
			raise TypeError(f"expected data type {packet_type.value[1]}")

		self.content = content
		self.type = packet_type

	def pack(self):
		packet_bytes = self.type.value[0].to_bytes(1, "little")

		data = None
		if self.type.value[1] == str:
			data = self.content.encode("utf-8")
		elif self.type.value[1] != type(None):
			data = self.content

		if data:
			packet_bytes += data

		return packet_bytes

	@staticmethod
	def unpack(packet_bytes):
		if len(packet_bytes) < 1:
			raise ValueError("missing packet type")

		type_id = packet_bytes[0]
		packet_type = None
		for t in Packet.Type:
			if t.value[0] == type_id:
				packet_type = t
				break

		if not packet_type:
			raise ValueError("content type not recognized")

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
			packed_packet = bytes(CLIENTID_LENGTH)
		else:
			packed_packet = client_id[:CLIENTID_LENGTH].encode("utf-8")

		packed_packet += packet.pack()
		length = len(packed_packet)

		return self.socket.sendto(
			length.to_bytes(4, "little") + packed_packet,
			ip
		)

	def receive(self):
		length_bytes, address = self.socket.recvfrom(4, socket.MSG_PEEK)

		length = int.from_bytes(length_bytes, "little")
		data = self.socket.recvfrom(4 + length)[0][4:]

		if len(data) < length:
			raise ValueError("invalid packet length")

		client_id = None
		client_id_bytes = data[:CLIENTID_LENGTH]
		if client_id_bytes != bytes(CLIENTID_LENGTH):
			client_id = client_id_bytes.decode("utf-8")

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
			t: (Semaphore(0), [])
			for t in Packet.Type
		}

	def run(self):
		while True:
			try:
				client, packet = self.connection.receive()
			except (ValueError, TypeError, UnicodeDecodeError):
				continue

			if not self.handler:
				lock, packets = self.received[packet.type]
				lock.release()
				packets.append((client, packet.content))
			else:
				self.handler(client, packet)

	def next(self, packet_type, timeout=None):
		lock, packets = self.received[packet_type]

		lock.acquire(timeout=timeout)
		try:
			return packets.pop(0)
		except IndexError:
			raise self.TimeoutError("packet request timed out")
