import os

from dotenv import dotenv_values
from easydict import EasyDict as edict

config = edict({
    **os.environ,
    **dotenv_values(".env"),
})
