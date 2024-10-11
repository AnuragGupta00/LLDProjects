import asyncio
import selectors
import socket
from asyncio import AbstractEventLoop
from selectors import DefaultSelector


async def test_func(x: int):
    await asyncio.sleep(1)
    return x + 3

async def accept_responses(client_connection, client_address, loop: AbstractEventLoop):
        try:
            while True:
                data = await loop.sock_recv(client_connection, 1024)
                print(f"Received Data From {client_address}: {data}")
                await loop.sock_sendall(client_connection, data)
                if data == b'Exit\r\n':
                    raise Exception("Error Occurred")
        except Exception as e:
            print(e)
        finally:
            client_connection.close()

async def create_client_connections(server_socket, loop: AbstractEventLoop):
    while True:
        client_connection, client_address = await loop.sock_accept(server_socket)
        client_connection.setblocking(False)
        print(f"Client Connected {client_address}")
        asyncio.create_task(accept_responses(client_connection, client_address, loop))

async def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    address = ("127.0.0.1", 8000)
    server_socket.bind(address)
    server_socket.setblocking(False)
    server_socket.listen()

    loop = asyncio.get_event_loop()
    await create_client_connections(server_socket, loop)




if __name__ == '__main__':
    asyncio.run(main())