import socket
import json
import struct
import asyncio
class ClientSocket:
    def __init__(self):
        self.current_socket = None
        self.HOST = None
        self.PORT = None
        self.connected = False
        self._reset()

    def _reset(self):
        self.received_data = b""
        self.content = None
        self.encoded_header = None
        self.json_header_length = None
        self.json_header = None
        self.message_length = None
        self.message_encoding = None
        self.message_type = None
        self.message = None

    def create_socket(self, HOST, PORT):
        if self.current_socket is None:
            self.current_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.HOST = HOST
            self.PORT = PORT
    
    def connect_to_server(self):
        current_socket = self.current_socket
        if self.connected == True:
            raise Exception("SOCKET ALREADY CONNECTED ERROR")
        if current_socket is not None and isinstance(self.HOST, str) and isinstance(self.PORT, int):
            current_socket.connect((self.HOST, self.PORT))
            current_socket.setblocking(False)
            self.connected = True
            return self.connected
        raise Exception("CONNECTION NOT POSSIBLE, HOST AND PORT NOT DEFINED")
    
    def close(self):
        try:
            if self.current_socket:
                self.current_socket.close()
        except OSError as error:
            raise Exception(f"SOCKET CLOSING ERROR BECAUSE OF {error!r}")
        finally:
            self.current_socket = None
            print(f"Connection ended, client closed the socket")


    async def _send_to_server(self, total_message):
        loop = asyncio.get_running_loop()
        if self.current_socket is None:
            raise Exception("SOCKET IS NOT CONNECTED ERROR")
        await loop.sock_sendall(self.current_socket, total_message)

    async def write_data(self, message):
        if not isinstance(message, str):
            raise Exception("WRONG TYPE ERROR, WE ONLY ACCEPT STRINGS")
        encoding = "utf-8"
        encoded_message = message.encode(encoding)
        message_length = len(encoded_message)

        if message_length > 1023:
            raise Exception("MESSAGE IS TOO LARGE ERROR") # Larger messages TBA
        
        encoded_json_header = self._make_header(message_length)
        encoded_json_header_length = len(encoded_json_header)
        protoheader = struct.pack(">H", encoded_json_header_length)

        total_message = protoheader + encoded_json_header + encoded_message
        await self._send_to_server(total_message)

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

    def _json_encode(self):
        if self.json_header == None:
            raise Exception("NO PROTOHEADER FOUND") 
        encoded_json_header = json.dumps(self.json_header).encode("utf-8")
        return encoded_json_header

    def _json_decode(self, encoded_header):
        if encoded_header is None or len(encoded_header) == 0:
            raise Exception("NO JSON HEADER FOUND")
        json_header = json.loads(encoded_header.decode("utf-8"))
        return json_header

    async def _get_data(self):
        loop = asyncio.get_running_loop()
        # TBA server closing
        data = b""
        
        data = await loop.sock_recv(self.current_socket, 1024)
        print(data)
        if data != b"" and data is not None:
            self.received_data += data
            return "Succesful"
        return "Failure" # means that the client has closed the connection
    
    def _read_proto_header(self):
        header_length = 2
        if len(self.received_data) >= 2:
            try:
                self.json_header_length = struct.unpack(">H", self.received_data[:header_length])[0]
                if self.json_header_length <= 0 or self.json_header_length > 1023:
                    raise Exception("Json header length is false")
            except:
                print("Invalid Header Data")
                self._reset()
                return

    def _read_header(self):
        start = 2 # we add both since the buffer also has a protoheader before it
        end = 2 + self.json_header_length 
        encoded_json_header = self.received_data[start:end]
        json_header = self._json_decode(encoded_json_header)

        for key in ["message_length", "message_encoding", "message_type"]:
            if key not in json_header:
                raise Exception("Invalid data in JSON header")

        self.message_length = json_header["message_length"]
        self.message_encoding = json_header["message_encoding"]
        self.message_type = json_header["message_type"]

    def _read_message_content(self):
        if (self.message_length > 1023 or self.message_length <= 0):
            raise Exception("TOO MUCH DATA ERROR: TBA, now we dont accept large or invalid message lengths")
        elif self.message_type != "str":
            raise Exception("NON STRING ERROR: We only accept strings for now")
        elif self.message_encoding != "utf-8":
            raise Exception("NON UTF-8 ENCODING: we only accept utf-8")
        
        # we sum the total lengths of the protoheader the json_header and the message length together
        start = 2 + self.json_header_length
        end = start + self.message_length
        body = self.received_data[start:end]
        self.received_data = self.received_data[end:] # Only now we flush the buffer
        self.message = body.decode(self.message_encoding)
        
    async def read_message(self):
        status = await self._get_data() # The program is meant to wait here till the server has sent something
        print(status)
        if status == "Failure":
            return None # Let the actual server_socket handle closing

        # TBA, finding a better loop to encapsulate messages that have not arrived properly. Now we just discard that
        if self.json_header_length is None:
            if len(self.received_data) < 2:
                print("No protoheader")
                return None # we want it to wait for more
            self._read_proto_header()

        proto_header_length = 2
        if self.json_header_length is not None:
            if len(self.received_data) - proto_header_length < self.json_header_length:
                print(f"No JSON header") 
                return None
            self._read_header()

        if len(self.received_data) - self.json_header_length - proto_header_length < self.message_length:
            print(f"No message found yet, exiting")
            return None
        
        self._read_message_content()
        message = self.message # make it so the values does not go to None because of the reset
        self._reset() # resets all the values so it is ready for the next read cycle
        return message
    

