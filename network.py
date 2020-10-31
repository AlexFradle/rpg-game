import socket
import threading
from entities import Player, Teammate, Enemy, PseudoBullet
import json
from constants import BYTES_RECV


class GameServer:
    def __init__(self, host, port, host_game):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.clients = []
        self.host_game = host_game
        self.players = [self.host_game.player_name]
        self.previous_packet = {}

    def get_init_packet(self):
        return {
            "enemies": {
                k: {"pos": v.get_normalised_pos(self.host_game.board), "size": v.size, "health": v.health}
                for k, v in self.host_game.enemies.items()
            },
            "players": {
                p.name: {
                    "pos": (p.x, p.y) if p.name != self.host_game.player_name else p.get_normalised_pos(self.host_game.board),
                    "num": self.players.index(p.name) + 1
                }
                for p in [self.host_game.player] + list(self.host_game.other_players.values())
            },
            "bullets": {
                n: {
                    k: {"pos": (b.x, b.y), "colour": b.colour, "size": b.width, "damage": b.damage, "from_enemy": b.from_enemy}
                    for k, b in v.items()
                }
                for n, v in self.host_game.bullets.items()
            },
            "maze": self.host_game.board.grid
        }

    def get_synced_data(self, new_data):
        synced = {
            "enemies": {
                k: {
                    "pos": e.get_normalised_pos(self.host_game.board),
                    "size": e.size,
                    "health": e.health if k not in new_data["enemies"] else e.health - new_data["enemies"][k]["health_changed"]
                }
                for k, e in self.host_game.enemies.items()
            },
            "players": {
                p.name: {
                    "pos": (p.x, p.y) if p.name != new_data["player"]["name"] else (new_data["player"]["pos"][0], new_data["player"]["pos"][1]),
                    "num": self.players.index(p.name) + 1
                }
                for p in [self.host_game.player] + list(self.host_game.other_players.values())
            },
            "bullets": {
                n: {
                    k: {"pos": (b.x, b.y), "colour": b.colour, "size": b.width, "damage": b.damage, "from_enemy": b.from_enemy}
                    for k, b in v.items()
                }
                for n, v in self.host_game.bullets.items() if n != new_data["player"]["name"]
            }
        }
        synced["bullets"][new_data["player"]["name"]] = new_data["bullets"][new_data["player"]["name"]]
        return synced

    def update_game_data(self, new_data):
        for k in new_data["enemies"]:
            self.host_game.enemies[k].health = new_data["enemies"][k]["health"]

        for k in new_data["players"]:
            if k != self.host_game.player_name:
                self.host_game.other_players[k].x = new_data["players"][k]["pos"][0] + self.host_game.board.x
                self.host_game.other_players[k].y = new_data["players"][k]["pos"][1] + self.host_game.board.y

        for n in new_data["bullets"]:
            if n != self.host_game.player_name and n in self.host_game.bullets:
                for k in new_data["bullets"][n]:
                    if k in self.host_game.bullets[n]:
                        self.host_game.bullets[n][k].x = new_data["bullets"][n][k]["pos"][0]
                        self.host_game.bullets[n][k].y = new_data["bullets"][n][k]["pos"][1]
                    else:
                        cur_bullet = new_data["bullets"][n][k]
                        self.host_game.bullets[n][k] = PseudoBullet(
                            cur_bullet["pos"][0],
                            cur_bullet["pos"][1],
                            cur_bullet["colour"],
                            cur_bullet["size"],
                            cur_bullet["damage"],
                            cur_bullet["from_enemy"]
                        )
            elif n not in self.host_game.bullets:
                self.host_game.bullets[n] = {
                    a: PseudoBullet(
                        b["pos"][0],
                        b["pos"][1],
                        b["colour"],
                        b["size"],
                        b["damage"],
                        b["from_enemy"]
                    )
                    for a, b in new_data["bullets"][n].items()
                }

        for n in new_data["bullets"]:
            if n != self.host_game.player_name:
                for k in list(self.host_game.bullets[n]):
                    if k not in new_data["bullets"][n]:
                        del self.host_game.bullets[n][k]

    def start(self) -> None:
        """
        Listens for client connections
        :return: None
        """
        self.sock.listen(4)
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
        bytes_num = BYTES_RECV
        while True:
            try:
                # Message sent by client
                data = json.loads(clnt.recv(bytes_num).decode())
                if data["request"] == "CLIENT JOIN":
                    self.players.append(data["payload"]["player_name"])
                    # Send init packet
                    send_data = json.dumps(self.get_init_packet()).encode()
                    self.host_game.other_players[data["payload"]["player_name"]] = Teammate(
                        0,
                        0,
                        data["payload"]["player_name"],
                        self.players.index(data["payload"]["player_name"]) + 1
                    )
                    clnt.send(send_data)
                elif data["request"] == "GET DATA":
                    # Send synced data, update host game with the data
                    synced_data = self.get_synced_data(data["payload"])
                    self.update_game_data(synced_data)
                    clnt.send(json.dumps(synced_data).encode())
            except Exception as e:
                print(e)
                # Client disconnected
                del self.host_game.other_players[self.players[self.clients.index(clnt) + 1]]
                del self.players[self.clients.index(clnt) + 1]
                self.clients.remove(clnt)
                clnt.close()
                return False


class GameClient:
    def __init__(self, host, port, client_game):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.received = []
        self.client_game = client_game
        self.init_packet = {}
        self.previous_packet = {}

    def load_json(self):
        return {
            "player": {
                "name": self.client_game.player_name,
                "pos": self.client_game.player.get_normalised_pos(self.client_game.board)
            },
            "enemies": {
                k: {
                    "health": e.health,
                    "health_changed": 0 if not self.previous_packet or self.previous_packet["enemies"].get(k) is None else self.previous_packet["enemies"][k]["health"] - e.health
                } for k, e in self.client_game.enemies.items()
            },
            "bullets": {
                self.client_game.player_name: {
                    k: {
                        "pos": (b.x, b.y),
                        "colour": b.colour,
                        "size": b.width,
                        "damage": b.damage,
                        "from_enemy": b.from_enemy
                    } for k, b in self.client_game.bullets[self.client_game.player_name].items()
                }
            }
        }

    def update_game_data(self, new_data):
        print(new_data["players"])
        for k in new_data["enemies"]:
            if k in self.client_game.enemies:
                self.client_game.enemies[k].x = new_data["enemies"][k]["pos"][0] + self.client_game.board.x
                self.client_game.enemies[k].y = new_data["enemies"][k]["pos"][1] + self.client_game.board.y
                self.client_game.enemies[k].health = new_data["enemies"][k]["health"]
            else:
                self.client_game.enemies[k] = Enemy(
                    new_data["enemies"][k]["pos"][0] - self.client_game.board.x,
                    new_data["enemies"][k]["pos"][1] - self.client_game.board.y,
                    new_data["enemies"][k]["size"],
                    self.client_game.is_host
                )

        for k in new_data["players"]:
            if k != self.client_game.player_name:
                if k in self.client_game.other_players:
                    self.client_game.other_players[k].x = new_data["players"][k]["pos"][0] + self.client_game.board.x
                    self.client_game.other_players[k].y = new_data["players"][k]["pos"][1] + self.client_game.board.y
                else:
                    self.client_game.other_players[k] = Teammate(
                        new_data["players"][k]["pos"][0] - self.client_game.board.x,
                        new_data["players"][k]["pos"][1] - self.client_game.board.y,
                        k,
                        new_data["players"][k]["num"]
                    )

        for n in new_data["bullets"]:
            if n != self.client_game.player_name:
                for k in new_data["bullets"][n]:
                    if k in self.client_game.bullets[n]:
                        self.client_game.bullets[n][k].x = new_data["bullets"][n][k]["pos"][0]
                        self.client_game.bullets[n][k].y = new_data["bullets"][n][k]["pos"][1]
                    else:
                        cur_bullet = new_data["bullets"][n][k]
                        self.client_game.bullets[n][k] = PseudoBullet(
                            cur_bullet["pos"][0],
                            cur_bullet["pos"][1],
                            cur_bullet["colour"],
                            cur_bullet["size"],
                            cur_bullet["damage"],
                            cur_bullet["from_enemy"]
                        )

        for n in new_data["bullets"]:
            if n != self.client_game.player_name:
                for k in list(self.client_game.bullets[n]):
                    if k not in new_data["bullets"][n]:
                        del self.client_game.bullets[n][k]

    def connect(self):
        self.sock.connect((self.host, self.port))
        self.send(json.dumps({"request": "CLIENT JOIN", "payload": {"player_name": self.client_game.player_name}}).encode())
        self.init_packet = json.loads(self.sock.recv(BYTES_RECV).decode())

        self.client_game.enemies = {
            k: Enemy(v["pos"][0], v["pos"][1], v["size"], self.client_game.is_host)
            for k, v in self.init_packet["enemies"].items()
        }

        for k, e in self.client_game.enemies.items():
            e.change_health_value(self.init_packet["enemies"][k]["health"])

        self.client_game.grid = self.init_packet["maze"]

        self.client_game.other_players = {
            k: Teammate(v["pos"][0], v["pos"][1], k, v["num"])
            for k, v in self.init_packet["players"].items() if k != self.client_game.player_name
        }

        self.client_game.player = Player(
            self.client_game.player_name,
            sorted([self.init_packet["players"][i]["num"] for i in self.init_packet["players"]])[-1] + 1
        )

        self.client_game.bullets = {
            n: {
                k: PseudoBullet(b["pos"][0], b["pos"][1], b["colour"], b["size"], b["damage"], b["from_enemy"])
                for k, b in v.items()
            }
            for n, v in self.init_packet["bullets"].items()
        }
        self.client_game.bullets[self.client_game.player_name] = {}
        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        while True:
            try:
                data = json.loads(self.sock.recv(BYTES_RECV).decode())
                self.previous_packet = data
                self.update_game_data(data)
            except:
                pass

    def send(self, data):
        self.sock.sendall(data)


server_to_client = {
    "enemies": {
        1: {"pos": (100, 100), "type": "large", "health": 45},
        2: {}
    },
    "players": {
        "name": {"pos": (200, 200), "num": 1}
    },
    "bullets": {
        "name": {
            1: {"pos": (50, 50), "colour": (255, 128, 0), "size": 10, "from_enemy": False}
        }
    }
}

client_to_server = {
    "pos": (400, 500),
    "enemies": {},
    "bullets": {}
}
