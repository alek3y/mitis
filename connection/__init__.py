import socket

class Connection:
	def __init__(self, ip):
		self.socket = socket.socket(type=socket.SOCK_DGRAM)
		self.ip = ip

	def send(data):
		length = len(data).to_bytes(4, "little")
		packet = length + data
		self.socket.sendto(packet, self.ip)
