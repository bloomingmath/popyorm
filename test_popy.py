from pony.orm import db_session, Database
from .popyorm import BaseContainer, ModelContainer, Container, SchemaContainer, OperationContainer
from importlib import import_module
from pytest import raises

bases = import_module(".testbases", "popy")


# mc = ModelContainer(fake_models, provider="sqlite", filename=":memory:", create_db=True)
# ModelA = mc["ModelA"]
# ModelB = mc["ModelB"]

def test_module_import():
    assert bases is not None


def test_container():
    # You can define empty containers, fill with __setitem__ and read values by either __getitem__ or __getattr__
    c = Container()
    c["a"] = 9
    c["b"] = 19
    c["c"] = 29
    assert c.a == 9
    assert c["b"] == 19
    c["b"] = 17
    assert c.b == 17
    assert "a" not in c
    assert 9 in c

    # You can't set items with invalid identifiers
    with raises(KeyError):
        c["3"] = 5

    # Setting attributes does not affect the contents
    c.e = 8
    assert 8 not in c
    with raises(KeyError):
        print(c["e"] == 8)
    assert vars(c) == {"a": 9, "b": 17, "c": 29}

    # Containers have dict-like view functions (items, values, keys) and are iterables (but the iterators gives
    # values, not keys)
    assert [("a", 9), ("b", 17), ("c", 29)] == list(c.items())
    assert sum(v for k, v in c.items()) == 55
    for item in c:
        assert isinstance(item, int)
    assert any(key in ("a", "b", "c") for key in c.keys())

    # Containers can be initialized with a mapping or by keywords
    c = Container({"a": 132, "b": 2453, "c": 36546})
    assert c.c is 36546
    c = Container(a=9, b=19, c=29)
    assert c.c is 29
    with raises(Exception):
        c = Container(9)
    with raises(Exception):
        c = Container("a")
    with raises(Exception):
        c = Container({"4": 45})


def test_schema_and_operation_containers():
    s = SchemaContainer()
    o = OperationContainer()

    # SchemaContainer and OperationContainer are fixed and can't be arbitrarily assigned, except on predetermined keys
    assert list(s.keys()) == ["crt", "get", "qry", "put"]
    assert o.create is Ellipsis
    s["get"] = 45
    assert s.get == 45
    with raises(AttributeError):
        o["disperse"] = lambda: 4


def test_base_container():
    from inspect import isclass
    bmc = BaseContainer(bases)

    # BaseContainer contains every class defined in given module
    assert "ModelA" in vars(bmc).keys()
    assert bases.ModelA in bmc
    assert any(isclass(model) for model in bmc)


def test_get_fields():
    basemodels_dict = BaseModelDict(fake_models)
    BaseModelA = basemodels_dict["ModelA"]
    assert "arg_a" in get_fields(BaseModelA)


def test_generate_models_dict():
    assert "arg_a" in models["ModelA"].schemas.create.schema()["properties"]
    ModelA = models["ModelA"]
    with db_session:
        x = ModelA.operations.create(create_info={"arg_a": "s"})
    assert isinstance(x, ModelA)
