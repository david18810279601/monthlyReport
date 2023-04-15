import redis
import json


class RedisClient:
    def __init__(self, host='localhost', port=6379, password=None, db=0):
        self.client = redis.Redis(host=host, port=port, password=password, db=db)

    def set_key(self, key, value, ex=None):
        if isinstance(value, dict) or isinstance(value, list):
            value = json.dumps(value)
        self.client.set(key, value, ex)

    def get_key(self, key):
        value = self.client.get(key)
        if value:
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
        return value

    def delete_key(self, key):
        self.client.delete(key)

    def update_key(self, key, value, ex=None):
        old_value = self.get_key(key)
        if old_value:
            if isinstance(old_value, dict):
                old_value.update(value)
                value = old_value
            self.set_key(key, value, ex)