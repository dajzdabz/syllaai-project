from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from ..database import Base

class CourseEvent(Base):
    __tablename__ = "course_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    
    start_ts = Column(DateTime(timezone=True), nullable=False)
    end_ts = Column(DateTime(timezone=True), nullable=False)
    title = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # "Exam", "HW", "Project", etc.
    location = Column(Text, nullable=True)
    
    # Calendar integration
    professor_gcal_event_id = Column(Text, nullable=True)
    content_hash = Column(Text, nullable=True)  # For change detection
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="course_events")
