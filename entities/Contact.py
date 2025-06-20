from pydantic import BaseModel


class Contact(BaseModel):
    id: str
    title: str
    phone: int
    signature: str

