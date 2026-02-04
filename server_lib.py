import socket
import json
import struct
import asyncio

class server:
    def __init__(self):
        self.current_socket = None
        self.HOST = None
        self.PORT = None
        self.address = None
        self.connection = None
        self._reset()

    def _reset(self):
        self.received_data = b""
        self.content = None
        self.encoded_header = None
        self.json_header_length = None
        self.json_header
        self.message_length = None
        self.message_encoding = None
        self.message_type = None
        self.message = None

    def create_socket(self, HOST, PORT):
        if self.current_socket is None:
            current_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            current_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            current_socket.bind((HOST, PORT))
            current_socket.listen()
            current_socket.setblocking(False)

            self.current_socket = current_socket
            self.HOST = HOST
            self.PORT = PORT # we keep it to be sure
        return self.current_socket
    
    async def accept_client(self):
        loop = asyncio.get_event_loop()
        current_socket = self.current_socket
        if current_socket is None or not isinstance(self.HOST, str) or not isinstance(self.PORT, int):
            raise Exception("CONNECTION NOT POSSIBLE, HOST AND PORT NOT DEFINED")
        
        connection, address = await loop.sock_accept(current_socket)
        self.connection = connection
        self.address = address
        connection.setblocking(False)

    def close(self):
        try:
            self.current_socket.close()
        except OSError as error:
            raise Exception(f"SOCKET CLOSING ERROR BECAUSE OF {error!r}")
        finally:
            self.current_socket = None
            print(f"Connection ended, client closed the socket")


    async def _send_to_client(self, total_message):
        loop = asyncio.get_event_loop()
        if self.current_socket is None:
            raise Exception("SOCKET IS NOT CONNECTED ERROR")
        loop.sock_sendall(self.current_socket, total_message)

    def write_data(self, message):
        if isinstance(message, str):
            raise Exception("WRONG TYPE ERROR, WE ONLY ACCEPT STRINGS")
        message_length = len(message)
        if message_length  > 1023:
            raise Exception("MESSAGE IS TOO LARGE ERROR") # Larger messages TBA
        encoding = "utf-8"
        encoded_message = message.encode(encoding)
        encoded_json_header = self._make_header(message_length)
        encoded_json_header_length = len(encoded_json_header)
        protoheader = struct.pack(">H", encoded_json_header_length)

        total_message = protoheader + encoded_json_header + encoded_message
        self._send_to_client(total_message)

    def _make_header(self, message_length):
        encoding = "utf-8"
        json_dict = {
            "message_length": message_length,
            "message_encoding": encoding, # we just do utf-8 in our program
            "message_type": "str" # we just do strings for now
        }

        json_header = json.dumps(json_dict)
        encoded_json_header = json_header.encode(encoding)
        return encoded_json_header

    async def get_data(self):
        loop = asyncio.get_event_loop()
        # TBA server closing
        data = b""
        try:
            data = loop.sock_recv(self.current_socket, 1024)
        except BlockingIOError:
            pass # just try again in a second when the data is there
        if data != b"":
            self.received_data += data
        else:
            self.close()
            raise Exception("CONECTION HAS ENDED ERROR")

    def _json_encode(self):
        if self.json_header == None:
            raise Exception("NO PROTOHEADER FOUND") 
        encoded_json_header = json.dumps(self.json_header).encode("utf-8")
        return encoded_json_header

    def _json_decode(self, encoded_header):
        if encoded_header == None:
            raise Exception("NO JSON HEADER FOUND")
        json_header = json.loads(encoded_header.decode("utf-8"))
        return json_header


    async def read_message(self):
        self.get_data() # The program is meant to wait here till the server has sent something

        if self.json_header_length is None:
            if len(self.received_data) < 2:
                return None # we wamt it to wait for more
            self._read_proto_header()

        if self.json_header is None:
            if len(self.received_data) < self.json_header_length:
                self._reset(keep_buffer=True)
                raise Exception("NO JSON HEADER ERROR") # TBA it is an error for now
            self._read_header()

        if len(self.received_data) < self.message_length:
            raise Exception("NO MESSAGE ERROR")
        
        self._read_message_content()
        self._reset() # resets all the values so it is ready for the next read cycle
        return self.message

    def _read_proto_header(self):
        header_length = 2
        if len(self.received_data) >= 2:
            self.json_header_length = struct.unpack(">H", self.received_data[:header_length])[0]
        self.received_data = self.received_data[header_length:]

    def _read_header(self):
        encoded_json_header = self.received_data[:self.json_header_length]
        self.received_data = self.received_data[self.json_header_length:]
        json_header = self._json_decode(encoded_json_header)
        self.message_length = json_header["message_length"]
        self.message_encoding = json_header["message_encoding"]
        self.message_type = json_header["message_type"]

        
    def _read_message_content(self):
        if (self.message_length > 1023):
            raise Exception("TOO MUCH DATA ERROR: TBA, now we dont accept large message lengths")
        elif self.message_type != "str":
            raise Exception("NON STRING ERROR: We only accept strings for now")
        elif self.message_encoding != "utf-8":
            raise Exception("NON UTF-8 ENCODING: we only accept utf-8")
        
        body = self.received_data[:self.message_length]
        self.received_data = self.received_data[self.message_length:]
        self.message = body.decode(self.message_encoding)
        

        