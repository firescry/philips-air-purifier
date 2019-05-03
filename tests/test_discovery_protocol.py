import unittest
from textwrap import dedent
from unittest import mock

import philips_air_purifier


class TestSSDP(unittest.TestCase):
    def setUp(self):
        with mock.patch('philips_air_purifier.SSDP._get_ssdp_socket'):
            self.ssdp = philips_air_purifier.SSDP()

    def test_get_ssdp_query(self):
        expected = ('M-SEARCH * HTTP / 1.1\r\nHOST: 239.255.255.250:1900\r\n'
                    'MAN: "ssdp:discover"\r\nMX: 1\r\nST: urn:philips-com:device:DiProduct:1\r\n\r\n')
        returned = self.ssdp._get_ssdp_query('urn:philips-com:device:DiProduct:1')
        self.assertEqual(expected, returned)

    def test_parse_ssdp_reply(self):
        reply = ('HTTP/1.1 200 OK\r\n'
                 'CACHE-CONTROL: max-age=1800\r\n'
                 'EXT:\r\n'
                 'LOCATION: http://10.0.0.1/upnp/description.xml\r\n'
                 'SERVER: ThreadX/5.6 UPnP/1.1 AirPurifier/3 \r\n'
                 'ST: urn:philips-com:device:DiProduct:1\r\n'
                 'USN: uuid:12345678-1234-1234-1234-123456789012::urn:philips-com:device:DiProduct:1\r\n'
                 'BOOTID.UPNP.ORG: 99\r\n\r\n')
        expected = {
            'BOOTID.UPNP.ORG': '99',
            'CACHE-CONTROL': 'max-age=1800',
            'EXT': '',
            'LOCATION': 'http://10.0.0.1/upnp/description.xml',
            'SERVER': 'ThreadX/5.6 UPnP/1.1 AirPurifier/3 ',
            'ST': 'urn:philips-com:device:DiProduct:1',
            'USN': 'uuid:12345678-1234-1234-1234-123456789012::urn:philips-com:device:DiProduct:1'
        }
        returned = self.ssdp._parse_ssdp_reply(reply)
        self.assertEqual(expected, returned)


class TestUPNPDevice(unittest.TestCase):
    def setUp(self):
        description = dedent('''\
        <?xml version="1.0"?>
        <root xmlns="urn:schemas-upnp-org:device-1-0">
            <specVersion>
                <major>1</major>
                <minor>1</minor>
            </specVersion>
            <device>
                <deviceType>urn:philips-com:device:DiProduct:1</deviceType>
                <friendlyName>AirPurifier</friendlyName>
                <manufacturer>Royal Philips Electronics</manufacturer>
                <modelName>AirPurifier</modelName>
                <modelNumber>AC2729</modelNumber>
                <UDN>uuid:12345678-1234-1234-1234-123456789012</UDN>
                <cppId>1234567890123456</cppId>
            </device>
        </root>''')
        with mock.patch('philips_air_purifier.UPNPDevice._get_upnp_desc', return_value=description):
            self.upnp = philips_air_purifier.UPNPDevice('http://10.0.0.1/upnp/description.xml')

    def test_get_netloc(self):
        expected = '10.0.0.1'
        returned = self.upnp.get_netloc()
        self.assertEqual(expected, returned)

    def test_get_id(self):
        expected = '12345678-1234-1234-1234-123456789012'
        returned = self.upnp.get_id()
        self.assertEqual(expected, returned)

    def test_get_name(self):
        expected = 'AirPurifier AC2729'
        returned = self.upnp.get_name()
        self.assertEqual(expected, returned)

    def test_description(self):
        expected = 'Royal Philips Electronics - AirPurifier - AC2729 - 12345678-1234-1234-1234-123456789012'
        returned = self.upnp.get_description()
        self.assertEqual(expected, returned)


if __name__ == '__main__':
    unittest.main()
