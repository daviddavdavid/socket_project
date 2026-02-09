import asyncio
import socket
import client_lib
import click


def client_function(client_list):
    for i, current_client in enumerate(client_list):
        current_client.write_data(f"hi, I am client {i}")
    
    try:
        while True:
            message = current_client.read_message()
            if message is not None:
                print(message)
    except KeyboardInterrupt:
        pass
    finally:
        current_client.close()

    
def create_clients(N, HOST, PORT):
    client_list = [] 
    for i in range(N):
        current_client = client_lib.ClientSocket()
        current_client.create_socket(HOST, PORT)
        current_client.connect_to_server()
        client_list.append(current_client)

    return client_list

@click.group()
def main_group():
    pass

@click.command(name="START")
@click.option("--host", default="127.0.0.1", help="IP adress of the server")
@click.option("--port", default="2444", help="port integer of the server, default is just a random value", type=int)
def start_client(host, port):
    N = 1 # I dont want this as a click value for now since this is just a temporarily option
    # random values

    client_list = create_clients(N, HOST=host, PORT=port)
    client_function(client_list)

main_group.add_command(start_client)

if __name__ == "__main__":
    main_group()