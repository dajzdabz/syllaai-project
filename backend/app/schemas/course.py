from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# KEEP your existing schemas, ADD new ones
class CourseBase(BaseModel):
    title: str

class CourseCreate(CourseBase):
    # Keep backward compatibility
    pass

# NEW MVP schemas
class CourseCreateMVP(BaseModel):
    school_id: int
    crn: str
    title: str
    semester: str

class CourseSearchMVP(BaseModel):
    school_id: int
    crn: str
    semester: str

class EnrollmentCreate(BaseModel):
    course_code: str

# Enhanced course response
class Course(CourseBase):
    id: uuid.UUID
    code: str
    created_by: uuid.UUID
    
    # NEW MVP fields (optional for backward compatibility)
    school_id: Optional[int] = None
    crn: Optional[str] = None
    semester: Optional[str] = None
    
    created_at: Optional[datetime] = None
    school: Optional[Dict[str, Any]] = None
    student_count: Optional[int] = None
    
    class Config:
        from_attributes = True