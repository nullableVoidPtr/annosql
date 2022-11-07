from annosql import Column, Model
from annosql.dialect import SQLiteDialect
from annosql.column.attribute import PrimaryKey, Unique


class Album(Model):
    artist: Column | str | PrimaryKey
    name: Column | str | PrimaryKey
    cover: Column | bytes

breakpoint()

class Song(Model):
    id: Column | int
    album: Column | Album
    name: Column | str


print(SQLiteDialect().ddl_from_model_base(Model))
