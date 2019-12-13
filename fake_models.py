"""These models are for test purpose. When using popy import the Model class, define your models that inherit from
it, and pass them as a list, a dictionary or a module to the functions you are interested in, like generate_popy. """

from .popyorm import *


class Ma(Model):
    arg_a = Required(str)


class ModelB(Model):
    arg_b = Optional(int)
    arg_c = Required(Json)
    arg_d = Required("ModelC")

    @classmethod
    def create_preparation(self, arg_c_json: str, arg_d_id: int, arg_b: str = None):
        import json
        create_info = {}
        if arg_b is not None:
            create_info["arg_b"] = arg_b
        create_info["arg_c"] = json.loads(arg_c_json)
        create_info["arg_d"] = arg_d_id
        return create_info

    @classmethod
    def get_preparation(cls, id: int):
        return {"id": id}

    @classmethod
    def select_preparation(cls, arg_b: int = None, arg_d_id: int = None):
        select_info = {}
        if arg_b is not None:
            select_info["arg_b"] = arg_b
        if arg_d_id is not None:
            select_info["arg_d"] = arg_d_id
        return select_info

    @classmethod
    def update_preparation(cls, arg_b: int = None, arg_c_json: str = None):
        import json
        update_info = {}
        if arg_b is not None:
            update_info["arg_b"] = arg_b
        if arg_c_json is not None:
            update_info["arg_c"] = json.loads(arg_c_json)

    @classmethod
    def show_preparation(cls, arg_b, arg_c, arg_d):
        return None


class ModelC(Model):
    arg_e = Required(str, default="e default")
    arg_f = Set("ModelB")
    arg_g = Set("ModelC", reverse="arg_h")
    arg_h = Set("ModelC", reverse="arg_g")
    
    @classmethod
    def create_preparation(cls, arg_e: str = None):
        if arg_e is not None:
            return {"arg_e": arg_e}
        else:
            return {}
        
    @classmethod
    def get_preparation(cls, id: int = None, arg_e: str = None):
        get_info = {}
        if id is not  None:
            get_info["id"] = id
        if arg_e is not None:
            get_info["arg_e"] = arg_e
        return get_info
    
    @classmethod
    def select_preparation(cls, arg_f_set_id_json : str = None):
        import json
        select_info = {}
        if arg_f_set_id_json is not None:
            select_info["arg_f"] = json.loads(arg_f_set_id_json)
        return select_info
    
    @classmethod
    def update_preparation(cls, arg_e: str = None, arg_f_set_id_json : str = None, arg_g_set_id_json : str = None):
        import json
        update_info = {}
        if arg_e is not None:
            update_info["arg_e"] = arg_e
        if arg_f_set_id_json is not None:
            update_info["arg_f"] = json.loads(arg_f_set_id_json)
        if arg_g_set_id_json is not None:
            update_info["arg_f"] = json.loads(arg_g_set_id_json)

    @classmethod
    def show_preparation(cls, arg_e, arg_f, arg_g, arg_h):
        return None

class ModelD(Model):
    arg_a = Required(str)
    arg_b = Required(int)

    @classmethod
    def create_preparation(cls, arg_a: str):
        return {"arg_a": arg_a, "arg_b": len(arg_a)}

    @classmethod
    def get_preparation(cls, arg_a: str):
        return {"arg_a": arg_a}

    @classmethod
    def select_preparation(cls, arg_b: int = None):
        return {"arg_b": arg_b}

    @classmethod
    def update_preparation(cls, arg_a: str = None):
        if arg_a is not None:
            return {"arg_a": arg_a, "arg_b": len(arg_a)}
        else:
            return {}

    @classmethod
    def show_preparation(cls, arg_a, arg_b):
        return None