import socket
import threading
import json
import tkinter as tk
import pyaudio

SERVER_IP = '127.0.0.1'  # Replace with actual IP
TCP_PORT = 9999
UDP_BASE_PORT = 5000
BUFFER_SIZE = 4096

username = input("Enter your username: ")
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.connect((SERVER_IP, TCP_PORT))
tcp_sock.send(username.encode())
udp_port = json.loads(tcp_sock.recv(1024).decode())['udp_port']

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind(('', udp_port))

# Audio config
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                output=True,
                frames_per_buffer=1024)

mic_allowed = True
space_pressed = False

root = tk.Tk()
root.title(f"PTT Client: {username}")
status_label = tk.Label(root, text="Can Speak", bg='green', fg='white', font=("Arial", 18), width=20)
status_label.pack(pady=20)

def update_mic_status(allowed):
    global mic_allowed
    mic_allowed = allowed
    if allowed:
        status_label.config(text="Can Speak", bg='green')
    else:
        status_label.config(text="Cannot Speak", bg='red')

def listen_tcp():
    while True:
        try:
            msg = tcp_sock.recv(1024).decode()
            if msg.startswith("MIC_GRANTED"):
                speaker = msg.split(":")[1]
                update_mic_status(speaker == username)
            elif msg == "MIC_RELEASED":
                update_mic_status(True)
        except:
            break

def receive_audio():
    while True:
        try:
            data, _ = udp_sock.recvfrom(BUFFER_SIZE)
            stream.write(data)
        except:
            break

def send_audio():
    while True:
        if mic_allowed and space_pressed:
            try:
                data = stream.read(1024, exception_on_overflow=False)
                udp_sock.sendto(data, (SERVER_IP, UDP_BASE_PORT))
            except:
                pass

def on_space_press(event):
    global space_pressed
    if mic_allowed:
        space_pressed = True
        tcp_sock.send(b'MIC_REQUEST')

def on_space_release(event):
    global space_pressed
    space_pressed = False
    tcp_sock.send(b'MIC_RELEASE')

root.bind('<KeyPress-space>', on_space_press)
root.bind('<KeyRelease-space>', on_space_release)

threading.Thread(target=listen_tcp, daemon=True).start()
threading.Thread(target=receive_audio, daemon=True).start()
threading.Thread(target=send_audio, daemon=True).start()

root.mainloop()
