import unittest
from unittest import mock

import philips_air_purifier


class TestKeyExchange(unittest.TestCase):
    def setUp(self):
        with mock.patch('philips_air_purifier.key_exchange.randbits', return_value=15):
            self.dh = philips_air_purifier.KeyExchange('5', '17')

    def test_get_public_key(self):
        expected = '13'
        returned = self.dh.get_public_key()
        self.assertEqual(expected, returned)

    def test_get_exchanged_key(self):
        expected = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        returned = self.dh.get_exchanged_key('8')
        self.assertEqual(expected, returned)


if __name__ == '__main__':
    unittest.main()
