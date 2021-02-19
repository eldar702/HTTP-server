import socket
import os.path
import sys


class server:

	# errors:
	FILE_200 = "HTTP/1.1 200 OK\r\n"
	ERROR_404 = "HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n"
	ERROR_301 = "HTTP/1.1 301 Moved Permanently\r\nConnection: close\r\nLocation: /result.html\r\n\r\n"

	# initialize function for the server
	def __init__(self, source_ip, source_port):
		self._source_ip = source_ip
		self._source_port = source_port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind((self._source_ip, self._source_port))
		self.socket.listen(5)

	# the function open the files, read them in binary.
	def dealingFile(self, req_file):
		file = open(req_file, "rb")
		readed_file = file.read()
		# close the file
		file.close()
		return readed_file

	# the function search for a requested file.
	# if he exist - return the path of him.
	# if he doesn't exist -  return the correspond error.
	def searchFile(self, req_file):
		if req_file == "/":
			return "files/index.html"
		elif req_file == "/redirect":
			return "redirect"
		else:
			path = "files" + req_file
		if os.path.isfile(path):
			return path
		return None

	# implementation function:
	def run(self):
		while True:
            # accept connection:
			client_socket, client_adress = self.socket.accept()
			while True:
				try:
					dataBytes = client_socket.recv(1024)  # getting a massage in bits
					client_socket.settimeout(1)  # closing connection with a client after 1 second without respond
					if dataBytes == b'':     # checking if the massage is empty, if yes - close the connection
						break
					dataStr = dataBytes.decode()    # convert the client massage from bits to str.
					print(dataStr)
					# taking the relevant information (the path of the requested file and the connection type):
					pathStart = dataStr.find('GET') + 4
					pathEnd = dataStr.find(' HTTP')
					connectionStart = dataStr.find('Connection: ') + 12
					connectionEnd = dataStr.find('\r\n', connectionStart)

					# if there is no 'GET' or "connection" in the message, close the connection.
					if pathStart == -1 or pathEnd == -1 or connectionStart == -1 or connectionEnd == -1:
						break

					# using the relevant information to distil the requested file's address and connection type.
					first_path = dataStr[pathStart:pathEnd]
					connection_type = dataStr[connectionStart:connectionEnd]

					# create variable contain the variable path and/or name and the connection type.
					final_file_path = self.searchFile(first_path)
					if final_file_path is None:   # the requested file is not in the given path.
						client_socket.send(self.ERROR_404.encode())
						break

					elif final_file_path == "redirect":   # the request file is "redirect".
						client_socket.send(self.ERROR_301.encode())
						break

					else:   # the requested file is found.
						the_File = self.dealingFile(final_file_path)
						file_size = os.path.getsize(final_file_path)
						# sent massage for the client, contain the relative error
						# (if is an error) and the requested file (if exist):
						message = "{}Connection: {}\r\nContent-Length: {}\r\n\r\n".format(self.FILE_200, connection_type,
																							file_size)
						client_socket.send(message.encode())
						client_socket.send(the_File)
						# if the connection type is 'close' - close the connection.
						# (break will take it 5 lines down to the 'client_socket.close())
						if connection_type == "close":
							break

				except Exception as e:
					break
			client_socket.close()


# self variables deceleration:
source_ip = 'localhost'
source_port = int(sys.argv[1])
buffer_size = 1024
file_dict = "files"
server = server(source_ip, source_port)
server.run()
