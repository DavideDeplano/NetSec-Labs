from http.server import HTTPServer, BaseHTTPRequestHandler
import secrets

class HandleHTTPRequest(BaseHTTPRequestHandler):
    token = b''

    def do_GET(self):
        global token
        if self.path == "/":
            self.send_response(200)
            self.end_headers()
        elif self.path == "/claim":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(token)
        
    def do_POST(self):
        global token 
        if self.path == "/claim":
            length = int(self.headers.get("Content-Length"))
            token = self.rfile.read(length)
            self.send_response(200)
            self.end_headers()

server = HTTPServer(('0.0.0.0', 8090), HandleHTTPRequest)
server.serve_forever()