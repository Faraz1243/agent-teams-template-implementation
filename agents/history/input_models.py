from pydantic import BaseModel

class HistoryInput(BaseModel):
    country: str

