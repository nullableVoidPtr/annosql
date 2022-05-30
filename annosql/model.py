import re
from typing import ClassVar, Sequence

CAMELCASE_PATTERN = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


def camel_to_snake(name):
    return CAMELCASE_PATTERN.sub(r'_\1', name)


class Model:
    _registered_tables: dict = {}

    def __init_subclass__(cls):
        table_name = cls.__tablename__
        if table_name in cls._registered_tables:
            raise ValueError(f"{cls.table_name} already defined")

        cls._registered_tables[table_name] = cls

    @classmethod
    @property
    def __tablename__(cls):
        return camel_to_snake(cls.__name__)

    @classmethod
    @property
    def __primarykey__(cls):
        from .column import Column
        from .column.attribute import PrimaryKey
        keys = {
            name: col
            for name, col in cls.__annotations__.items()
            if type(col) is Column and
            any(attr is PrimaryKey is PrimaryKey for attr in col.attributes)
        }
        return keys

    @staticmethod
    def new_model_base(typename: str = "Model"):
        return type(typename, Model.__bases__, vars(Model).copy())
