from enum import Enum
from typing import Union

from pydantic import BaseModel


class FileType(str, Enum):
    configs = "configs"
    groups = "groups"
    scenarios = "scenarios"
    moments = "moments"


class RootType(str, Enum):
    protocols = "protocols"
    info = "info"


class DeviceType(str, Enum):
    data = "data"
    meta = "meta"
    cmeta = "cmeta"
    cdata = "cdata"
    devices = "devices"


class Data(BaseModel):
    name: str
    value: Union[str, int, float]
