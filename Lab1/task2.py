from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json

notes = {}
id = 1

class HandleHTTPRequest(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/':
            self.send_response(200)
            self.end_headers()
        elif path == '/echo':
            msg = urlparse(self.path).query
            text = parse_qs(msg)["msg"][0]
            body = json.dumps({"msg": text})
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body.encode())
        elif path.startswith("/notes/"):
            id = path.removeprefix("/notes/")
            if not id.isdigit():
                self.send_response(404)
                self.end_headers()
                return
            id = int(id)
            if id not in notes:
                self.send_response(404)
                self.end_headers()
                return
            body = json.dumps({"id": id, "text": notes[id]})
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        global id 
        if self.path == "/notes":
            if self.headers.get("Content-Type") != "application/json":
                self.send_response(415)
                self.end_headers()
                return
            length = int(self.headers.get("Content-Length"))
            if length == 0:
                self.send_response(404)
                self.end_headers()
                return
            s = self.rfile.read(length)
            try:
                data = json.loads(s)
            except ValueError:
                self.send_response(400)
                self.end_headers()
                return
            if not isinstance(data, dict) or not isinstance(data.get("text"), str):
                self.send_response(400)
                self.end_headers()
                return
            notes[id] = data["text"]
            body = json.dumps({"id": id})
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body.encode())
            id += 1

    def do_DELETE(self):
        if self.path.startswith("/notes/"):
            id = self.path.removeprefix("/notes/")
            if not id.isdigit():
                self.send_response(404)
                self.end_headers()
                return
            id = int(id)
            if id not in notes:
                self.send_response(404)
                self.end_headers()
                return
            del notes[id]
            self.send_response(204)
            self.end_headers()

    def do_PUT(self):
        if self.path == "/notes":
            self.send_response(405)
            self.end_headers()
            return

server = HTTPServer(('0.0.0.0', 8080), HandleHTTPRequest)
server.serve_forever()
