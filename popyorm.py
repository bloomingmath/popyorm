from .model import Model, OPERATIONS
from pony.orm import Required, Optional, Set, Json, db_session, Database, PrimaryKey
from pydantic import BaseModel
from typing import Dict, Type
from types import ModuleType


def generate_database(module: ModuleType, **kwargs) -> Database:
    """Given a module, it extract its adequate class and build a ponyorm's Database with them. Arguments for the 
    database creation (i.e. provider, filename and create_db) are to be passed as keywords. """
    models_dict = extract_popy_models(module)
    db = Database(**kwargs)
    for key, model in models_dict.items():
        # This is ponyorm's _magic_ that I don't understand: by defining a type that inherits from db.Entity, that type
        # goes into db with its primary key and the database gets its tables and so on and so forth... and it works!
        type(key, (model, db.Entity,), {})
    db.generate_mapping(create_tables=True)
    return db


def generate_schemas(module: ModuleType):
    models_dict = extract_popy_models(module)
    schemas = SchemaContainer()
    for operation in OPERATIONS:
        setattr(schemas, operation, SchemaContainer())
        for model_name, model in models_dict.items():
            setattr(getattr(schemas, operation), model_name.lower(), model.pydantic_model(operation, models_dict))
    return schemas


def generate_operations():
    pass


def generate_popy():
    pass


class SchemaContainer:
    pass


def extract_popy_models(module: ModuleType) -> Dict[str, Type[Model]]:
    """Returns all class derived from Model (not Model itself) in the given module, in a dictionary."""
    return {attr: getattr(module, attr)
            for attr in dir(module)
            if hasattr(getattr(module, attr), "is_popy_model") and getattr(module, attr) is not Model}
