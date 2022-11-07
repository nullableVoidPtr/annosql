import re
from typing import TYPE_CHECKING, Dict
from types import new_class
if TYPE_CHECKING:
    from .column import Column

CAMELCASE_PATTERN = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


def camel_to_snake(name):
    return CAMELCASE_PATTERN.sub(r'_\1', name)


class _DatabaseModelMeta():
    @classmethod
    def new_base(cls, typename: str = "Model"):
        return new_class(typename, (cls,), {'metaclass': _ModelMeta})


class _TableModelMeta():
    @classmethod
    @property
    def __tablename__(cls):
        return camel_to_snake(cls.__name__)

    @classmethod
    @property
    def __primarykey__(cls) -> Dict[str, "Column"]:
        from .column import Column
        from .column.attribute import PrimaryKey
        keys = {
            name: col
            for name, col in cls.__annotations__.items()
            if type(col) is Column and
            any(attr is PrimaryKey is PrimaryKey for attr in col._attributes)
        }
        return keys



class _ModelMeta(type):
    _registered_tables: Dict = {}

    def __new__(cls, name, bases, dct):
        print("_ModelMeta.__new__", cls, name, bases, dct)

        if len(bases) == 0:
            raise TypeError("Expected some bases")

        if len(bases) == 1:
            if bases[0] == _DatabaseModelMeta:
                if dct.get('__annotations__') is not None and len(dct['__annotations__']):
                    raise TypeError("_ModelMeta should not be used to define tables")
                return super().__new__(cls, name, (type, *bases), dct)

            db_model = bases[0]
            table_model = super().__new__(db_model, name, (_TableModelMeta,), dct)
            cls.__init__(table_model, name, (db_model, _TableModelMeta), dct)
            return table_model

        raise TypeError("Table models should not be subclassed")

    def __init__(cls, name, bases, dct):
        print("_ModelMeta.__init__", cls, name, bases, dct)
        if len(bases) == 1:
            super().__init__(name, bases, dct)
            cls._registered_tables = {}
        elif len(bases) == 2:
            db_model = type(cls)
            table_name = cls.__tablename__
            if table_name in cls._registered_tables:
                raise ValueError(f"{cls.__tablename__} already defined")

            db_model._registered_tables[table_name] = cls
        else:
            raise TypeError("Table models should not be subclassed")


    @classmethod
    @property
    def ddl(cls):
        print(cls.__dialect__().ddl_from_model_base(Model))


class Model(_DatabaseModelMeta, metaclass=_ModelMeta):
    pass
