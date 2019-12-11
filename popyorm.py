from .model import Model, SCHEMAS, OPERATIONS, SchemaContainer, OperationContainer
from pony.orm import Required, Optional, Set, Json, db_session, Database, PrimaryKey
from pydantic import BaseModel
from typing import Dict, Type, Tuple
from types import ModuleType


def generate_database(module: ModuleType, **kwargs) -> Database:
    """Given a module, it extract its adequate class and build a ponyorm's Database with them. Arguments for the 
    database creation (i.e. provider, filename and create_db) are to be passed as keywords. """
    models_dict = extract_popy_models(module)
    db = Database(**kwargs)
    for key, model in models_dict.items():
        # This is ponyorm's _magic_ that I don't understand: by defining a type that inherits from db.Entity, that type
        # goes into db with its primary key and the database gets its tables and so on and so forth... and it works!
        type(key, (db.Entity,), model.get_fields())
    db.generate_mapping(create_tables=True)
    return db


def generate_schemas(module: ModuleType) -> SchemaContainer:
    """Schemas are pydantic models. They are used to validate data received in requests and to shape the response."""
    models_dict = extract_popy_models(module)
    schemas = SchemaContainer()
    for schema_name in SCHEMAS:
        for model_name, model in models_dict.items():
            setattr(getattr(schemas, schema_name), model_name.lower(), model.pydantic_model(schema_name, models_dict))
    return schemas


def generate_operations(module: ModuleType) -> OperationContainer:
    """Basics model-specific CreateReadGetUpdateDelete operations to act upon the database."""
    models_dict = extract_popy_models(module)
    schemas = generate_schemas(module)
    operations = OperationContainer()
    for operation in OPERATIONS:
        setattr(operations, operation, OperationContainer())
        for model_name, model in models_dict.items():
            setattr(getattr(operations, operation), model_name.lower(), model.generate_operation(operation, schemas))
    return operations


def generate_popy(module: ModuleType, **kwargs) -> Tuple[Database, SchemaContainer, OperationContainer]:
    return generate_database(module, **kwargs), generate_schemas(module), generate_operations(module)


def extract_popy_models(module: ModuleType) -> Dict[str, Type[Model]]:
    """Returns all class derived from Model (not Model itself) in the given module, in a dictionary."""
    return {attr: getattr(module, attr)
            for attr in dir(module)
            if hasattr(getattr(module, attr), "is_popy_model") and getattr(module, attr) is not Model}
