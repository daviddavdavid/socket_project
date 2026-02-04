import socket

class client_socket:
    def __init__(self):
        self.client_socket = None
        self.HOST = None
        self.PORT = None
        self.protoheader = None
        self.header = None
        self.content = None
        self.collected_data = None

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
        
    def process_data(self):
        pass


    def read_message(self, content):
        self.collected_data = self.process_data()
        if self.protoheader == None:
            self.protoheader = self.read_proto_header()

        if self.header == None:
            self.header = self.read_header()

        if isinstance(content, str) == False:
            raise("You did not supply any content string")
        elif len(content) > 1023:
            raise("You send way too much content")
        
        self.read_message_content()

    def read_proto_header(self):
        pass

    def read_header(self):
        pass

    def read_message_content(self):
        pass

