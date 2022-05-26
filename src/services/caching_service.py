import pickle
import zlib

import redis
from threading import Lock
from src.settings import REDIS_HOST, REDIS_PORT


class CachingService:
    def __init__(self):
        self.lock = Lock()

        self.redis_host = REDIS_HOST
        self.redis_port = REDIS_PORT

        self.r = None

        if self.redis_host is None or self.redis_port is None:
            print(f'No redis cache specified, assuming no cache. Host: {self.redis_host}, Port: {self.redis_port}')
            self.r = None

        else:
            try:
                print(f'Initialising Redis for {self.redis_host}...')
                self.r = redis.Redis(host=self.redis_host, port=int(self.redis_port))
                print('Redis connected :)') if self.r.ping() else print('Connection failed :(')

            except Exception as e:
                print(f'Problem initialising redis, assuming no cache: {e}')

    def get(self, key):
        if self.r is None:
            return None

        try:
            with self.lock:
                v = self.r.get(key)
                if v is None:
                    print(f'CACHE MISS: {key}')
                    return None
                return pickle.loads(zlib.decompress(v))
        except Exception as e:
            print(f'Problem initialising redis, assuming no cache: {e}')
            return None

    def put(self, key, value, ex_seconds=3600):  # Default 1 hr? Not sure how often packages are updated...
        if self.r is None:
            return
        try:
            with self.lock:
                d = zlib.compress(pickle.dumps(value))
                self.r.set(key, d, ex_seconds)
        except Exception as e:
            print(f'Problem reading redis, assuming no cache: {e}')
