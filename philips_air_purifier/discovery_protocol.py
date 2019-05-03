import email
import socket
from urllib.parse import urlparse
from xml.etree import ElementTree

import requests


class SSDP:
    def __init__(self, timeout=3):
        self.timeout = timeout
        self.ssdp_group = '239.255.255.250'
        self.ssdp_port = 1900
        self.ssdp_query_template = '\r\n'.join(
            ('M-SEARCH * HTTP / 1.1', 'HOST: {}:{}', 'MAN: "ssdp:discover"', 'MX: 1', 'ST: {}', '', ''))
        self.socket = self._get_ssdp_socket()

    def _get_ssdp_socket(self):
        socket.setdefaulttimeout(self.timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        return s

    def _get_ssdp_query(self, search_target):
        return self.ssdp_query_template.format(self.ssdp_group, self.ssdp_port, search_target)

    def _send_query(self, ssdp_query):
        self.socket.sendto(ssdp_query.encode(), (self.ssdp_group, self.ssdp_port))

    def _get_ssdp_reply(self):
        replies = []
        while True:
            try:
                r = self.socket.recv(4096)
            except socket.timeout:
                break
            replies.append(r.decode())
        return replies

    @staticmethod
    def _parse_ssdp_reply(reply):
        i = reply.find('\n')
        m = email.message_from_string(reply[i + 1:])  # Skip first line of reply
        return dict(m.items())

    def discover(self, search_target='urn:philips-com:device:DiProduct:1'):
        ssdp_query = self._get_ssdp_query(search_target)
        self._send_query(ssdp_query)
        ssdp_replies = [self._parse_ssdp_reply(x) for x in self._get_ssdp_reply()]
        return [UPNPDevice(x.get('LOCATION')) for x in ssdp_replies]


class UPNPDevice:
    def __init__(self, upnp_desc_url):
        self.upnp_desc_url = upnp_desc_url
        self.netloc = urlparse(self.upnp_desc_url).netloc
        self.name_space = {'upnp-1': 'urn:schemas-upnp-org:device-1-0'}
        self.manufacturer = ''
        self.model_name = ''
        self.model_number = ''
        self.uuid = ''
        self._parse_desc()

    def _get_upnp_desc(self):
        r = requests.get(self.upnp_desc_url)
        r.raise_for_status()
        return r.text

    def _parse_desc(self):
        xml = ElementTree.fromstring(self._get_upnp_desc())
        self.manufacturer = xml.find('upnp-1:device/upnp-1:manufacturer', self.name_space).text
        self.model_name = xml.find('upnp-1:device/upnp-1:modelName', self.name_space).text
        self.model_number = xml.find('upnp-1:device/upnp-1:modelNumber', self.name_space).text
        self.uuid = xml.find('upnp-1:device/upnp-1:UDN', self.name_space).text.replace('uuid:', '')

    def get_netloc(self):
        return self.netloc

    def get_id(self):
        return self.uuid

    def get_name(self):
        return ' '.join((self.model_name, self.model_number))

    def get_description(self):
        return ' - '.join((self.manufacturer, self.model_name, self.model_number, self.uuid))
