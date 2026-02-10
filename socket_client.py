import asyncio
import socket
import client_lib
import click
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout 


async def client_messsage_reader(client):
    try:
        while True:
            message = await client.read_message()
            if message is not None:
                print(message)
    except asyncio.CancelledError: # the QUIT command has been initiated
        pass 

async def client_command_control(client):
    session = PromptSession()
    while True:
        with patch_stdout(): # to prevent stdout situations
            client_input = await session.prompt_async("Command: ")

            if client_input.startswith("MSG ") and len(client_input) > 4:
                await client.write_data(message=client_input[4:])
            elif client_input.startswith("QUIT"):
                break
            else:
                print(f"Unknown command: {client_input}")

@click.group()
def main_group():
    pass

async def client_function(host, port):
    # random values
    
    client = client_lib.ClientSocket()
    client.create_socket(HOST=host, PORT=port)
    client.connect_to_server()

    reader_task = asyncio.create_task(client_messsage_reader(client=client))
    writer_task = asyncio.create_task(client_command_control(client=client))

    await writer_task

    if not reader_task.done():
        reader_task.cancel()

    await reader_task # just to let asyncio do the right garbage collecitng

    client.close()

@click.command(name="START")
@click.option("--host", default="127.0.0.1", help="IP adress of the server")
@click.option("--port", default="2444", help="port integer of the server, default is just a random value", type=int)
def start_client(host, port):
   asyncio.run(client_function(host=host, port=port))

main_group.add_command(start_client)

if __name__ == "__main__":
    main_group()