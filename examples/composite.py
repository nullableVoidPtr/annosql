from annosql import Column, Model
from annosql.column.attribute import PrimaryKey, Unique
from annosql.dialect import SQLiteDialect


class Album(Model):
    artist: Column | str | PrimaryKey
    name: Column | str | PrimaryKey
    cover: Column | bytes | Unique


class Song(Model):
    id: Column | int
    album: Column | Album
    name: Column | str


print(SQLiteDialect().ddl_from_model_base(Model))
