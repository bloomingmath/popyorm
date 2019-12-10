"""These models are for test purpose. When using popy import the Model class, define your models that inherit from
it, and pass them as a list, a dictionary or a module to the functions you are interested in, like generate_popy. """

from .popyorm import *


class AA(Model):
    aa = Required(str)
