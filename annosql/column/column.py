from typing import Optional, Any, List
from .attribute import ColumnAttribute
from ..model import Model


class _ColumnMeta(type):
    def __or__(cls, other):
        return cls() | other


class Column(object, metaclass=_ColumnMeta):
    datatype: Optional[Any]
    length: Optional[int]
    attributes: List[ColumnAttribute]

    def __init__(self):
        self.datatype = None
        self.length = None
        self.attributes = []

    def define_attr(self, attribute: Any):
        attr_type = type(attribute)
        if self.datatype is None:
            if attr_type in [int, float, str]:
                self.datatype = attr_type
                self.length = int(attribute)
                return self
            elif attribute in [int, float, str, bool, dict, bytes]:
                self.datatype = attribute
                return self
            elif issubclass(attribute, Model):
                self.datatype = attribute
                return self
        elif attr_type is ColumnAttribute:
            self.attributes.append(attribute)
            return self
        else:
            raise ValueError(f"Unknown column attribute {attribute}")

    def __or__(self, other):
        return self.define_attr(other)
