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

		return packet_bytes

	@staticmethod
	def unpack(packet_bytes):
		if len(packet_bytes) < 1:
			raise ValueError(f"missing packet type")

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
	def __init__(self, binding=None):
		self.socket = socket.socket(type=socket.SOCK_DGRAM)

		if binding:
			self.socket.bind(binding)

	def send(self, packet, ip):
		packed_packet = packet.pack()
		length = len(packed_packet)

		return self.socket.sendto(
			length.to_bytes(4, "little") + packed_packet,
			ip
		)

	def receive(self):
		length_bytes, _ = self.socket.recvfrom(4)

		if len(length_bytes) < 4:
			raise EOFError(f"truncated packet bytes")

		length = int.from_bytes(length_bytes, "little")
		if length < 1:
			raise ValueError(f"invalid packet length")

		# TODO: https://stackoverflow.com/a/675821
		packed_packet = self.socket.recvfrom(length)
		return Packet.unpack(packed_packet)
