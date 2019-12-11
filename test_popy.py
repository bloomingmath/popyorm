from .popyorm import *
from importlib import import_module

fake_models = import_module(".fake_models", "popy")
db = generate_database(fake_models, provider="sqlite", filename=":memory:", create_db=True)


def test_module_import():
    assert "Model" in globals()


def test_extract_models():
    d = extract_popy_models(fake_models)
    assert isinstance(d, dict)
    assert any(issubclass(m, Model) and m is not Model for key, m in d.items())
    assert "Ma" in d.keys()


def test_generate_database():
    assert isinstance(db, Database)
    assert hasattr(db, "Ma")
    db.Ma = getattr(db, "Ma")
    assert issubclass(db.Ma, db.Entity)
    assert isinstance(getattr(db.Ma, "aa"), Required)
    assert isinstance(getattr(db.Ma, "id"), PrimaryKey)


def test_generate_schemas():
    schemas = generate_schemas(fake_models)
    assert issubclass(schemas.create.ma, BaseModel)
    assert "aa" in schemas.show.ma.__fields__
    assert schemas.update.ma.__fields__["aa"].type_ == str


def test_generate_operations():
    operations = generate_operations(module=fake_models)
    assert callable(operations.create.ma)
    with db_session:
        new_ima = operations.create.ma(db=db, create_info={"aa": "x"})
        assert isinstance(new_ima, db.Ma)
        ima = operations.get.ma(db=db, get_info={"aa": "x"})
        assert ima.aa == "x"

        new_ima = operations.create.ma(db=db, create_info={"aa": "y"})
        query = operations.select.ma(db=db, select_info={})
        assert query.count() == 2

        query = operations.select.ma(db=db, select_info={"aa": "x"})
        assert query.count() == 1

        query = operations.select.ma(db=db, select_info={"aa": "z"})
        assert query.count() == 0

        ima = operations.update.ma(db=db, get_info={"id": 1}, update_info={"aa": "z"})
        assert ima.aa == "z"
        assert operations.get.ma(db=db, get_info={"aa": "z"}).id == 1

        operations.delete.ma(db=db, get_info={"aa": "y"})
        assert operations.select.ma(db=db, select_info={}).count() == 1

