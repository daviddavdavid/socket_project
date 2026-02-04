import socket

class client_socket:
    def __init__(self):
        self.client_socket = None
        self.HOST = None
        self.PORT = None
        self.protoheader = None
        self.header = None
        self.content = None
        self.received_data = None

    def create_socket(self, HOST, PORT):
        if client_socket == None:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.HOST = HOST
            self.PORT = PORT
        return socket
    
    def connect_to_server(self):
        client_socket = self.client_socket
        if client_socket != None & isinstance(self.HOST, str) & isinstance(self.PORT, int):
            client_socket.connect((self.HOST, self.PORT))
            return True
        raise("Connecting is not possible, values are missing")
    
    def close(self):
        self.socket.close()
        print(f"Connection ended, client closed the socket")

    def receive_data(self):
        try:
            data = self.client_socket.recv(4096)
        except BlockingIOError:
            pass # just try again in a second when the data is there
        if data != None:
            self.receive_data = data
        else:
            self.close()
            raise("Error: Connection has closed")
            
    def read_message(self, content):
        self.receive_data() # The program is meant to wait here till the server has sent something

        if self.protoheader == None:
            self.protoheader = self.read_proto_header()

        if self.header == None:
            self.header = self.read_header()

        if isinstance(content, str) == False:
            raise("You did not supply any content string")
        elif len(content) > 1023:
            raise("You send way too much content")
        
        self.read_message_content()

    def json_encode(self):
        pass

    def json_decode(self):
        pass

    def read_proto_header(self):
        pass

    def read_header(self):
        pass

    def read_message_content(self):
        pass

