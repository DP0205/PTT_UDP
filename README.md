# PTT_UDP
Developing a Push-To-Talk functionality using UDP to enable communication between two clients through a server
We are using Python's socket module to create a Datagram Socket and establish a connection between the client and server. We use the keyboard module to allow the user to start talking by pushing the spacebar button. 
Audio data starts getting recorded using the PyAudio module and transferred to the sever using the UDP Protocol. This is then sent to the other client where its unwrapped and the audio is heard.

Why was UDP used?
This feature is being developed for a defense communication company and would eventually part of the final product that could be used by defence personnel. Due to the lightweight software and and higher speeds of transmission, both of which are crucial in critical situations, the choice was made to use UDP instead of the more secure TCP
