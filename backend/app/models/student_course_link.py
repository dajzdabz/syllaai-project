from sqlalchemy import Column, ForeignKey, JSON, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class StudentCourseLink(Base):
    __tablename__ = "student_course_links"
    
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), primary_key=True)
    
    # Store mapping of course events to student's calendar events
    gcal_event_map = Column(JSON, default=dict)  # {course_event_id: student_gcal_id}
    
    # Student's calendar access token (encrypted)
    student_calendar_token = Column(Text, nullable=True)
    
    # Timestamps
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("User", foreign_keys=[student_id])
    course = relationship("Course", back_populates="student_links")