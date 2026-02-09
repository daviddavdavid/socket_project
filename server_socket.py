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
    server = server_lib.Server()
    server.create_socket(HOST, PORT)
    
    while True:
        client_connection = await server.accept_client()
        if client_connection != None:
            asyncio.create_task(handle_client(server, client_connection))

@click.group()
def main_group():
    pass

@click.command(name="START")
@click.option("--host", default="127.0.0.1", help="IP adress of the server")
@click.option("--port", default="2444", help="port integer of the server, default is just a random value", type=int)
def start_server(host, port):
    asyncio.run(server_function(HOST=host, PORT=port))

main_group.add_command(start_server)

if __name__ == "__main__":
    main_group()