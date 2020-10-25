import socket
import threading
import json


class GNS:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.clients = []
        self.hosts = []

    def listen(self) -> None:
        """
        Listens for client connections
        :return: None
        """
        self.sock.listen()
        while True:
            # Accepts client connection
            clnt, addr = self.sock.accept()
            # Adds client to list of clients
            self.clients.append(clnt)
            print(f"Connected -> [{addr[0]}:{addr[1]}]")
            # Constantly listens for messages
            threading.Thread(target=self.listen_to_client, args=(clnt, addr), daemon=True).start()

    def listen_to_client(self, clnt: socket.socket, addr: tuple) -> bool:
        """
        Constantly running to listen for messages
        :param clnt: Client to listen for
        :param addr: Address of the client
        :return: ??
        """
        bytes_num = 1024
        while True:
            try:
                # Message sent by client
                data = clnt.recv(bytes_num)
                data = json.loads(data.decode())
                if data["request"] == "GET ALL SERVERS":
                    clnt.send(json.dumps(self.hosts).encode())
                    print(f"Sent all host ports to -> [{addr[0]}:{addr[1]}]")
                elif data["request"] == "HOST ADD":
                    print(f"Added to host list -> [{addr[0]}:{addr[1]}]")
                    self.hosts.append({"name": data["payload"]["name"], "password": data["payload"]["password"], "port": addr[1]})
                    print(self.hosts)
            except:
                # Client disconnected
                print(f"Disconnected -> [{addr[0]}:{addr[1]}]")
                # Removes client from clients list
                self.clients.remove(clnt)
                for i in self.hosts:
                    if i["port"] == addr[1]:
                        self.hosts.remove(i)
                clnt.close()
                return False


if __name__ == '__main__':
    s = GNS("192.168.1.103", 50000)
    s.listen()
