from .base import Dialect
from annosql import Model, Column


class SQLiteDialect(Dialect):
    def __init__(self):
        pass

    def generate_typename(self, typename, length=None):
        return {
            int: "INTEGER",
            str: "TEXT",
            float: "REAL",
            bool: "NUMERIC",
            bytes: "BLOB",
            dict: "TEXT",
        }[typename]

    def ddl_from_model(self, model: type):
        table_name = model.__tablename__
        generated = []
        epilogue = []
        for name, column in model.__annotations__.items():
            if type(column) is not Column:
                continue

            datatype = column.datatype
            # TODO escape col names
            if issubclass(datatype, Model):
                foreign_keys = {}
                for key_name, key_col in datatype.__primarykey__.items():
                    # TODO recursively resolve for PKFK tables
                    foreign_keys[fk_name := f"{name}_{key_name}"] = key_name
                    generated.append(f"{fk_name} {self.generate_typename(key_col.datatype)}")
                epilogue.append(
                    f"FOREIGN KEY ({', '.join(foreign_keys.keys())}) "
                    f"REFERENCES {datatype.__tablename__}({', '.join(foreign_keys.values())})"
                )
            else:
                generated.append(f"{name} {self.generate_typename(column.datatype)}")

        generated += epilogue
        return f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(generated)});"

    def ddl_from_model_base(self, base: type = Model):
        return "\n".join(self.ddl_from_model(table) for table in base._registered_tables.values())

