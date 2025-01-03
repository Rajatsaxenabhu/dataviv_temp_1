from pydantic import BaseModel

class Input_Schema(BaseModel):
    name: str
    content_type: str

