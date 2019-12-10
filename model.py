from __future__ import annotations
from pony.orm import Required, Optional, Set, PrimaryKey, Json
from pydantic import BaseModel, create_model
from typing import Literal, Type, Any, Dict
from inspect import signature, _empty

OPERATIONS = ("create", "show", "get", "select", "update")
LITOPERATIONS = Literal["create", "show", "get", "select", "update"]

class Model:
    is_popy_model = True

    @classmethod
    def get_fields(cls):
        return {field: value
                for field, value in cls.__dict__.items()
                if isinstance(value, (Required, Optional, Set, PrimaryKey))}

    @classmethod
    def pydantic_model(cls, operation: LITOPERATIONS, all_models: Dict[str, Type[Model]]) -> Type[BaseModel]:
        model_name = cls.__name__.capitalize()
        schema_name = f"{operation.capitalize()}{model_name}Schema"
        if operation == "create":
            kwargs = {}
            if hasattr(cls, "create_preparation"):
                sign = signature(cls.create_preparation).parameters
                for field, parameter in sign.items():
                    if parameter.annotation is _empty:
                        attr_type = Any
                    else:
                        attr_type = parameter.annotation
                    if parameter.default is _empty:
                        attr_default = Ellipsis
                    else:
                        attr_default = parameter.default
                    kwargs[field] = (attr_type, attr_default)
            else:
                original_fields = cls.get_fields()
                for field, parameter in original_fields.items():
                    if isinstance(parameter.py_type, str):
                        attr_type = all_models[parameter.py_type]
                    elif isinstance(parameter.py_type, Json):
                        attr_type = Any
                    else:
                        attr_type = parameter.py_type
                    if "default" in parameter.kwargs:
                        attr_default = parameter.kwargs["default"]
                    else:
                        attr_default = Ellipsis
                    kwargs[field] = (attr_type, attr_default)
            return create_model(schema_name, **kwargs)
        elif operation == "show":
            # TODO: extend creation model
            return create_model(schema_name, **{})
        elif operation == "get":
            return create_model(schema_name, **{})
        elif operation == "select":
            return create_model(schema_name, **{})
        elif operation == "update":
            return create_model(schema_name, **{})
        else:
            return BaseModel

    def generate_operation(self):
        pass
