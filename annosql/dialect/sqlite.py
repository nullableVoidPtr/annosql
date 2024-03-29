from .base import Dialect


class SQLiteDialect(Dialect):
    def __init__(self):
        pass

    def generate_typename(self, typename, length=None):
        return {
            int: "INTEGER",
            str: "TEXT",
            float: "REAL",
            bool: "NUMERIC",
            bytes: "BLOB",
            dict: "TEXT",
        }[typename]
