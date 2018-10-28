import select
import uuid
from multiprocessing import Queue
from socket import socket

from utils.config import ADDRESS, PORT, LISTEN, SERVER_TIMEOUT, BUF_READ_SIZE
from utils.utils import encode_data, decode_data, get_name_by_value

# import log_config
import logging

# logger = log_config.logger
###ВМесто Logging написал logger = logging. (поскольку иначе не работало)####
logger = logging.getLogger('server')

class ChatServer:

    def __init__(self):
        self.send_queue = Queue()
        self.clients = []
        self.contacts = dict()
        self.s = socket()
        self.jim_handler = self.JIMHandler(self)

    def connect(self) -> None:
        self.s.bind((ADDRESS, PORT))
        self.s.listen(LISTEN)
        self.s.settimeout(SERVER_TIMEOUT)
        ### ЗДЕСЬ#####
        logger.debug('Старт приложения')

    def run(self) -> None:
        self.connect()
        print("Server started")
        while True:
            try:
                # TODO can we do smth with this? Async?
                client, addr = self.s.accept()

                if self.handle_presence(client):
                    self.clients.append(client)
                    print("Client connected:", addr)
                    ### ЗДЕСЬ#####
                    logger.debug('Связь установлена')
            except:
                pass
                ### ЗДЕСЬ#####
                logger.error('Связь не установлена')

            if len(self.clients) > 0:
                try:
                    readable, writable, err = select.select(self.clients, self.clients, [])
                    # TODO Add queues for block and send handles into another processes
                    if len(readable) > 0:
                        self.handle_read_sockets(readable)
                        ### ЗДЕСЬ#####
                        logger.debug ('Сообщение читабельно')

                    if len(writable) > 0:
                        self.handle_write_sockets(writable)
                        ### ЗДЕСЬ#####
                        logger.debug ('Сообщение можно отправить')
                except:
                    pass
                    ### ЗДЕСЬ#####
                    logger.error('Сообщение нельзя прочиттать или отправить')

    def handle_write_sockets(self, writable: list) -> None:
        if not self.send_queue.empty():
            buf = self.send_queue.get()
            for write in writable:
                if write in self.clients:
                    try:
                        write.send(encode_data(buf))
                    except:
                        self.sock_disconnect(write)

    def handle_read_sockets(self, readable: list) -> None:
        for read in readable:
            if read in self.clients:
                try:
                    self.parse_message(decode_data(read.recv(BUF_READ_SIZE)), read)
                except:
                    self.sock_disconnect(read)

    def sock_disconnect(self, sock: socket) -> None:
        sock_name = get_name_by_value(self.contacts, sock)
        print("Client disconnnected.", sock_name)
        self.clients.remove(sock)

    def handle_presence(self, client: socket) -> bool:
        print("Handle presence")
        client.setblocking(True)
        data = decode_data(client.recv(BUF_READ_SIZE))

        response = {
            "response": 400,
            "alert": "Smth went wrong"
        }
        print("Presence received")

        if "action" in data and data["action"] == "presence":
            if "login" in data and "password" in data:
                self.contacts[data["login"]] = client
                response["response"] = 200
                response["token"] = str(uuid.uuid4())
                print("All clear")

        print(self.contacts)

        client.send(encode_data(response))

        return response["response"] == 200

    def parse_message(self, message: dict, sender: socket) -> None:
        msg_handlers = self.jim_handler.get_handlers()

        if "action" in message and message["action"] in msg_handlers:
            msg_handlers[message["action"]](message, sender)
        else:
            msg_handlers["error"](message, sender)

    class JIMHandler:

        def __init__(self, server):
            self.server = server
            self.get_error_response = lambda code, error: {"response": code, "error": error}

        def handle_probe(self, message: dict, sender: socket) -> None:
            pass

        def handle_msg(self, message: dict, sender: socket) -> None:
            if message["to"] in self.server.contacts:
                to = self.server.contacts[message["to"]]
                to.send(encode_data(message))
            else:
                sender.send(encode_data(self.get_error_response(404, f"User <{message['to']}> not found")))

        def handle_quit(self, message: dict, sender: socket) -> None:
            pass

        def handle_authenticate(self, message: dict, sender: socket) -> None:
            pass

        def handle_join(self, message: dict, sender: socket) -> None:
            pass

        def handle_leave(self, message: dict, sender: socket) -> None:
            pass

        def handle_check_contact(self, message: dict, sender: socket) -> None:
            pass

        def handle_delete_chat(self, message: dict, sender: socket) -> None:
            pass

        def handle_create_chat(self, message: dict, sender: socket) -> None:
            pass

        def handle_error(self, message: dict, sender: socket) -> None:
            response = {
                "response": 404,
                "error": "This action not found"
            }

            response.update(message)
            sender.send(encode_data(response))

        def get_handlers(self):
            return {
                "probe": self.handle_probe,
                "msg": self.handle_msg,
                "quit": self.handle_quit,
                "authenticate": self.handle_authenticate,
                "join": self.handle_join,
                "leave": self.handle_leave,
                "check_contact": self.handle_check_contact,
                "delete_chat": self.handle_delete_chat,
                "create_chat": self.handle_create_chat,
                "error": self.handle_error,
            }


if __name__ == '__main__':
    ChatServer().run()
