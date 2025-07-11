from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base

class School(Base):
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    
    # Relationships
    courses = relationship("Course", back_populates="school")