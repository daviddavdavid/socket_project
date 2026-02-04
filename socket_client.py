import asyncio
import socket


def client_function(socket_list):
    for i, socket in enumerate(socket_list):
        socket.sendall(f"this is socket {str(i)} communicating to the server".encode("utf-8"))
        socket.close()
    

def create_client_sockets(N, HOST, PORT):
    socket_list = []
    for i in range(N):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        socket_list.append(client_socket)

    return socket_list
            
def main():
    N = 2
    # random values
    HOST = "127.0.0.1"
    PORT = 2444

    socket_list = create_client_sockets(N, HOST, PORT)
    client_function(socket_list)


if __name__ == "__main__":
    main()