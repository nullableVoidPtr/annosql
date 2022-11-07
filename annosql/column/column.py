from typing import Optional, Any, List
from .attribute import ColumnAttribute
from ..model import Model


class _ColumnMeta(type):
    def __or__(cls, other):
        return cls() | other


class Column(object, metaclass=_ColumnMeta):
    _datatype: Optional[Any]
    _length: Optional[int]
    _attributes: List[ColumnAttribute]

    def __init__(self):
        self._datatype = None
        self._length = None
        self._attributes = []

    @property
    def is_foreign_key(self) -> bool:
        if not self._datatype:
            return False
        return issubclass(self._datatype, Model)

    def define_attr(self, attribute: Any):
        attr_type = type(attribute)
        if self._datatype is None:
            if attr_type in [int, float, str]:
                self._datatype = attr_type
                self.length = int(attribute)
                return self
            elif attribute in [int, float, str, bool, dict, bytes]:
                self._datatype = attribute
                return self
            elif issubclass(attribute, Model):
                self._datatype = attribute
                return self
        elif attr_type is ColumnAttribute:
            self._attributes.append(attribute)
            return self
        else:
            raise ValueError(f"Unknown column attribute {attribute}")

    def __or__(self, other):
        return self.define_attr(other)
