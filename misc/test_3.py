import socket
import json

# test_req = {"request": "HOST ADD", "payload": {"name": "test game", "password": "test password"}}
test_req = {"request": "GET ALL SERVERS", "payload": {}}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("192.168.1.103", 50000))
s.send(json.dumps(test_req).encode())
data = s.recv(2048)
print(data)
s.close()
