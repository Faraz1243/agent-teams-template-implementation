from typing import Literal

from pydantic import BaseModel

class SumInput(BaseModel):
    a: float
    b: float

