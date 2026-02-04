import asyncio
import socket
import server_lib
async def handle_client(server):
    try:
        while True:
            message = await server.read_message()
            if not message:
                break
            print(f"{message}")
    except KeyboardInterrupt:
        raise("Server has ended")
    finally:
        server.close()


async def server_function(HOST, PORT):
    loop = asyncio.get_event_loop()
    server = server_lib.server()
    server.create_socket()
    
    while True:
        await server.accept_client()
        if server.connection != None:
            await handle_client(server.connection, loop)
            
def main():
    # random values
    HOST = "127.0.0.1"
    PORT = 2444
    asyncio.run(server_function("127.0.0.1", 2444))

if __name__ == "__main__":
    main()