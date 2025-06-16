
import socket
import time

SERVER_IP = '0.0.0.0'  #Set to IP of the server device
SERVER_PORT = 50007
BUFFER_SIZE = 4096

clients = set()
current_speaker = None
last_packet_time = {}
MIC_TIMEOUT = 2  # seconds to auto-release mic

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))

print(f"Server listening on {SERVER_IP}:{SERVER_PORT}...")

while True:
    try:
        data, addr = sock.recvfrom(BUFFER_SIZE)

        if addr not in clients:
            clients.add(addr)

        if data.startswith(b"CTRL:"):
            message = data.decode().strip()

            if message == "CTRL:PTT_REQUEST":
                if current_speaker is None:
                    current_speaker = addr
                    last_packet_time[addr] = time.time()
                    print(f"Mic granted to {addr}")
                    sock.sendto(b"CTRL:PTT_GRANTED", addr)
                    for client in clients:
                        if client != addr:
                            sock.sendto(b"CTRL:MIC_BUSY", client)
                else:
                    sock.sendto(b"CTRL:MIC_BUSY", addr)

            elif message == "CTRL:PTT_RELEASE":
                if addr == current_speaker:
                    print(f"{addr} released the mic.")
                    current_speaker = None
                    for client in clients:
                        sock.sendto(b"CTRL:MIC_FREE", client)

            continue

        if addr == current_speaker:
            last_packet_time[addr] = time.time()
            for client in clients:
                if client != addr:
                    sock.sendto(data, client)
        else:
            pass

        if current_speaker and time.time() - last_packet_time.get(current_speaker, 0) > MIC_TIMEOUT:
            print(f"Mic timeout: {current_speaker}")
            current_speaker = None
            for client in clients:
                sock.sendto(b"CTRL:MIC_FREE", client)

    except Exception as e:
        print(f"Server error: {e}")
        break

sock.close()
