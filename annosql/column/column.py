from typing import Any, List, Optional, Union, get_origin, get_args
from types import GenericAlias, NoneType

from ..model import _TableModelMeta
from .attribute import ColumnAttribute, Length, Unique, PrimaryKey, FKC_ACTION, OnUpdate, OnDelete


class _ColumnMeta(type):
    def __or__(cls, other):
        return cls() | other


class Column(metaclass=_ColumnMeta):
    _datatype: Any
    _length: Optional[int]
    _attributes: List[ColumnAttribute]
    _primary_key: bool = False
    _nullable: Optional[bool]
    _unique: bool = False
    _on_update: FKC_ACTION = "NO ACTION"
    _on_delete: FKC_ACTION = "NO ACTION"

    def __init__(self):
        self._datatype = None
        self._length = None
        self._attributes = []

    @property
    def is_foreign_key(self) -> bool:
        if not self._datatype:
            return False
        return isinstance(self._datatype, _TableModelMeta)

    def define_attr(self, attribute: Any):
        attr_type = type(attribute)
        if self._datatype is None:
            if get_origin(attribute) is Union:
                union_types = list(get_args(attribute))
                if len(union_types) != 2:
                    raise TypeError()
                union_types.remove(NoneType)
                if len(union_types) != 1:
                    raise TypeError()
                self._nullable = True
                return self.define_attr(union_types[0])
            if attribute in [int, float, str, bool, dict, bytes]:
                self._datatype = attribute
                return self
            if isinstance(attribute, _TableModelMeta):
                self._datatype = attribute
                return self
        elif isinstance(attribute, GenericAlias):
            origin = get_origin(attribute)
            if origin is Length:
                self._length = get_args(attribute)[0]
                return self
            if origin is OnUpdate:
                self._on_update = get_args(attribute)[0]
                return self
            if origin is OnDelete:
                self._on_delete = get_args(attribute)[0]
                return self
            raise TypeError('Expected Value')
        elif attr_type is ColumnAttribute:
            if attribute is Unique:
                self._unique = True
            elif attribute is PrimaryKey:
                self._primary_key = True
            else:
                self._attributes.append(attribute)
            return self
        else:
            raise ValueError(f"Unknown column attribute {attribute}")

    def __or__(self, other):
        return self.define_attr(other)
