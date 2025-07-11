# app/schemas/event.py - FIXED VERSION
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.event import EventCategory, EventSource

class EventBase(BaseModel):
    title: str
    dt_start: datetime
    dt_end: Optional[datetime] = None
    category: EventCategory = EventCategory.other
    location: Optional[str] = None
    description: Optional[str] = None

class EventCreate(EventBase):
    course_id: UUID

class EventUpdate(BaseModel):
    title: Optional[str] = None
    dt_start: Optional[datetime] = None
    dt_end: Optional[datetime] = None
    category: Optional[EventCategory] = None
    location: Optional[str] = None
    description: Optional[str] = None

class Event(EventBase):
    id: UUID
    course_id: UUID
    source: EventSource
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Fixed: was orm_mode = True

class SyllabusBase(BaseModel):
    filename: str
    file_size: Optional[str] = None

class SyllabusCreate(SyllabusBase):
    course_id: UUID

class Syllabus(SyllabusBase):
    id: UUID
    course_id: UUID
    file_url: Optional[str] = None
    parsed_text: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Fixed: was orm_mode = True

# app/schemas/course.py - FIXED VERSION
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class Course(CourseBase):
    id: UUID
    code: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Fixed: was orm_mode = True

class EnrollmentCreate(BaseModel):
    course_code: str

# app/schemas/user.py - FIXED VERSION  
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    email: str
    name: str
    role: UserRole

class UserCreate(UserBase):
    auth_provider: str
    external_id: str

class User(UserBase):
    id: UUID
    auth_provider: str
    external_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Fixed: was orm_mode = True

class GoogleAuthRequest(BaseModel):
    token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str