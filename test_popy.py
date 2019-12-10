from .popyorm import *
from . import fake_models


def test_module_import():
    assert "Model" in globals()


def test_extract_models():
    d = extract_popy_models(fake_models)
    assert isinstance(d, dict)
    assert any(issubclass(m, Model) and m is not Model for key, m in d.items())
    assert "AA" in d.keys()
