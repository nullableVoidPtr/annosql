from abc import ABC, abstractmethod
from annosql import Model, Column


class Dialect(ABC):
    @abstractmethod
    def generate_typename(self, typename, length=None):
        pass

    def resolve_foreign_keys(self, prefix, target):
        foreign_keys = {}
        for key_name, key_col in target.__primarykey__.items():
            fk_name = f"{prefix}_{key_name}"
            if issubclass(key_col.datatype, Model):
                foreign_keys |= self.resolve_foreign_keys(fk_name, key_col.datatype)
            else:
                foreign_keys[fk_name] = (key_name, key_col.datatype)

        return foreign_keys

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
                foreign_keys = self.resolve_foreign_keys(name, datatype)
                for key_name, (target_name, target_type) in foreign_keys.items():
                    generated.append(f"{key_name} {self.generate_typename(target_type)}")
                epilogue.append(
                    f"FOREIGN KEY ({', '.join(foreign_keys.keys())}) "
                    f"REFERENCES {datatype.__tablename__}({', '.join(n for n, _ in foreign_keys.values())})"
                )
            else:
                generated.append(f"{name} {self.generate_typename(column.datatype)}")

        generated += epilogue
        return f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(generated)});"

    def ddl_from_model_base(self, base: type = Model):
        return "\n".join(self.ddl_from_model(table) for table in base._registered_tables.values())

