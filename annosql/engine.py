from .dialect import Dialect


class Connection:
    pass


class Engine:
    dialect: Dialect
    connection: Connection

    def __init__(self, conn_str: str):
        pass

    @classmethod
    def __matmul__(cls, conn_str: str):
        return Engine(conn_str)
