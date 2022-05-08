from secrets import randbits

# Pre-shared values for Diffie-Hellman key exchange - Philips Air Purifier
PHILIPS_BASE = ('a4d1cbd5c3fd34126765a442efb99905f8104dd258ac507fd6406cff14266d31'
                '266fea1e5c41564b777e690f5504f213160217b4b01b886a5e91547f9e2749f4'
                'd7fbd7d3b9a92ee1909d0d2263f80a76a6a24c087a091f531dbf0a0169b6a28a'
                'd662a4d18e73afa32d779d5918d08bc8858f4dcef97c2a24855e6eeb22b3b2e5')
PHILIPS_MOD = ('b10b8f96a080e01dde92de5eae5d54ec52c99fbcfb06a3c69a6a9dca52d23b61'
               '6073e28675a23d189838ef1e2ee652c013ecb4aea906112324975c3cd49b83bf'
               'accbdd7d90c4bd7098488e9c219a73724effd6fae5644738faa31a4ff55bccc0'
               'a151af5f0dc8b4bd45bf37df365c1a65e68cfda76d4da708df1fb2bc2e4a4371')


class KeyExchange:
    def __init__(self, g=PHILIPS_BASE, p=PHILIPS_MOD):
        self.g = int(g, 16)
        self.p = int(p, 16)
        self.a = randbits(1024)

    def get_public_key(self):
        public_key = pow(self.g, self.a, self.p)
        return format(public_key, 'x')

    def get_exchanged_key(self, peer_pub_key):
        peer_pub_key = int(peer_pub_key, 16)
        exchanged_key = pow(peer_pub_key, self.a, self.p)
        return exchanged_key.to_bytes(128, 'big')[:16]
