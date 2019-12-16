class Container:
    def __init__(self, *args, **kwargs):
        self._dict = {}
        for mapping in args:
            for key, value in mapping.items():
                self[key] = value
        for key, value in kwargs.items():
            self[key] = value
        for key, value in vars(type(self)).items():
            if value is Ellipsis:
                self[key] = 6

    def __contains__(self, item):
        return item in self._dict.values()

    def __getattr__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            try:
                return self._dict[item]
            except KeyError:
                raise AttributeError

    def __getitem__(self, item):
        return self._dict[item]

    def __iter__(self):
        for value in self._dict.values():
            yield value

    def __setitem__(self, key, value):
        try:
            eval(f"self.{key}")
        except AttributeError:
            self._dict[key] = value
        except SyntaxError:
            raise KeyError
        else:
            self._dict[key] = value

    @property
    def __dict__(self):
        return self._dict

    def items(self):
        return self._dict.items()

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()


class FixedContainer(Container):
    def __init__(self, *args):
        self._keys = args
        super().__init__({attr: ... for attr in args})

    def __setitem__(self, key, value):
        if key in self._keys:
            super().__setitem__(key, value)
        else:
            raise AttributeError(f"Given key {key!r} is not in allowed keys {self._keys}")


class SchemaContainer(FixedContainer):
    def __init__(self):
        super().__init__("create", "get", "select", "update")


class OperationContainer(FixedContainer):
    def __init__(self):
        super().__init__("create", "fetch", "select", "update", "delete")


class BaseContainer(Container):
    """A Container with all classes defined in the given module"""

    def __init__(self, module=None):
        super().__init__()
        if module is not None:
            for attr, value in vars(module).items():
                from inspect import isclass
                if isclass(value) and value.__module__ == module.__name__:
                    self[attr] = value

    @staticmethod
    def extract_fields(base):
        from pony.orm import Required, Optional, Set
        return {attr: value for attr, value in vars(base).items() if isinstance(value, (Required, Optional, Set))}

    @staticmethod
    def extract_functions(base):
        from inspect import isfunction
        return {attr: value for attr, value in vars(base).items() if isfunction(value)}


class ModelContainer(Container):
    """A Container with all (pony.orm) models based on the base models defined in the given module, enriched with
    schemas and operations """

    def __init__(self, module, **kwargs):
        from pony.orm import Database, db_session
        super().__init__()
        self.bmc = bmc = BaseContainer(module)
        self.db = db = Database(**kwargs)
        self.db_session = db_session
        for base in bmc:
            fields = {"schemas": SchemaContainer(), "operations": OperationContainer()}
            fields.update(bmc.extract_fields(base))
            fields.update(bmc.extract_functions(base))
            # This is ponyorm's _magic_ that I don't understand: by defining a type that inherits from db.Entity, that
            # type goes into db with its primary key and the database gets its tables and so on... and it works!
            model = type(base.__name__, (db.Entity,), fields)
            self[base.__name__] = model
        for model in self:
            for schema_name in model.schemas.keys():
                model.schemas[schema_name] = self.pydantic_model(model.__name__, schema_name)
            for operation_name in model.operations.keys():
                model.operations[operation_name] = self.generate_operation(model.__name__, operation_name)
        db.generate_mapping(create_tables=True)

    def pydantic_model(self, model_name, schema_name):
        from pydantic import create_model
        model = self[model_name]
        if hasattr(model, f"{schema_name}_preparation"):
            kwargs = self.kwargs_from_prep(getattr(model, f"{schema_name}_preparation"))
        else:
            kwargs = self.kwargs_from_cls(model)
        schema_name = f"{model_name}{schema_name.capitalize()}Schema"
        pydanticmodel = create_model(schema_name, **kwargs)
        setattr(pydanticmodel, "is_a_pydantic_model", True)
        return pydanticmodel

    def generate_operation(self, model_name, operation_name):
        model = self[model_name]

        if operation_name == "create":
            def func(*, create_info: model.schemas.create):
                try:
                    create_info = model.create_preparation(**create_info)
                except AttributeError:
                    pass
                return model(**create_info)
        elif operation_name == "fetch":
            def func(get_info: model.schemas.get):
                try:
                    get_info = model.fetch_preparation(**get_info)
                except AttributeError:
                    pass
                return model.get(**get_info)
        elif operation_name == "select":
            def func(select_info: model.schemas.select):
                try:
                    select_info = model.select_preparation(**select_info)
                except AttributeError:
                    pass
                query = model.select()
                for key, value in select_info.items():
                    query = query.filter(lambda i: getattr(i, key) == value)
                return query
        elif operation_name == "update":
            def func(get_info: model.schemas.get, update_info: model.schemas.update):
                try:
                    get_info = model.get_preparation(**get_info)
                except AttributeError:
                    pass
                try:
                    update_info = model.update_preparation(**update_info)
                except AttributeError:
                    pass
                instance = model.get(get_info)
                instance.set(update_info)
                return instance
        elif operation_name == "delete":
            def func(get_info: model.schemas.get):
                try:
                    get_info = model.get_preparation(**get_info)
                except AttributeError:
                    pass
                return model.get(**get_info).delete()

        func.__name__ = f"operation_{operation_name}_{model_name.lower()}"
        setattr(func, "is_an_operation", True)
        return func

    @staticmethod
    def kwargs_from_prep(prep):
        from inspect import signature, _empty
        from typing import Any
        kwargs = {}
        sign = signature(prep).parameters
        for field, parameter in sign.items():
            if parameter.annotation is _empty:
                attr_type = Any
            else:
                attr_type = parameter.annotation
            if parameter.default is _empty:
                attr_default = Ellipsis
            else:
                attr_default = parameter.default
            kwargs[field] = (attr_type, attr_default)
        return kwargs

    def kwargs_from_cls(self, model):
        from pony.orm import Json
        from typing import Any
        kwargs = {}
        original_fields = model._adict_
        for field, parameter in original_fields.items():
            if isinstance(parameter.py_type, str):
                attr_type = self[parameter.py_type]
            elif isinstance(parameter.py_type, Json):
                attr_type = Any
            else:
                attr_type = parameter.py_type
            if "default" in parameter.kwargs:
                attr_default = parameter.kwargs["default"]
            else:
                attr_default = Ellipsis
            kwargs[field] = (attr_type, attr_default)
        return kwargs


if __name__ == "__main__":
    from importlib import import_module

    models_module = import_module(".fake_models", "popy")
    mc = ModelContainer(models_module, provider="sqlite", filename=":memory:", create_db=True)

    print(mc.ModelB)
    c = Container(art=55, beta=0)

    pass
