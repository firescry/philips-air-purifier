import json
from base64 import b64decode, b64encode

import requests
from pyaes import AESModeOfOperationCBC, Decrypter, Encrypter

from .key_exchange import KeyExchange

PHILIPS_API_ENDPOINTS = {
    'firmware': 'http://{}/di/v1/products/0/firmware',
    'security': 'http://{}/di/v1/products/0/security',
    'userinfo': 'http://{}/di/v1/products/0/userinfo',
    'wifi': 'http://{}/di/v1/products/0/wifi',
    'air': 'http://{}/di/v1/products/1/air',
    'device': 'http://{}/di/v1/products/1/device',
    'filter': 'http://{}/di/v1/products/1/fltsts'
}

PHILIPS_ERROR_CODES = {
    32768: 'Water tank is removed',
    49408: 'Water refill alert',
    49411: 'Pre-filter and wick cleaning alert'
}


class AirPurifier:
    def __init__(self, ip):
        self.api_endpoints = {x: PHILIPS_API_ENDPOINTS[x].format(ip) for x in PHILIPS_API_ENDPOINTS}
        self.session_key = b''
        self._set_session_key()

    def _api_put(self, endpoint, data, encrypted_data=True):
        data = data if encrypted_data else json.dumps(data)
        r = requests.put(self.api_endpoints[endpoint], data=data)
        r.raise_for_status()
        return r.text if encrypted_data else r.json()

    def _api_get(self, endpoint):
        r = requests.get(self.api_endpoints[endpoint])
        r.raise_for_status()
        return r.text

    def _set_session_key(self):
        kex = KeyExchange()
        resp = self._api_put('security', {'diffie': kex.get_public_key()}, False)
        tmp_key = kex.get_exchanged_key(resp['hellman'])
        dec = Decrypter(AESModeOfOperationCBC(tmp_key))
        self.session_key += dec.feed(bytes.fromhex(resp['key']))
        self.session_key += dec.feed()

    def _decrypt(self, encrypted_message):
        dec = Decrypter(AESModeOfOperationCBC(self.session_key))
        message = dec.feed(b64decode(encrypted_message))
        message += dec.feed()
        return json.loads(message[2:].decode())

    def _encrypt(self, data):
        enc = Encrypter(AESModeOfOperationCBC(self.session_key))
        message = '\n\n' + json.dumps(data)
        enc_message = enc.feed(message)
        enc_message += enc.feed()
        return b64encode(enc_message)

    def is_powered_on(self):
        data = self._decrypt(self._api_get('air'))
        return data.get('pwr') == '1'

    def is_locked(self):
        data = self._decrypt(self._api_get('air'))
        return data.get('cl')

    def is_humidifier_enabled(self):
        data = self._decrypt(self._api_get('air'))
        return 'H' in data.get('func')

    def is_display_on(self):
        data = self._decrypt(self._api_get('air'))
        return data.get('uil') == '1'

    def get_temperature(self):
        data = self._decrypt(self._api_get('air'))
        return data.get('temp')

    def get_humidity(self):
        data = self._decrypt(self._api_get('air'))
        return data.get('rh')

    def get_desired_humidity(self):
        data = self._decrypt(self._api_get('air'))
        return data.get('rhset')

    def get_pm25_level(self):
        data = self._decrypt(self._api_get('air'))
        return data.get('pm25')

    def get_allergen_index(self):
        data = self._decrypt(self._api_get('air'))
        return data.get('iaql')

    def get_brightness(self):
        data = self._decrypt(self._api_get('air'))
        return data.get('aqil')

    def get_error_code(self):
        data = self._decrypt(self._api_get('air'))
        return data.get('err')

    def get_water_level(self):
        data = self._decrypt(self._api_get('air'))
        return data.get('wl')

    def get_fan_speed(self):
        data = self._decrypt(self._api_get('air'))
        return data.get('om')

    def get_mode(self):
        data = self._decrypt(self._api_get('air'))
        return data.get('mode')

    def get_timer(self):
        data = self._decrypt(self._api_get('air'))
        return data.get('dtrs')

    def get_display_mode(self):
        data = self._decrypt(self._api_get('air'))
        return data.get('ddp')

    def power_on(self):
        if not self.is_powered_on():
            data = {'pwr': '1'}
            self._api_put('air', self._encrypt(data))

    def power_off(self):
        if self.is_powered_on():
            data = {'pwr': '0'}
            self._api_put('air', self._encrypt(data))

    def turn_display_on(self):
        if not self.is_display_on():
            data = {'uil': '1'}
            self._api_put('air', self._encrypt(data))

    def turn_display_off(self):
        if self.is_display_on():
            data = {'uil': '0'}
            self._api_put('air', self._encrypt(data))

    def lock(self):
        if not self.is_locked():
            data = {'cl': True}
            self._api_put('air', self._encrypt(data))

    def unlock(self):
        if self.is_locked():
            data = {'cl': False}
            self._api_put('air', self._encrypt(data))

    def enable_humidifier(self):
        if not self.is_humidifier_enabled():
            data = {'func': 'PH'}
            self._api_put('air', self._encrypt(data))

    def disable_humidifier(self):
        if self.is_humidifier_enabled():
            data = {'func': 'P'}
            self._api_put('air', self._encrypt(data))

    def set_desired_humidity(self, humidity):
        if humidity != self.get_desired_humidity():
            data = {'rhset': humidity}
            self._api_put('air', self._encrypt(data))

    def set_brightness(self, brightness):
        if brightness != self.get_brightness():
            data = {'aqil': brightness}
            self._api_put('air', self._encrypt(data))

    def set_fan_speed(self, fan_speed):
        if fan_speed != self.get_fan_speed():
            data = {'om': fan_speed}
            self._api_put('air', self._encrypt(data))

    def set_mode(self, mode):
        if mode != self.get_mode():
            data = {'mode': mode}
            self._api_put('air', self._encrypt(data))

    def set_timer(self, time):
        data = {'dt': time}
        self._api_put('air', self._encrypt(data))

    def set_display_mode(self, mode):
        if mode != self.get_display_mode():
            data = {'ddp': mode}
            self._api_put('air', self._encrypt(data))
