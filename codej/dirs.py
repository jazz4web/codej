import os

from starlette.config import Config

base = os.path.dirname(__file__)
static = os.path.join(base, 'static')
templates = os.path.join(base, 'templates')
settings = Config(os.path.join(os.path.dirname(base), '.env'))
