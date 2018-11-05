import unittest
from threading import Thread

import client
import server


def up_server():
    server.ChatServer().run()


def up_client(login: str, password: str):
    client.ChatClient(login, password).run()


class TestClient(unittest.TestCase):
    t = Thread(target=up_server, daemon=True)
    t.start()

    def setUp(self):
        self.client = client.ChatClient("log", "pas")

    def tearDown(self):
        self.client.close()
        del self.client

    def checkDictTypesAndKeys(self, data: dict, keys: list, types: list) -> bool:
        if len(keys) != len(types):
            raise Exception("Keys and types len should be equal")

        return all([i in data for i in keys]) and all([type(data[keys[i]]) == types[i] for i in range(len(keys))])

    def testConnect(self):
        try:
            self.client.connect()
        except ConnectionRefusedError:
            self.fail("Connection error")

    def testPresenceSend(self):

        self.client.connect()

        presence = self.client.create_presence()

        required_fields = ["action", "time", "login", "password"]
        required_fields_types = [str, str, str, str]
        self.jimTesting(presence, required_fields, required_fields_types, "presence")

        resp = self.client.send_presence(presence)

        if resp["response"] != 200:
            self.fail("Presence error")

    def jimTesting(self, data: dict, keys: list, types: list, action: str):
        self.assertTrue(self.checkDictTypesAndKeys(data, keys, types))
        self.assertTrue(data["action"] == action)

    def testJimHandler(self):

        self.client.connect()
        resp = self.client.send_presence(self.client.create_presence())
        self.client.token = resp["token"]
        jim = self.client.JIMHandler(self.client)

        # PROBE
        required_fields = ["action", "time", "token"]
        required_fields_types = [str] * len(required_fields)
        self.jimTesting(jim.get_probe(), required_fields, required_fields_types, "probe")

        # MSG
        required_fields = ["action", "time", "token", "to", "from", "message"]
        required_fields_types = [str] * len(required_fields)
        self.jimTesting(jim.get_msg("msg", "to"), required_fields, required_fields_types, "msg")

        # AUTHENTICATE
        required_fields = ["action", "time", "token", "login", "password"]
        required_fields_types = [str] * len(required_fields)
        self.jimTesting(jim.get_authenticate("msg", "to"), required_fields, required_fields_types, "authenticate")

        # TODO All others jim messages
