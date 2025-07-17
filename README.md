🔊 Room-Based Push-To-Talk (PTT) Voice Communication System over UDP
This project implements a real-time, room-based Push-To-Talk (PTT) voice communication system using Python and UDP sockets. Designed for low-latency local communication, it enables multiple users to join virtual rooms and communicate in a structured way—one speaker at a time, simulating traditional walkie-talkie behavior.

🚀 Features
🔄 Client-Server Architecture with central room and mic arbitration.

📡 UDP-Based Audio Transmission for low-latency, real-time voice streaming.

🧠 Mic Arbitration Logic to ensure only one speaker per room at a time.

👥 Dynamic Room Management — clients can create, join, and invite others.

🖥️ Graphical User Interface (GUI) built with Tkinter for usability.

🎙️ Push-to-Talk Control using spacebar (via pynput).

⚡ Interrupt Functionality — any user can override the current speaker, mimicking real-world walkie-talkies.
