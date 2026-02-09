import asyncio
import socket
import server_lib
import click
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout # package said to include this to prevent stdout errors

async def handle_client(client_connection):
    try:
        while True:
            message = await client_connection.read_message()
            if not message:
                break
    except KeyboardInterrupt:
        pass
    finally:
        client_connection.close()

async def accept_clients(server):
    client_connection = await server.accept_client()
    if client_connection != None:
        asyncio.create_task(handle_client(client_connection))

     
async def server_function(HOST, PORT):
    server = server_lib.Server()
    server.create_socket(HOST=HOST, PORT=PORT)

    asyncio.create_task(accept_clients(server=server))

    print("Server has started succesfully!")
    session = PromptSession()
    while True:
        with patch_stdout():
            server_input = await session.prompt_async("Command: ")

            if server_input.startswith("MSG ") and len(server_input) > 4:
                if server.client_list == []:
                    print("No active client connection")
                    continue
                client_1 = server.client_list[0]
                if client_1: ## TODO: ensure that this client actually exists, because the address is never removed
                    await client_1.write_data(message=server_input[4:]) # sends the message without the command

            elif server_input.startswith("QUIT"):
                server.close()
                break

            else:
                print(f"Unknown command: {server_input}")

        
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