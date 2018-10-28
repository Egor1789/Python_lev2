import unittest
from multiprocessing import Queue

import server


class TestServer(unittest.TestCase):
    class ClientMock:
        def __init__(self, queue: Queue):
            self.q = queue

        def send(self, msg: bytes):
            print("Sending from mock")
            self.q.put(msg)

    def testParseMessage(self):
        ser = server.ChatServer()

        msg_queue = Queue()
        mock = self.ClientMock(msg_queue)

        ser.parse_message({"action": "aawda"}, mock)

        try:
            msg = msg_queue.get(timeout=0.05)
            print("Message from queue", msg)
        except:
            self.fail("Smth wrong with response")


if __name__ == '__main__':
    unittest.main()
