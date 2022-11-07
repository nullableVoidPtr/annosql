class ColumnAttribute(type):
    pass


class PrimaryKey(metaclass=ColumnAttribute):
    pass


class Unique(metaclass=ColumnAttribute):
    pass

class ForeignKeyAttribute(ColumnAttribute):
    pass
