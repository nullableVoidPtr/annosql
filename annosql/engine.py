from typing import ClassVar
from .dialect import Dialect, SQLiteDialect

class Connection:
    pass

class Engine:
    dialect: Dialect
    connection: Connection

    def __init__(self, conn_str: str):
        self.dialect = SQLiteDialect
        pass

    @classmethod
    def __matmul__(self, conn_str: str):
        return Engine(conn_str)
