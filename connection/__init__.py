from enum import Enum
import socket

class Packet:
	class Type(Enum):
		HELLO = (0, type(None))
		RAW = (1, bytes)
		CHAT = (2, str)
		CAPTIONS = (3, str)
		AUDIO = (4, bytes)
		VIDEO = (5, bytes)	# TODO: Numpy array?

	def __init__(self, packet_type, content=None):
		if packet_type.value[1] != type(content):
			raise TypeError(f"expected data type {packet_type.value[1]}")

		self.content = content
		self.type = packet_type

	def pack(self):
		packet_bytes = self.type.value[0].to_bytes(1, "little")

		data = None
		if self.type in (self.Type.CHAT, self.Type.CAPTIONS):
			data = self.content.encode("utf-8")
		elif self.type != self.Type.HELLO:
			data = self.content

		if data:
			packet_bytes += data

		return len(packet_bytes).to_bytes(4, "little") + packet_bytes

	@staticmethod
	def unpack(packed_packet):
		if len(packed_packet) < 4:
			raise ValueError(f"missing packet length")

		length = int.from_bytes(packed_packet[:4], "little")
		if length < 1:
			raise ValueError(f"invalid packet length")

		packet_bytes = packed_packet[4:4 + length]
		if len(packet_bytes) < length:
			raise EOFError(f"truncated packet bytes")

		type_id = packet_bytes[0]
		packet_type = None
		for t in Packet.Type:
			if t.value[0] == type_id:
				packet_type = t
				break

		if not packet_type:
			raise ValueError(f"content type not recognized")

		data = packet_bytes[1:]
		content = None
		if packet_type in (Packet.Type.CHAT, Packet.Type.CAPTIONS):
			content = data.decode("utf-8")
		elif packet_type != Packet.Type.HELLO:
			content = data

		return Packet(packet_type, content)

class Connection:
	def __init__(self, ip):
		self.socket = socket.socket(type=socket.SOCK_DGRAM)
		self.ip = ip
		# TODO: What about listening mode?

	def send(data):
		length = len(data).to_bytes(4, "little")
		packet = length + data
		self.socket.sendto(packet, self.ip)
