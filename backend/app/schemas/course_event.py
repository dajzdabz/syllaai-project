from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class CourseEventBase(BaseModel):
    start_ts: datetime
    end_ts: datetime
    title: str
    category: str
    location: Optional[str] = None

class CourseEventCreate(CourseEventBase):
    pass

class CourseEvent(CourseEventBase):
    id: uuid.UUID
    course_id: uuid.UUID
    professor_gcal_event_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class SyllabusUploadResponse(BaseModel):
    extracted_events: List[CourseEventCreate]
    course_id: uuid.UUID
