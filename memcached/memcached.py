#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymemcache.client import base
import json


def json_serializer(key, value):
    if type(value) == str:
        return value, 1
    return json.dumps(value), 2


def json_deserializer(key, value, flags):
    if flags == 1:
        return value
    if flags == 2:
        return json.loads(value)
    raise Exception("Unknown serialization format")


class Memcache:
    def __init__(self):
        self.db = base.Client(('localhost', 11211), serializer=json_serializer, deserializer=json_deserializer)

    def set(self, key, value):
        self.db.set(key, value)

    def get(self, key):
        try:
            value = (self.db.get(key)).decode('utf-8')

        except AttributeError:
            value = self.db.get(key)

        return value

    def del_data(self, key):
        self.db.delete(key)
