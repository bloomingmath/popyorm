from __future__ import annotations
from pony.orm import Required, Optional, Set, PrimaryKey, Json, Database
from pydantic import BaseModel, create_model
from typing import Literal, Type, Any, Dict, Callable
from inspect import signature, _empty

SCHEMAS = ("create", "show", "get", "select", "update")
LITSCHEMAS = Literal["create", "show", "get", "select", "update"]

OPERATIONS = ("create", "get", "select", "update", "delete")
LITOPERATIONS = Literal["create", "get", "select", "update", "delete"]


class Model:
    is_popy_model = True

    @classmethod
    def get_fields(cls):
        return {field: value
                for field, value in cls.__dict__.items()
                if isinstance(value, (Required, Optional, Set, PrimaryKey))}

    @classmethod
    def pydantic_model(cls, schema_name: LITSCHEMAS, all_models: Dict[str, Type[Model]]) -> Type[BaseModel]:
        model_name = cls.__name__
        model = all_models[model_name]
        if hasattr(model, f"{schema_name}_preparation"):
            kwargs = kwargs_from_prep(getattr(model, f"{schema_name}_preparation"))
        else:
            kwargs = kwargs_from_cls(cls, all_models)
        schema_name = f"{schema_name.capitalize()}{model_name}Schema"
        pydantic_model = create_model(schema_name, **kwargs)
        setattr(pydantic_model, "is_a_pydantic_model", True)
        return pydantic_model

    @classmethod
    def generate_operation(cls, operation_name: LITOPERATIONS, schemas: SchemaContainer, all_models: Dict[str, Type[Model]]):
        model_name = cls.__name__
        if operation_name == "create":
            schema = getattr(getattr(schemas, "create"), model_name.lower())

            def func(db: Database, create_info: schema):
                model = all_models[model_name]
                dbmodel = getattr(db, model_name)
                if hasattr(model, "create_preparation"):
                    create_info = model.create_preparation(**create_info)
                new_instance = dbmodel(**create_info)
                return new_instance

                model = getattr(db, model_name)
            func.__name__ = f"operation_{operation_name}_{model_name.lower()}"
            setattr(func, "is_an_operation", True)
            return func
        elif operation_name == "get":
            schema = getattr(getattr(schemas, "get"), model_name.lower())

            def func(db: Database, get_info: schema):
                model = getattr(db, model_name)
                if hasattr(model, "get_preparation"):
                    get_info = model.get_preparation(**get_info)
                instance = model.get(**get_info)
                return instance

            func.__name__ = f"operation_{operation_name}_{model_name.lower()}"
            setattr(func, "is_an_operation", True)
            return func
        elif operation_name == "select":
            schema = getattr(getattr(schemas, "select"), model_name.lower())

            def func(db: Database, select_info: schema):
                model = getattr(db, model_name)
                if hasattr(model, "select_preparation"):
                    select_info = model.select_preparation(**select_info)

                query = model.select()
                for key, value in select_info.items():
                    query = query.filter(lambda i: getattr(i, key) == value)

                return query

            func.__name__ = f"operation_{operation_name}_{model_name.lower()}"
            setattr(func, "is_an_operation", True)
            return func
        elif operation_name == "update":
            get_schema = getattr(getattr(schemas, "get"), model_name.lower())
            update_schema = getattr(getattr(schemas, "update"), model_name.lower())

            def func(db: Database, get_info: get_schema, update_info: update_schema):
                model = getattr(db, model_name)
                if hasattr(model, "get_preparation"):
                    get_info = model.get_preparation(**get_info)
                instance = model.get(**get_info)
                if hasattr(model, "update_preparation"):
                    update_info = model.update_preparation(**update_info)
                instance.set(**update_info)
                return instance

            func.__name__ = f"operation_{operation_name}_{model_name.lower()}"
            setattr(func, "is_an_operation", True)
            return func
        elif operation_name == "delete":
            schema = getattr(getattr(schemas, "get"), model_name.lower())

            def func(db: Database, get_info: schema):
                model = getattr(db, model_name)
                if hasattr(model, "get_preparation"):
                    get_info = model.get_preparation(**get_info)
                model.get(**get_info).delete()
                return None

            func.__name__ = f"operation_{operation_name}_{model_name.lower()}"
            setattr(func, "is_an_operation", True)
            return func
        else:
            return lambda: True


def kwargs_from_prep(prep: Callable):
    kwargs = {}
    sign = signature(prep).parameters
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
    return kwargs


def kwargs_from_cls(cls: Type[Model], all_models: Dict[str, Type[Model]]):
    kwargs = {}
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
    return kwargs


class ModelContainer:
    def __init__(self, _name):
        self._name = _name

    def __iter__(self):
        for attr in dir(self):
            if hasattr(getattr(self, attr), "is_an_operation"):
                yield getattr(self, attr)
            if hasattr(getattr(self, attr), "is_a_pydantic_model"):
                yield getattr(self, attr)



class SchemaContainer:
    def __init__(self):
        for schema in SCHEMAS:
            setattr(self, schema, ModelContainer(schema))

    def __iter__(self):
        for schema in SCHEMAS:
            yield getattr(self, schema)



class OperationContainer:
    def __init__(self):
        for operation in OPERATIONS:
            setattr(self, operation, ModelContainer(operation))

    def __iter__(self):
        for operation in OPERATIONS:
            yield getattr(self, operation)
