from types import GenericAlias
from typing import Literal

class ColumnAttribute(type):
    pass


class Length(metaclass=ColumnAttribute):
    def __class_getitem__(cls, length: int):
        return GenericAlias(cls, (length,))


class PrimaryKey(metaclass=ColumnAttribute):
    pass


class Unique(metaclass=ColumnAttribute):
    pass


class ForeignKeyClause(metaclass=ColumnAttribute):
    pass


FKC_ACTION = Literal["RESTRICT", "NO ACTION", "CASCADE", "SET NULL", "SET DEFAULT"]
class OnUpdate(ForeignKeyClause, metaclass=ColumnAttribute):
    def __class_getitem__(cls, action: FKC_ACTION):
        return GenericAlias(cls, (action,))


class OnDelete(ForeignKeyClause, metaclass=ColumnAttribute):
    def __class_getitem__(cls, action: FKC_ACTION):
        return GenericAlias(cls, (action,))
