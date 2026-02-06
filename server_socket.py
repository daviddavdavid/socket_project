import asyncio
import socket
import server_lib
import click


async def handle_client(server, client_connection):
    try:
        while True:
            message = await client_connection.read_message()
            if not message:
                break
            print(f"{message}")
            await client_connection.write_data("Hello client")
    except KeyboardInterrupt:
        pass
    finally:
        client_connection.close()
        


async def server_function(HOST, PORT):
    loop = asyncio.get_running_loop()
    global server = server_lib.Server()
    server.create_socket(HOST, PORT)
    
    while True:
        client_connection = await server.accept_client()
        if client_connection != None:
            asyncio.create_task(handle_client(server, client_connection))

def main(ctx):
    # random values
    HOST = "127.0.0.1"
    PORT = 2444
    asyncio.run(server_function("127.0.0.1", 2444))

if __name__ == "__main__":
    main()