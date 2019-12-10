from .model import Model
from pony.orm import Required, Optional, Set, Json, db_session, Database
from typing import Dict, Type
import types


def generate_database():
    pass


def generate_schemas():
    pass


def generate_operations():
    pass


def generate_popy():
    pass


def extract_popy_models(module: types.ModuleType) -> Dict[str, Type[Model]]:
    """Returns all class derived from Model (not Model itself) in the given module, in a dictionary."""
    return {attr: getattr(module, attr)
            for attr in dir(module)
            if hasattr(getattr(module, attr), "is_popy_model") and getattr(module, attr) is not Model}
