import hashlib

async def app(scope, receive, send):
    if scope["method"] == "GET":
        if scope["path"] == "/":
            await send({"type":"http.response.start", "status":200, "headers":[[b"alt-svc", b'h3=":4433"']]})
            await send({"type":"http.response.body"})
        elif scope["path"] == "/proto":
            protocol = scope["http_version"]
            proto = "HTTP/" + protocol
            await send({"type":"http.response.start", "status":200})
            await send({"type":"http.response.body", "body":proto.encode()})
    elif scope["method"] == "POST":
        flag = True
        chunks = b''
        while flag:
            event = await receive()
            chunks += event["body"]
            flag = event["more_body"]
        hash_obj = hashlib.sha256(chunks)
        hex_msg = hash_obj.hexdigest()
        await send({"type":"http.response.start", "status":200})
        await send({"type":"http.response.body", "body":hex_msg.encode()})