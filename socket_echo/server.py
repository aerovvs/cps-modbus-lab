import socket

HOST = '127.0.0.1' # localhost
PORT = 1502 # unused port

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	"""AF_INET = uses IPv4 addresses, SOCK_STREAM = uses TCP"""
	s.bind((HOST, PORT)) # uses given host and port
	s.listen(1) # allows only 1 connect in queue
	print(f"Listening on {HOST}:{PORT}")
	conn, addr = s.accept() # allows a new socket and addr to talk
	with conn:
		print("Connected by", addr) # addr = port number
		while True:
			data = conn.recv(1024) # receives up to 1024 bytes
			if not data:
				break
			conn.sendall(data) # sends data back
