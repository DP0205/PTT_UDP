import socket
import threading
import json
import os

TCP_PORT = 9999
UDP_BASE_PORT = 5000
BUFFER_SIZE = 4096
CLIENTS_FILE = 'clients.txt'

clients = {}  
current_speaker = None
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
lock = threading.Lock()

def save_clients_to_file():
    with open(CLIENTS_FILE, 'w') as f:
        for user, data in clients.items():
            f.write(f"{user} {data['addr'][0]} {data['udp_port']}\n")

def handle_tcp(conn, addr):
    global current_speaker
    username = conn.recv(1024).decode()
    udp_port = UDP_BASE_PORT + len(clients)
    clients[username] = {'tcp': conn, 'udp_port': udp_port, 'addr': (addr[0], udp_port)}
    save_clients_to_file()

    print(f"[+] {username} connected from {addr[0]}")

    conn.send(json.dumps({'udp_port': udp_port}).encode())

    try:
        while True:
            msg = conn.recv(1024).decode()
            if msg == 'MIC_REQUEST':
                with lock:
                    if current_speaker is None:
                        current_speaker = username
                        broadcast_tcp(f'MIC_GRANTED:{username}')
                    else:
                        conn.send(b'MIC_DENIED')
            elif msg == 'MIC_RELEASE':
                with lock:
                    if current_speaker == username:
                        current_speaker = None
                        broadcast_tcp('MIC_RELEASED')
    except:
        print(f"[-] {username} disconnected.")
        with lock:
            if current_speaker == username:
                current_speaker = None
                broadcast_tcp('MIC_RELEASED')
        if username in clients:
            del clients[username]
            save_clients_to_file()
        conn.close()

def udp_server():
    udp_sock.bind(('', UDP_BASE_PORT))
    print(f"[UDP] Listening on {UDP_BASE_PORT}...")

    while True:
        try:
            data, sender_addr = udp_sock.recvfrom(BUFFER_SIZE)
            sender_user = None
            for user, info in clients.items():
                if info['addr'][0] == sender_addr[0] and info['udp_port'] == sender_addr[1]:
                    sender_user = user
                    break

            if sender_user != current_speaker:
                continue

            for user, info in clients.items():
                if user != sender_user:
                    udp_sock.sendto(data, info['addr'])
        except:
            continue

def broadcast_tcp(message):
    for user in clients:
        try:
            clients[user]['tcp'].send(message.encode())
        except:
            pass

def main():
    if os.path.exists(CLIENTS_FILE):
        os.remove(CLIENTS_FILE)

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind(('', TCP_PORT))
    tcp_sock.listen()
    print(f"[TCP] Listening on {TCP_PORT}...")

    threading.Thread(target=udp_server, daemon=True).start()

    while True:
        conn, addr = tcp_sock.accept()
        threading.Thread(target=handle_tcp, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
