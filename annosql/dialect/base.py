from typing import Type, Dict, Any, Tuple
from abc import ABC, abstractmethod
from ..model import _ModelMeta, Model
from ..column import Column


class BaseDialect(ABC):
    @abstractmethod
    def generate_typename(self, typename, length=None):
        pass

    def resolve_foreign_keys(self, prefix, target) -> Dict[str, Tuple[str, Any]]:
        foreign_keys = {}
        for key_name, key_col in target.__primarykey__.items():
            fk_name = f"{prefix}_{key_name}"
            if issubclass(key_col._datatype, _ModelMeta):
                foreign_keys |= self.resolve_foreign_keys(fk_name, key_col._datatype)
            else:
                foreign_keys[fk_name] = (key_name, key_col._datatype)

        return foreign_keys

    def ddl_from_model(self, model: _ModelMeta):
        table_name = model.__tablename__
        generated = []
        epilogue = []
        for name, column in model.__annotations__.items():
            if type(column) is not Column:
                continue

            datatype = column._datatype
            if datatype is None:
                raise TypeError("Column data type is None!")

            # TODO escape col names
            if issubclass(datatype, _ModelMeta):
                foreign_keys = self.resolve_foreign_keys(name, datatype)
                for key_name, (target_name, target_type) in foreign_keys.items():
                    generated.append(f"{key_name} {self.generate_typename(target_type)}")
                epilogue.append(
                    f"CONSTRAINT fk_{datatype.__tablename__} FOREIGN KEY ({', '.join(foreign_keys.keys())}) "
                    f"REFERENCES {datatype.__tablename__}({', '.join(n for n, _ in foreign_keys.values())})"
                )
            else:
                generated.append(f"{name} {self.generate_typename(column._datatype)}")

        primary_keys = model.__primarykey__.keys()
        if len(primary_keys):
            generated.append(f"CONSTRAINT pk_{table_name} PRIMARY KEY({', '.join(primary_keys)})")

        generated += epilogue

        return "CREATE TABLE IF NOT EXISTS " + table_name + "(\n" \
               "\t" + (',\n\t'.join(generated)) + "\n" \
               ");"

    def ddl_from_model_base(self, base: _ModelMeta = Model):
        return "\n".join(self.ddl_from_model(table) for table in base._registered_tables.values())

