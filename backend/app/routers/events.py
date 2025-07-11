# app/routers/events.py - ADD PUT/DELETE endpoints
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..models.event import Event as EventModel
from ..models.course import Course as CourseModel
from ..schemas.event import EventCreate, Event as EventSchema, EventUpdate

router = APIRouter(prefix="/api/events", tags=["events"])

@router.get("/course/{course_id}", response_model=List[EventSchema])
async def get_course_events(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all events for a specific course"""
    events = db.query(EventModel).filter(EventModel.course_id == course_id).all()
    return events

@router.post("/", response_model=EventSchema)
async def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new event (Professor only)"""
    if current_user.role.value != "professor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professors can create events"
        )
    
    # Verify the course exists and user owns it
    course = db.query(CourseModel).filter(CourseModel.id == event_in.course_id).first()
    if not course or course.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create events for your own courses"
        )
    
    event = EventModel(**event_in.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.put("/{event_id}", response_model=EventSchema)
async def update_event(
    event_id: UUID,
    event_update: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing event (Professor only)"""
    if current_user.role.value != "professor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professors can update events"
        )
    
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check if professor owns the course
    course = db.query(CourseModel).filter(CourseModel.id == event.course_id).first()
    if not course or course.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update events for your own courses"
        )
    
    # Update only provided fields
    for field, value in event_update.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    return event

@router.delete("/{event_id}")
async def delete_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an event (Professor only)"""
    if current_user.role.value != "professor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professors can delete events"
        )
    
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check if professor owns the course
    course = db.query(CourseModel).filter(CourseModel.id == event.course_id).first()
    if not course or course.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete events for your own courses"
        )
    
    db.delete(event)
    db.commit()
    return {"detail": "Event deleted successfully"}

@router.post("/course/{course_id}/syllabus")
async def upload_syllabus(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload and parse syllabus (Professor only)"""
    if current_user.role.value != "professor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professors can upload syllabi"
        )
    
    course = db.query(CourseModel).filter(CourseModel.id == course_id).first()
    if not course or course.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload syllabi for your own courses"
        )
    
    return {
        "detail": "Syllabus upload endpoint - implementation needed",
        "course_id": str(course_id)
    }

# app/routers/courses.py - ADD PUT/DELETE endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import random
import string

from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..models.course import Course as CourseModel, Enrollment
from ..schemas.course import CourseCreate, Course as CourseSchema, EnrollmentCreate, CourseUpdate

router = APIRouter(prefix="/api/courses", tags=["courses"])

def generate_course_code() -> str:
    """Generate a unique 8-character course code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@router.get("/", response_model=List[CourseSchema])
async def get_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get courses based on user role"""
    if current_user.role.value == "professor":
        courses = db.query(CourseModel).filter(CourseModel.created_by == current_user.id).all()
    elif current_user.role.value == "student":
        courses = db.query(CourseModel).join(
            Enrollment, CourseModel.id == Enrollment.course_id
        ).filter(Enrollment.user_id == current_user.id).all()
    else:  # admin
        courses = db.query(CourseModel).all()
    
    return courses

@router.post("/", response_model=CourseSchema)
async def create_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new course (Professor only)"""
    if current_user.role.value != "professor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professors can create courses"
        )
    
    course_code = generate_course_code()
    while db.query(CourseModel).filter(CourseModel.code == course_code).first():
        course_code = generate_course_code()
    
    course = CourseModel(
        **course_in.model_dump(),
        code=course_code,
        created_by=current_user.id
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

@router.put("/{course_id}", response_model=CourseSchema)
async def update_course(
    course_id: UUID,
    course_update: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing course (Professor only)"""
    if current_user.role.value != "professor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professors can update courses"
        )
    
    course = db.query(CourseModel).filter(CourseModel.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    if course.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own courses"
        )
    
    # Update only provided fields
    for field, value in course_update.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    return course

@router.delete("/{course_id}")
async def delete_course(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a course (Professor only)"""
    if current_user.role.value != "professor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professors can delete courses"
        )
    
    course = db.query(CourseModel).filter(CourseModel.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    if course.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own courses"
        )
    
    db.delete(course)
    db.commit()
    return {"detail": "Course deleted successfully"}

@router.post("/join", response_model=CourseSchema)
async def join_course(
    enrollment_in: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join a course by course code (Student only)"""
    if current_user.role.value != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can join courses"
        )
    
    course = db.query(CourseModel).filter(CourseModel.code == enrollment_in.course_code).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course.id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )
    
    enrollment = Enrollment(user_id=current_user.id, course_id=course.id)
    db.add(enrollment)
    db.commit()
    
    return course