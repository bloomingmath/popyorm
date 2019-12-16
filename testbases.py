"""These models are for test purpose. When using popy import the Model class, define your models that inherit from
it, and pass them as a module to generate_models. """

from . import Required, Optional, Set, Json


class ModelA:
    arg_a = Required(str)


class ModelB:
    arg_a = Required(str)
    arg_b = Required(int)

    def create_preparation(self, arg_a: str):
        return {"arg_a": arg_a, "arg_b": len(arg_a)}