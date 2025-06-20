from pydantic import BaseModel
import datetime

class ParteObra(BaseModel):
    id: int
    title: str
    description: str
    status: str
    createdAt: datetime.date
