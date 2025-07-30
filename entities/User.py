from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(alias='display_name')
    email: str = Field(alias='mail')
    id: str
    selected: bool
    type: str | None
