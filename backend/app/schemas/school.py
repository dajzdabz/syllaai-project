from pydantic import BaseModel
from typing import List, Optional

class SchoolBase(BaseModel):
    name: str

class SchoolCreate(SchoolBase):
    pass

class School(SchoolBase):
    id: int
    
    class Config:
        from_attributes = True