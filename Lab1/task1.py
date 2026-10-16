import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0", 9001))
s.listen()

store = {}

def handle_client(conn):
        buffer = b""
        while True:
            data = conn.recv(4096)
            if data == b"":
                    break
            buffer += data
            while b"\n" in buffer:
                line, buffer = buffer.split(maxsplit=1, sep=b"\n")
                line = line.decode()
                if line == "PING":
                    conn.sendall(b"PONG\n")
                elif line.startswith("ECHO "):
                    line = line.removeprefix("ECHO ")
                    conn.sendall(line.encode() + b"\n")
                elif line.startswith("SET "):
                    line = line.removeprefix("SET ")
                    parts = line.split(maxsplit=1)
                    if len(parts) != 2:
                        conn.sendall(b"ERR\n")
                        continue
                    key, value = parts
                    store[key] = value
                    conn.sendall(b"OK\n")
                elif line.startswith("GET "):
                    line = line.removeprefix("GET ")
                    if line in store:
                        conn.sendall(store[line].encode() + b"\n")
                    else:
                        conn.sendall(b"NOT_FOUND\n")
                else:
                    conn.sendall(b"ERR\n")
        conn.close()

while True:
    conn, addr = s.accept()
    threading.Thread(target=handle_client, args=(conn,)).start()
