from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse, parse_qs

# In-memory notes storage {id: text} and next id to assign
notes = {}
next_id = 1

# Request handler: one do_<METHOD> function per HTTP method
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Separate the path from the query string (e.g. "/echo" and "msg=...")
        url = urlparse(self.path)
        id_str = url.path[len("/notes/"):]
        # Routing: GET / -> 200
        if url.path == "/":
            self.send_response(200)
            self.end_headers()
        # JSON echo: return the decoded value of the "msg" parameter
        elif url.path == "/echo":
            body = json.dumps({"msg": parse_qs(url.query)["msg"][0]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        # GET /notes/<id>: return the note if the id is numeric and exists
        elif url.path.startswith("/notes/") and id_str.isdigit() and int(id_str) in notes:
            body = json.dumps({"id": int(id_str), "text": notes[int(id_str)]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        # Any other path, missing note or non-numeric id -> 404
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        global next_id
        if self.path != "/notes":
            self.send_response(404)
            self.end_headers()
            return
        # Only JSON bodies are accepted -> otherwise 415
        if self.headers.get("Content-Type") != "application/json":
            self.send_response(415)
            self.end_headers()
            return
        # Read the body (its size is given by Content-Length) and parse the JSON
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        except ValueError:
            data = None
        # Malformed JSON, missing or non-string "text" -> 400
        if not isinstance(data, dict) or not isinstance(data.get("text"), str):
            self.send_response(400)
            self.end_headers()
            return
        # Store the note and return its id -> 201
        notes[next_id] = data["text"]
        body = json.dumps({"id": next_id}).encode()
        next_id += 1
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_DELETE(self):
        # Delete the note if it exists -> 204, otherwise -> 404
        id_str = self.path[len("/notes/"):]
        if self.path.startswith("/notes/") and id_str.isdigit() and int(id_str) in notes:
            del notes[int(id_str)]
            self.send_response(204)
        else:
            self.send_response(404)
        self.end_headers()

    def do_PUT(self):
        # Unsupported method on /notes -> 405
        if self.path.startswith("/notes/"):
            self.send_response(404)
        else:
            self.send_response(405)
        self.end_headers()

# Start the HTTP server on port 8080, listening on all interfaces
HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()