from .popyorm import *
from . import fake_models


def test_module_import():
    assert "Model" in globals()


def test_extract_models():
    d = extract_popy_models(fake_models)
    assert isinstance(d, dict)
    assert any(issubclass(m, Model) and m is not Model for key, m in d.items())
    assert "Ma" in d.keys()


def test_generate_database():
    db = generate_database(fake_models, provider="sqlite", filename=":memory:", create_db=True)
    assert isinstance(db, Database)
    assert hasattr(db, "Ma")
    db.Ma = getattr(db, "Ma")
    assert issubclass(db.Ma, Model)
    assert issubclass(db.Ma, fake_models.Ma)
    assert isinstance(getattr(db.Ma, "aa"), Required)
    assert isinstance(getattr(db.Ma, "id"), PrimaryKey)


def test_generate_schemas():
    schemas = generate_schemas(fake_models)
    assert issubclass(schemas.create.ma, BaseModel)
    assert "aa" in schemas.create.ma.__fields__
    assert schemas.create.ma.__fields__["aa"].type_ == str
