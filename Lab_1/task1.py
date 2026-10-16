import socket
import threading

# Create a TCP socket listening on port 9001 on all interfaces
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(("0.0.0.0", 9001))
s.listen()

# Shared key-value store, visible from every connection
store = {}

# Handle a single client connection (each client runs in its own thread)
def handle_client(conn):
    # Framing: TCP is a byte stream, so data is accumulated in a buffer until '\n'
    buffer = b""
    while True:
        data = conn.recv(1024)
        if not data:                 
            break
        buffer += data
        # Extract every complete command (several may arrive in one recv)
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            text = line.decode()  
            # Split only at the first space: command and the rest (spaces kept)               
            parts = text.split(" ", 1)           
            cmd = parts[0]                       

            if cmd == "PING":
                response = "PONG"
            elif cmd == "ECHO":
                response = parts[1]       
            elif cmd == "SET":
                # Split into command, key and value (the value may contain spaces)
                p = text.split(" ", 2)
                if len(p) < 3 or p[2] == "":
                    response = "ERR"
                else:
                    store[p[1]] = p[2]
                    response = "OK"
            elif cmd == "GET":
                if len(parts) < 2 or parts[1] == "":
                    response = "ERR"
                else:
                    response = store.get(parts[1], "NOT_FOUND")
            else:
                response = "ERR"                 

            print(text, "->", response)
            conn.sendall((response + "\n").encode())
    conn.close()

while True:
    conn, addr = s.accept()   
    # Start a new thread for each client to serve them concurrently
    threading.Thread(target=handle_client, args=(conn,)).start()