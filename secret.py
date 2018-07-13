# -*- coding: utf-8 -*-

import string
import random
import sys
import os
# from tests.profiler import Profiler

# Get path
path = sys.argv[0]
path = os.path.join(os.path.dirname(path), 'cert')

# Bot token
API_TOKEN = ''     # production bot.
TOKEN = ''         # dev bot.

WEBHOOK_HOST = ''
WEBHOOK_PORT = 8443         # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = path + '/webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = path + '/webhook_pkey.pem'  # Path to the ssl private key
WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)


# For encrypt/decrypt strings.
CIPHER_KEY = ''


class Generator:

    def __init__(self):
        self.small = string.ascii_lowercase
        self.big = string.ascii_uppercase
        self.digits = string.digits
        self.spec = string.punctuation

    def shuffle_digits(self, range_=10):
        digits_list = list(self.digits)

        random.shuffle(digits_list)

        first_seq = ''.join([random.choice(digits_list) for x in range(range_)])

        return first_seq

    def shuffle_s_and_b(self, range_=20):
        lett_list = list(self.small + self.big)

        random.shuffle(lett_list)

        second_seq = ''.join([random.choice(lett_list) for x in range(range_)])

        return second_seq

    def shuffle_all(self):
        new_mix = list(self.small + self.big + self.digits + self.spec)

        random.shuffle(new_mix)

        third_seq = ''.join([random.choice(new_mix) for x in range(15)])

        return third_seq

    def mix(self):
        return 'S' + Generator.shuffle_digits(self) + Generator.shuffle_s_and_b(self) + Generator.shuffle_all(self)


generator = Generator()
