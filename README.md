Push-to-Talk (PTT) Communication System Using TCP and UDP


This project implements a Push-to-Talk (PTT) real-time communication system that allows multiple users to participate in voice communication over a local network, similar to traditional walkie-talkies. The system is designed to ensure controlled access to the microphone, permitting only one speaker at a time while allowing all connected users to listen in real-time. It uses a combination of TCP for control signaling and UDP for audio streaming, ensuring both reliability of command messages and low-latency audio transmission.

=>System Architecture Overview
The system is composed of two main components:
Server – Manages client connections, microphone access, and routes audio data.
Client – Allows users to request mic access, send audio if allowed, and receive real-time audio from other users.

=>Threaded Model and Communication Protocol
->TCP (Signaling)
Used to manage control commands:
Username registration
Microphone request and release
Broadcast mic status (e.g., MIC_GRANTED, MIC_RELEASED)
Ensures reliable delivery of control messages.
Handled on the server using a dedicated thread per client.

->UDP (Audio Streaming)
Used to send and receive audio streams.
The client sends audio only if mic access is granted.
The server forwards the received audio to all other clients.
Provides low-latency, connectionless transmission and real-time playback.

->Push-to-Talk Logic
The system enforces a single-speaker model:
When a user presses the spacebar, a MIC_REQUEST is sent.
If the mic is free, the server assigns mic access and broadcasts a MIC_GRANTED message.
The user can now transmit audio via UDP to the server, which forwards it to all listeners.
On spacebar release, the client sends MIC_RELEASE, freeing the mic for others.

This mechanism:
Avoids collisions
Simulates walkie-talkie behavior
Enforces orderly communication

->User Interface
A simple Tkinter-based GUI is included in each client:
Displays connection status
Shows whether the user can speak or must wait
Updates in real time based on server broadcasts

->Color-coded labels:
🟢 Green – Mic access granted (Can Speak)
🔴 Red – Mic denied (Cannot Speak)
⚫ Gray – Disconnected or error
