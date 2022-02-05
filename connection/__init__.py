from enum import Enum
import socket

class Packet:
	class Type(Enum):
		HELLO = (0, type(None))
		RAW = (1, bytes)
		CHAT = (2, str)
		AUDIO = (3, bytes)
		VIDEO = (4, bytes)	# TODO: Numpy array?

	def __init__(self, packet_type, content=None):
		if packet_type.value[1] != type(content):
			raise ValueError(f"expected data type {packet_type.value[1]}")

		if packet_type == self.Type.CHAT:
			self.data = content.encode("utf-8")
		else:
			self.data = content

		self.type = packet_type

	def pack(self):
		packet_bytes = self.type.value[0].to_bytes(1, "little")
		if self.data:
			packet_bytes += self.data
		return len(packet_bytes).to_bytes(4, "little") + packet_bytes

class Connection:
	def __init__(self, ip):
		self.socket = socket.socket(type=socket.SOCK_DGRAM)
		self.ip = ip
		# TODO: What about listening mode?

	def send(data):
		length = len(data).to_bytes(4, "little")
		packet = length + data
		self.socket.sendto(packet, self.ip)
