

import socket
import threading
import pyaudio
import tkinter as tk
from pynput import keyboard

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
BUFFER_SIZE = 4096

SERVER_IP = '192.168.1.16'  # <-- Replace with actual server's IPv4 address

SERVER_PORT = 50007

running = True
ptt_pressed = threading.Event()

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                input=True, output=True, frames_per_buffer=CHUNK)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 0))  
def send_audio():
    while running:
        if ptt_pressed.is_set():
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                sock.sendto(data, (SERVER_IP, SERVER_PORT))
            except Exception as e:
                print(f"Send error: {e}")
        else:
            threading.Event().wait(0.01)

def receive_audio():
    while running:
        try:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            stream.write(data)
        except Exception as e:
            if running:
                print(f"Receive error: {e}")
            break

def on_press(key):
    if key == keyboard.Key.space:
        print("Spacebar pressed")
        ptt_pressed.set()

def on_release(key):
    if key == keyboard.Key.space:
        print("Spacebar released")

        ptt_pressed.clear()

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

def on_close():
    global running
    print("Shutting down...")
    running = False
    ptt_pressed.clear()

    try:
        stream.stop_stream()
        stream.close()
        sock.close()
        p.terminate()
    except Exception as e:
        print(f"Cleanup error: {e}")

    root.destroy()

send_thread = threading.Thread(target=send_audio)
recv_thread = threading.Thread(target=receive_audio)
send_thread.start()
recv_thread.start()

root = tk.Tk()
root.title("Push-To-Talk Client")
root.geometry("300x100")
tk.Label(root, text="Hold Spacebar to Talk", font=("Arial", 14)).pack(pady=20)

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

send_thread.join()
recv_thread.join()
listener.stop()
