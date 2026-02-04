import asyncio
import socket

async def handle_client(connection, loop):
    try:
        while True:
            data = await loop.sock_recv(connection, 1024)
            if not data:
                break
            print(f"{data.decode("utf-8")}")
    except KeyboardInterrupt:
        raise("Server has ended")
    finally:
        connection.close()


async def server_function(HOST, PORT):
    loop = asyncio.get_event_loop()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    server_socket.setblocking(False)
    while True:
        connection, address = await loop.sock_accept(server_socket)
        connection.setblocking(False)
        if connection != None:
            status = await handle_client(connection, loop)
            
def main():
    # random values
    HOST = "127.0.0.1"
    PORT = 2444
    asyncio.run(server_function("127.0.0.1", 2444))

if __name__ == "__main__":
    main()