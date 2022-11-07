import re
from types import new_class
from typing import TYPE_CHECKING, Dict, Type

if TYPE_CHECKING:
    from .column import Column
    from .dialect import Dialect

CAMELCASE_PATTERN = re.compile("((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))")


def camel_to_snake(name):
    return CAMELCASE_PATTERN.sub(r"_\1", name)


class _TableModelMeta(type):
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        schema_model = type(cls)
        assert isinstance(schema_model, _SchemaModelMeta)

        table_name = cls.__tablename__
        if table_name in schema_model._registered_tables:
            raise ValueError(f"{cls.__tablename__} already defined")

        schema_model._registered_tables[table_name] = cls

    @property
    def __tablename__(cls):
        return camel_to_snake(cls.__name__)

    @property
    def __primarykey__(cls) -> Dict[str, "Column"]:
        from .column import Column
        from .column.attribute import PrimaryKey

        keys = {
            name: col
            for name, col in cls.__annotations__.items()
            if type(col) is Column
            and any(attr is PrimaryKey is PrimaryKey for attr in col._attributes)
        }
        return keys

    @property
    def __schema__(cls) -> "_SchemaModelMeta":
        table_meta = type(cls)
        schema_model = type(table_meta)
        assert isinstance(schema_model, _SchemaModelMeta)

        return schema_model


class _SchemaModelMeta(type):
    _registered_tables: Dict = {}
    _table_meta: Type[_TableModelMeta]
    __defaultdialect__: Type["Dialect"]

    def __new__(cls, name, bases, dct):
        if len(bases) == 0:
            if len(dct.get("__annotations__", [])):
                raise TypeError(
                    "_SchemaModelMeta should not be directly used to define tables"
                )
            return super().__new__(cls, name, (type,), dct)

        schema_model = bases[0]
        if not isinstance(schema_model, cls) or len(bases) > 1:
            raise TypeError("Unexpected subclass")

        table_meta = schema_model._table_meta
        return table_meta(name, (), dct)

    def __init__(cls, name, bases, dct, dialect=None):
        if len(bases) == 0:
            super().__init__(name, bases, dct)
            cls._registered_tables = {}

            from .dialect import Dialect, SQLiteDialect

            cls.__defaultdialect__ = dialect or SQLiteDialect

            if not issubclass(cls.__defaultdialect__, Dialect):
                raise TypeError("Expected a subclass of Dialect")

            cls._table_meta = super().__new__(
                cls, f"{cls.__name__}_TableMeta", (_TableModelMeta,), {}  # type: ignore
            )

    def new_base(cls, typename: str = "Model"):
        return new_class(typename, (), {"metaclass": _SchemaModelMeta})

    @property
    def ddl(cls):
        return cls.__defaultdialect__().ddl_from_model_base(Model)


class Model(metaclass=_SchemaModelMeta):
    pass
