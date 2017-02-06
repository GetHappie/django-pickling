from django.db import DJANGO_VERSION_PICKLE_KEY
from django.db.models import Model
from django.utils.version import get_version
try:
    from itertools import izip
except ImportError:
    izip = zip

VERSION = (0, 2)
__version__ = '.'.join(map(str, VERSION))


def model_is_deferred(model):
    try:
        return bool(model.get_deferred_fields())
    except AttributeError:
        return model._deferred


def attnames(cls, _cache={}):
    try:
        return _cache[cls]
    except KeyError:
        _cache[cls] = [f.attname for f in cls._meta.fields]
        return _cache[cls]


def model_unpickle(cls, data):
    obj = cls.__new__(cls)
    obj.__dict__.update(izip(attnames(cls), data))
    return obj


model_unpickle.__safe_for_unpickle__ = True


def model__reduce__(self):
    if model_is_deferred(self):
        return original_model__reduce__(self)
    else:
        cls = self.__class__
        data = self.__dict__.copy()
        data[DJANGO_VERSION_PICKLE_KEY] = get_version()

        vector = map(data.pop, attnames(cls))
        return model_unpickle, (cls, vector), data


if Model.__reduce__ != model__reduce__:
    original_model__reduce__ = Model.__reduce__
    Model.__reduce__ = model__reduce__
