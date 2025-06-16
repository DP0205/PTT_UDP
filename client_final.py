# lwc1.py – Client with mic request/grant handling

import socket
import threading
import pyaudio
import tkinter as tk
from pynput import keyboard

# --- Audio Config ---
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
BUFFER_SIZE = 4096

# --- Server Info ---
SERVER_IP = '192.168.1.16'  # Replace with your server IP
SERVER_PORT = 50007

# --- State Flags ---
running = True
mic_granted = False
mic_requesting = False
status_label = None

# --- PyAudio Setup ---
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                input=True, output=True, frames_per_buffer=CHUNK)

# --- Socket Setup ---
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 0))  # OS assigns port

# --- Send Audio ---
def send_audio():
    while running:
        if mic_granted:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                sock.sendto(data, (SERVER_IP, SERVER_PORT))
            except Exception as e:
                print(f"Send error: {e}")
        else:
            threading.Event().wait(0.01)

# --- Receive Data and Control Messages ---
def receive_handler():
    global mic_granted, mic_requesting, status_label

    while running:
        try:
            data, _ = sock.recvfrom(BUFFER_SIZE)

            if data.startswith(b"CTRL:"):
                message = data.decode().strip()

                if message == "CTRL:PTT_GRANTED":
                    mic_granted = True
                    mic_requesting = False
                    print("Mic granted")
                    if status_label:
                        status_label.config(text="Mic ON: Speak Now", fg="green")

                elif message == "CTRL:MIC_BUSY":
                    mic_granted = False
                    mic_requesting = False
                    print("Mic busy")
                    if status_label:
                        status_label.config(text="Mic Disabled: Someone is Speaking", fg="red")

                elif message == "CTRL:MIC_FREE":
                    mic_granted = False
                    mic_requesting = False
                    print("Mic is now free")
                    if status_label:
                        status_label.config(text="Mic Enabled: Press Spacebar", fg="blue")

            else:
                stream.write(data)

        except Exception as e:
            if running:
                print(f"Receive error: {e}")
            break

# --- Keyboard Events ---
def on_press(key):
    global mic_requesting

    if key == keyboard.Key.space and not mic_requesting and not mic_granted:
        print("Requesting mic...")
        mic_requesting = True
        sock.sendto(b"CTRL:PTT_REQUEST", (SERVER_IP, SERVER_PORT))
        if status_label:
            status_label.config(text="Requesting Mic...", fg="orange")

def on_release(key):
    global mic_granted, mic_requesting

    if key == keyboard.Key.space and mic_granted:
        print("Releasing mic...")
        mic_granted = False
        mic_requesting = False
        sock.sendto(b"CTRL:PTT_RELEASE", (SERVER_IP, SERVER_PORT))
        if status_label:
            status_label.config(text="Mic Enabled: Press Spacebar", fg="blue")

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# --- GUI Setup ---
def on_close():
    global running
    print("Shutting down...")
    running = False
    try:
        stream.stop_stream()
        stream.close()
        sock.close()
        p.terminate()
    except Exception as e:
        print(f"Cleanup error: {e}")
    root.destroy()

root = tk.Tk()
root.title("Push-To-Talk Client")
root.geometry("400x120")

status_label = tk.Label(root, text="Mic Enabled: Press Spacebar", font=("Arial", 12), fg="blue")
status_label.pack(pady=10)
tk.Label(root, text="Hold Spacebar to Talk", font=("Arial", 14)).pack(pady=10)

root.protocol("WM_DELETE_WINDOW", on_close)

# --- Start Threads ---
send_thread = threading.Thread(target=send_audio)
recv_thread = threading.Thread(target=receive_handler)
send_thread.start()
recv_thread.start()
root.mainloop()

# --- Cleanup ---
send_thread.join()
recv_thread.join()
listener.stop()
