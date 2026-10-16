from http.server import BaseHTTPRequestHandler, HTTPServer
import ssl
import os
import json
import secrets
import threading

sessions = {}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.end_headers()
        elif self.path == "/me":
            cookie = self.headers.get("Cookie", "")
            token = cookie.removeprefix("session=") 
            if token in sessions:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({"user": sessions[token]}).encode())
            else:
                self.send_response(401)
                self.end_headers()
        elif self.path == "/whoami":
            self.send_response(200)
            self.end_headers()
            subject = self.request.getpeercert()["subject"]
            for group in subject:
                for name, value in group:
                    if name == "commonName":
                        common_name = value
            self.wfile.write(common_name.encode())
            
    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            if data.get("password") != "netsec":
                self.send_response(401)
                self.end_headers()
                return
            token = secrets.token_hex(16)
            sessions[token] = data.get("user")
            self.send_response(200)
            self.send_header("Set-Cookie", f"session={token}; HttpOnly; Secure")
            self.end_headers()

folder = os.path.dirname(__file__)
cert = os.path.join(folder, "server.crt")
key = os.path.join(folder, "server.key")
cert2 = os.path.join(folder, "ca.crt")

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(cert, key)
server = HTTPServer(("0.0.0.0", 8443), Handler)
server.socket = context.wrap_socket(server.socket, server_side=True)

context2 = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context2.load_cert_chain(cert, key)
context2.verify_mode = ssl.CERT_REQUIRED
context2.load_verify_locations(cert2)
server2 = HTTPServer(("0.0.0.0", 8444), Handler)
server2.socket = context2.wrap_socket(server2.socket, server_side=True)

threading.Thread(target=server.serve_forever).start()
threading.Thread(target=server2.serve_forever).start()