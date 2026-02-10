import asyncio
import socket
import server_lib
import click
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout 

async def handle_client(client_connection, shutdown_event):
    while not shutdown_event.is_set():
        try:
            message = await asyncio.wait_for(client_connection.read_message(), 
                                            timeout=0.5)
            if message is None or message == b"":
                break # No shutdown event because we only want the client to disconnect
            else:
                print(f"client: {message}")
        except asyncio.TimeoutError:
            continue
    
    client_connection.close()

async def accept_clients(server, shutdown_event):
    tasked_clients = []
    while not shutdown_event.is_set():
        try: 
            client_connection = await asyncio.wait_for(server.accept_client(), timeout=0.5)
            if client_connection is not None:
                current_client_task = asyncio.create_task(handle_client(client_connection=client_connection, shutdown_event=shutdown_event))
                tasked_clients.append(current_client_task)
        except asyncio.TimeoutError:
            continue

    if tasked_clients != []:
        for task in tasked_clients:
            await task
    

async def command_handling(server):
    session = PromptSession()
    while True:
        with patch_stdout(): # to prevent stdout situations
            server_input = await session.prompt_async("Command: ")

            if server_input.startswith("MSG ") and len(server_input) > 4:
                if server.client_list == []:
                    print("No active client connection")
                    continue
                client_1 = server.client_list[0]
                if client_1: ## TODO: ensure that this client actually exists, because the address is never removed
                    await client_1.write_data(message=server_input[4:]) # sends the message without the command

            elif server_input.startswith("QUIT"):
                print("Iniating server closing procedure...") # should notify clients first and then let them close so I dont get any weird errors
                break

            else:
                print(f"Unknown command: {server_input}")

async def server_function(HOST, PORT):
    server = server_lib.Server()
    server.create_socket(HOST=HOST, PORT=PORT)

    shutdown_event = asyncio.Event()

    reader_task = asyncio.create_task(accept_clients(server=server, shutdown_event=shutdown_event))
    writer_tasks = asyncio.create_task(command_handling(server=server))
    print("Server has started succesfully!")

    await writer_tasks
    shutdown_event.set()
    await reader_task
    server.close()
    
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