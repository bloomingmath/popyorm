# popyorm
A Pony-Pydantic Orm

Define your model bases in a separate module like:
```python
# bases.py
from popy import Required, Optional, Set, Json


class ModelA:
    arg_a = Required(str)


class ModelB:
    arg_a = Required(str)
    arg_b = Required(int)

    def create_preparation(self, arg_a: str):
        return {"arg_a": arg_a, "arg_b": len(arg_a)}
```

Then generate actual models and database with:
```python
from popy import ModelContainer, db_session
from . import bases

ModelA, ModelB = mc = ModelContainer(bases, provider="sqlite", filename=":memory:", create_db=True)

with db_session:
    x = ModelB.operations.create(create_info={"arg_a": "example"})
with db_session:
    y = ModelB.operations.fetch({"arg_b": 7})
    assert y.arg_a == "example"
```