# config.py
from pydantic import BaseModel

class BaseModelWithConfig(BaseModel):
    class Config:
        arbitrary_types_allowed = True
