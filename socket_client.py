import asyncio
import socket
import client_lib
import click
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout 


async def client_messsage_reader(client, shutdown_event):
     while not shutdown_event.is_set():
        try:
            message = await asyncio.wait_for(client.read_message(), timeout=0.5)
            if message == "SERVER_SHUTDOWN":
                print("Server has shut down, iniating closing procedure...")
                shutdown_event.set()
                break
            elif message == b"" or message is None:
                shutdown_event.set()
                break
            else:
                print(f"Server: {message}")
        
        except asyncio.TimeoutError: # the QUIT command has been initiated
            continue 


async def client_command_control(client, shutdown_event):
    session = PromptSession()
    while not shutdown_event.is_set(): # just in case
        with patch_stdout(): 

            client_input_task = asyncio.create_task(session.prompt_async("Command: "))
            shutdown_input = asyncio.create_task(shutdown_event.wait())

            done, pending = await asyncio.wait(
                {client_input_task, shutdown_input},  return_when=asyncio.FIRST_COMPLETED
            )

            if shutdown_input in done:
                client_input_task.cancel()
                try:
                    await client_input_task
                except asyncio.CancelledError:
                    pass
                break
            elif client_input_task in done:
                try:
                    client_input = client_input_task.result()
                except asyncio.CancelledError: # Just in case, realistically it should not trigger
                    break

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

    shutdown_task = asyncio.Event()

    reader_task = asyncio.create_task(client_messsage_reader(client=client, shutdown_event=shutdown_task))
    writer_task = asyncio.create_task(client_command_control(client=client, shutdown_event=shutdown_task))

    await writer_task
    shutdown_task.set()
    await reader_task 
    client.close()

@click.command(name="START")
@click.option("--host", default="127.0.0.1", help="IP adress of the server")
@click.option("--port", default="2444", help="port integer of the server, default is just a random value", type=int)
def start_client(host, port):
   asyncio.run(client_function(host=host, port=port))

main_group.add_command(start_client)

if __name__ == "__main__":
    main_group()