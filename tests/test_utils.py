import json
import unittest

from utils.config import ENCODING
from utils.utils import decode_data, encode_data, get_name_by_value


class TestUtils(unittest.TestCase):

    def setUp(self):
        self.data = {
            "test": "data"
        }
        self.bytes = json.dumps(self.data).encode(ENCODING)

    def testDecodeData(self):
        self.assertEqual(decode_data(self.bytes), self.data)

    def testEncodeData(self):
        self.assertEqual(encode_data(self.data), self.bytes)

    def testGetNameByValue(self):
        self.assertEqual(get_name_by_value(self.data, "data"), "test")
