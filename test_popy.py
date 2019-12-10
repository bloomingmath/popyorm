from .popyorm import *
from . import fake_models


def test_module_import():
    assert "Model" in globals()


def test_extract_models():
    d = extract_popy_models(fake_models)
    assert isinstance(d, dict)
    assert any(issubclass(m, Model) and m is not Model for key, m in d.items())
    assert "AA" in d.keys()


def test_generate_database():
    db = generate_database(fake_models, provider="sqlite", filename=":memory:", create_db=True)
    assert isinstance(db, Database)
    assert hasattr(db, "AA")
    db.AA = getattr(db, "AA")
    assert issubclass(db.AA, Model)
    assert issubclass(db.AA, fake_models.AA)
    assert isinstance(getattr(db.AA, "aa"), Required)
    assert isinstance(getattr(db.AA, "id"), PrimaryKey)
