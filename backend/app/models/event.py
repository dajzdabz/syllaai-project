# app/models/event.py - FIX THE ENUM VALUES
import enum
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SQLAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base

class EventCategory(enum.Enum):
    exam = "exam"
    hw = "hw" 
    project = "project"
    class_session = "class"  # Changed from 'class' to avoid Python keyword conflict
    other = "other"

class EventSource(enum.Enum):
    parser = "parser"
    manual = "manual"

class SyllabusStatus(enum.Enum):
    pending = "pending"
    processing = "processing" 
    done = "done"
    error = "error"

class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    dt_start = Column(DateTime(timezone=True), nullable=False)
    dt_end = Column(DateTime(timezone=True), nullable=True)
    category = Column(SQLAEnum(EventCategory), default=EventCategory.other)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    source = Column(SQLAEnum(EventSource), default=EventSource.manual)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    course = relationship("Course", back_populates="events")

class Syllabus(Base):
    __tablename__ = "syllabi"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_url = Column(String, nullable=True)
    file_size = Column(String, nullable=True)
    parsed_text = Column(Text, nullable=True)
    status = Column(SQLAEnum(SyllabusStatus), default=SyllabusStatus.pending)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    course = relationship("Course", back_populates="syllabi")