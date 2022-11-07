from annosql import Column, Model
from annosql.dialect import SQLiteDialect
from annosql.column.attribute import PrimaryKey, Unique


class Address(Model):
    id: Column | int | PrimaryKey
    email_address: Column | str | Unique

    def __repr__(self):
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


class User(Model):
    id: Column | int | PrimaryKey
    name: Column | str(30)
    fullname: Column | str
    addresses: Column | Address

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

print(SQLiteDialect().ddl_from_model_base(Model))
