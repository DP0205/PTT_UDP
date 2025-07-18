

import socket
import threading
import json

TCP_PORT = 9999
UDP_PORT_BASE = 10000
clients = {}  # username → { 'tcp': sock, 'addr': ip, 'udp': port }
current_mic_holder = None

def handle_tcp(conn, addr):
    global current_mic_holder
    conn.settimeout(1.0)  # Enable timeout to detect disconnects
    username = None
    try: #getting the username of the client trying to connect to server
        username = conn.recv(1024).decode().strip()
        udp_port = UDP_PORT_BASE + len(clients)
        clients[username] = {'tcp': conn, 'addr': addr[0], 'udp': udp_port}
        print(f"[+] {username} connected from {addr[0]} (UDP {udp_port})")

        # Send UDP port assignment
        conn.send(json.dumps({"udp_port": udp_port}).encode())  #assigning a unique port num to client

        while True:
            try:
                msg = conn.recv(1024).decode().strip()
                if not msg:
                    break
            except socket.timeout:
                continue
            except:
                break

            if msg == "MIC_REQUEST":
                if current_mic_holder != username:
                    current_mic_holder = username
                    broadcast(f"MIC_GRANTED:{username}")
                    print(f"[MIC] Forcefully granted to {username}")
                    
            elif msg == "MIC_RELEASE":
                if current_mic_holder == username:
                    current_mic_holder = None
                    broadcast("MIC_RELEASED")
                    print(f"[MIC] Released by {username}")
    except:
        print(f"[!] Error with connection from {addr}")
    finally:  #removing the client from user list when they disconnect from server
        if username:
            print(f"[!] {username} disconnected")
            if username in clients:
                del clients[username]
            if current_mic_holder == username:
                current_mic_holder = None
                broadcast("MIC_RELEASED")
        conn.close()

def broadcast(msg):    #sending a control message to all clients over tcp
    for client in list(clients.values()):
        try:
            client['tcp'].send(msg.encode())
        except:
            continue

def udp_forward():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('', UDP_PORT_BASE - 1))  # Voice packets come here
    print(f"[UDP] Listening for voice packets on port {UDP_PORT_BASE - 1}")

    while True:
        try:
            data, addr = udp_sock.recvfrom(2048)
            sender = None
            for u, info in clients.items():
                if info['addr'] == addr[0]:
                    sender = u
                    break
            if sender == current_mic_holder:
                print(f"[VOICE] Forwarding audio from {sender}")
                for u, info in clients.items():
                    if u != sender:
                        udp_sock.sendto(data, (info['addr'], info['udp']))
        except Exception as e:
            print(f"[UDP ERROR] {e}")

def main():
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind(('', TCP_PORT))
    tcp_sock.listen(5)
    print(f"[TCP] Server listening on port {TCP_PORT}")

    threading.Thread(target=udp_forward, daemon=True).start()

    while True:
        conn, addr = tcp_sock.accept()
        threading.Thread(target=handle_tcp, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
