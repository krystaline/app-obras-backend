from pydantic import BaseModel


class Manager(BaseModel):
    id: str
    name: str
    email: str