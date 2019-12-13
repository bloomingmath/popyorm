from .popyorm import *
from importlib import import_module

fake_models = import_module(".fake_models", "popy")
db, schemas, operations = generate_popy(fake_models, provider="sqlite", filename=":memory:", create_db=True)


def test_module_import():
    assert "Model" in globals()


def test_extract_models():
    models_dict = extract_popy_models(fake_models)
    assert isinstance(models_dict, dict)
    assert any(issubclass(m, Model) and m is not Model for key, m in models_dict.items())
    assert "Ma" in models_dict.keys()
    assert hasattr(models_dict["ModelB"], "create_preparation")


def test_generate_database():
    assert isinstance(db, Database)
    assert hasattr(db, "Ma")
    db.Ma = getattr(db, "Ma")
    assert issubclass(db.Ma, db.Entity)
    assert isinstance(getattr(db.Ma, "arg_a"), Required)
    assert isinstance(getattr(db.Ma, "id"), PrimaryKey)


def test_generate_schemas():
    assert issubclass(schemas.create.ma, BaseModel)
    assert "arg_a" in schemas.show.ma.__fields__
    assert schemas.update.ma.__fields__["arg_a"].type_ == str


def test_generate_operations():
    assert callable(operations.create.ma)
    with db_session:
        new_ima = operations.create.ma(db=db, create_info={"arg_a": "x"})
        assert isinstance(new_ima, db.Ma)
        ima = operations.get.ma(db=db, get_info={"arg_a": "x"})
        assert ima.arg_a == "x"

        operations.create.ma(db=db, create_info={"arg_a": "y"})
        query = operations.select.ma(db=db, select_info={})
        assert query.count() == 2

        query = operations.select.ma(db=db, select_info={"arg_a": "x"})
        assert query.count() == 1

        query = operations.select.ma(db=db, select_info={"arg_a": "z"})
        assert query.count() == 0

        ima = operations.update.ma(db=db, get_info={"id": 1}, update_info={"arg_a": "z"})
        assert ima.arg_a == "z"
        assert operations.get.ma(db=db, get_info={"arg_a": "z"}).id == 1

        operations.delete.ma(db=db, get_info={"arg_a": "y"})
        assert operations.select.ma(db=db, select_info={}).count() == 1

def test_model_d():
    with db_session:
        imd = operations.create.modeld(db, {"arg_a":"abcdef"})
        assert isinstance(imd, db.ModelD)
        assert imd.arg_b == 6