import socket
import threading


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.received = []

    def connect(self):
        self.sock.connect((self.host, self.port))
        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        while True:
            try:
                data = self.sock.recv(1024)
                self.received.append(data.decode())
            except:
                pass

    def send(self, txt):
        self.sock.sendall(txt.encode())


if __name__ == '__main__':
    c_1 = Client("192.168.1.103", 51123)
    c_1.connect()
    while True:
        for msg in c_1.received:
            print(msg)
            c_1.received.remove(msg)
        c_1.send(input("c_1>>>"))
