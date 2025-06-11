import socket

HOST = '127.0.0.1'
PORT = 1502

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.connect((HOST, PORT))
	s.sendall(b'Hello, CPS lab!') # takes bytes object (raw data) instead of a text string
	data = s.recv(1024)
	print('Received', repr(data))
