from threading import Lock
from typing import Any, Mapping

from pymongo import MongoClient
from pymongo.database import Database

from configuration.configuration import get_data


class MongoConnectionMeta(type):
    _instances = {}

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class MongoConnection(metaclass=MongoConnectionMeta):

    def __init__(self) -> None:
        self.mongodb_client = MongoClient(get_data()['mongodb']['uri'])

    def get_instance(self) -> Database[Mapping[str, Any] | Any]:
        return self.mongodb_client[get_data()['mongodb']['database']]
