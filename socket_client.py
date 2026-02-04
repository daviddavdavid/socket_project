import asyncio
import socket
import client_lib


def client_function(client_list):
    for i, current_client in enumerate(client_list):
        current_client.write_data(f"hi, I am client {i}")
        current_client.close()
    
def create_clients(N, HOST, PORT):
    client_list = [] 
    for i in range(N):
        current_client = client_lib.client_socket()
        current_client.create_socket(HOST, PORT)
        current_client.connect_to_server()
        client_list.append(current_client)

    return client_list
            
def main():
    N = 2
    # random values
    HOST = "127.0.0.1"
    PORT = 2444

    client_list = create_clients(N, HOST, PORT)
    client_function(client_list)

if __name__ == "__main__":
    main()