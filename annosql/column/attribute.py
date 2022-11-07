class ColumnAttribute(type):
    pass


class PrimaryKey(metaclass=ColumnAttribute):
    pass


class Unique(metaclass=ColumnAttribute):
    pass
