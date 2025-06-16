

import socket

SERVER_IP = '0.0.0.0'
SERVER_PORT = 50007
BUFFER_SIZE = 4096

clients = set()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))

print(f"Server listening on {SERVER_IP}:{SERVER_PORT}...")

while True:
    try:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        print(f"Received {len(data)} from IP {addr}")
        if addr not in clients:
            print(f"New client! IP {addr}")
            clients.add(addr)

        for client in clients:
            if client != addr:
                print(f"Sending to {len(data)} to client IP {client}")
                sock.sendto(data, client)
    except Exception as e:
        print(f"Server error: {e}")
        break

sock.close()