
import socket
import threading
import tkinter as tk
import pyaudio
import json
from pynput import keyboard

SERVER_IP = "192.168.1.16"  # Replace with your server's IP
TCP_PORT = 9999
UDP_SERVER_PORT = 9999
RATE = 44100
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1

mic_allowed = False
mic_pressed = False
udp_port = None
username = input("Enter your name: ").strip()

p = pyaudio.PyAudio()
tcp_sock = None
udp_sock = None

root = tk.Tk()
root.title(f"PTT - {username}")
label = tk.Label(root, text="Connecting...", font=("Arial", 24))
label.pack(padx=20, pady=20)

def update_label(text, color):
    label.config(text=text, fg=color)

def recv_control():
    global mic_allowed
    while True:
        try:
            msg = tcp_sock.recv(1024).decode()
            if msg.startswith("MIC_GRANTED"):
                holder = msg.split(":")[1]
                mic_allowed = (holder == username)
                if mic_pressed and mic_allowed:
                    update_label("Speaking", "green")
                elif not mic_pressed:
                    update_label("Connected", "black")
            elif msg == "MIC_RELEASED":
                mic_allowed = False
                if not mic_pressed:
                    update_label("Connected", "black")
            elif msg == "MIC_DENIED":  #just in case of any exceptions
                mic_allowed = False
                update_label("Connected", "black")
        except:
            update_label("Disconnected", "gray")
            break



def recv_audio():
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    output=True, frames_per_buffer=CHUNK)
    while True:
        try:
            data, _ = udp_sock.recvfrom(2048)
            stream.write(data)
        except:
            break

def send_audio():
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=CHUNK)
    update_label("Speaking", "green")
    print("[AUDIO] Start sending")
    while mic_pressed and mic_allowed:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            udp_sock.sendto(data, (SERVER_IP, UDP_SERVER_PORT))
        except Exception as e:
            print(f"[AUDIO ERROR] {e}")
            break
    stream.stop_stream()
    stream.close()
    update_label("Connected", "black")
    print("[AUDIO] Stop sending")


def on_press(key):
    global mic_pressed
    if key == keyboard.Key.space and not mic_pressed:
        mic_pressed = True
        try:
            tcp_sock.send(b"MIC_REQUEST")
        except:
            pass
        threading.Thread(target=send_audio, daemon=True).start()

def on_release(key):
    global mic_pressed
    if key == keyboard.Key.space and mic_pressed:
        mic_pressed = False
        try:
            tcp_sock.send(b"MIC_RELEASE")
        except:
            pass

def setup():
    global tcp_sock, udp_sock, udp_port

    # TCP connection
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.connect((SERVER_IP, TCP_PORT))
    tcp_sock.send(username.encode())

    data = tcp_sock.recv(1024).decode()
    info = json.loads(data)
    udp_port = info['udp_port']

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('', udp_port))

    threading.Thread(target=recv_control, daemon=True).start()
    threading.Thread(target=recv_audio, daemon=True).start()

    update_label("Connected. Can Speak", "green")

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.daemon = True
    listener.start()

setup()
root.mainloop()
