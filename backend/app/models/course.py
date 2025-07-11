from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from sqlalchemy.orm import relationship
from ..database import Base

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # EXISTING fields (kept exactly the same)
    code = Column(String(8), unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # NEW MVP fields (nullable for backward compatibility)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)
    crn = Column(String(10), nullable=True)  # Course Reference Number
    semester = Column(String(6), nullable=True)  # e.g., "2024FA", "2025SP"
    
    # Calendar integration
    professor_calendar_token = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # EXISTING relationships (kept exactly the same)
    events = relationship("Event", back_populates="course")  # Keep for backward compatibility
    syllabi = relationship("Syllabus", back_populates="course")  # Keep existing
    
    # NEW MVP relationships
    school = relationship("School", back_populates="courses")
    course_events = relationship("CourseEvent", back_populates="course", cascade="all, delete-orphan")
    student_links = relationship("StudentCourseLink", back_populates="course")
    professor = relationship("User", foreign_keys=[created_by])

# EXISTING Enrollment model (kept exactly the same)
class Enrollment(Base):
    __tablename__ = "enrollments"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), primary_key=True)