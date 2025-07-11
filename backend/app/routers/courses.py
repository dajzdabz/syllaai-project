from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import random
import string

from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..models.course import Course as CourseModel, Enrollment
from ..models.school import School
from ..models.course_event import CourseEvent
from ..models.student_course_link import StudentCourseLink
from ..schemas.course import CourseCreate, Course as CourseSchema, EnrollmentCreate
from ..schemas.school import School as SchoolSchema, SchoolCreate
from ..schemas.course_event import CourseEvent as CourseEventSchema, CourseEventCreate, SyllabusUploadResponse

router = APIRouter(prefix="/courses", tags=["courses"])

def generate_course_code() -> str:
    """Generate a unique 8-character course code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# ============================================================================
# EXISTING ENDPOINTS (kept exactly the same)
# ============================================================================

@router.get("/", response_model=List[CourseSchema])
async def get_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get courses based on user role"""
    if current_user.role.value == "professor":
        # Professors see courses they created
        courses = db.query(CourseModel).filter(CourseModel.created_by == current_user.id).all()
    elif current_user.role.value == "student":
        # Students see enrolled courses
        courses = db.query(CourseModel).join(
            Enrollment, CourseModel.id == Enrollment.course_id
        ).filter(Enrollment.user_id == current_user.id).all()
    else:  # admin
        # Admins see all courses
        courses = db.query(CourseModel).all()
    
    # Add additional info for each course
    for course in courses:
        # Add student count
        course.student_count = db.query(Enrollment).filter(Enrollment.course_id == course.id).count()
        
        # Add school info if available
        if course.school:
            course.school = {"id": course.school.id, "name": course.school.name}
    
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
    
    # Generate unique course code
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
    
    # Find course by code
    course = db.query(CourseModel).filter(CourseModel.code == enrollment_in.course_code).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if already enrolled
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course.id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )
    
    # Create enrollment
    enrollment = Enrollment(user_id=current_user.id, course_id=course.id)
    db.add(enrollment)
    db.commit()
    
    return course

# ============================================================================
# NEW MVP ENDPOINTS
# ============================================================================

# School Management
@router.get("/schools", response_model=List[SchoolSchema])
async def get_schools(db: Session = Depends(get_db)):
    """Get list of all schools"""
    schools = db.query(School).order_by(School.name).all()
    return schools

@router.post("/schools", response_model=SchoolSchema)
async def create_school(
    school: SchoolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new school (professors only)"""
    if current_user.role.value != "professor":
        raise HTTPException(status_code=403, detail="Only professors can create schools")
    
    # Check if school already exists
    existing = db.query(School).filter(School.name == school.name).first()
    if existing:
        return existing
    
    db_school = School(**school.dict())
    db.add(db_school)
    db.commit()
    db.refresh(db_school)
    return db_school

# Enhanced Course Creation
class CourseCreateMVP(CourseCreate):
    school_id: int
    crn: str
    semester: str

@router.post("/mvp", response_model=CourseSchema)
async def create_course_mvp(
    course: CourseCreateMVP,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a course with MVP fields (school, CRN, semester)"""
    if current_user.role.value != "professor":
        raise HTTPException(status_code=403, detail="Only professors can create courses")
    
    # Check for duplicate CRN in same school/semester
    existing = db.query(CourseModel).filter(
        CourseModel.school_id == course.school_id,
        CourseModel.crn == course.crn,
        CourseModel.semester == course.semester
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Course with this CRN already exists for this semester")
    
    # Generate unique course code
    course_code = generate_course_code()
    while db.query(CourseModel).filter(CourseModel.code == course_code).first():
        course_code = generate_course_code()
    
    db_course = CourseModel(
        title=course.title,
        code=course_code,
        created_by=current_user.id,
        school_id=course.school_id,
        crn=course.crn,
        semester=course.semester
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

# Course Search
@router.get("/search")
async def search_course(
    school_id: int,
    crn: str,
    semester: str,
    db: Session = Depends(get_db)
):
    """Search for a course by school, CRN, and semester"""
    course = db.query(CourseModel).filter(
        CourseModel.school_id == school_id,
        CourseModel.crn == crn,
        CourseModel.semester == semester
    ).first()
    
    if course:
        # Add student count
        course.student_count = db.query(StudentCourseLink).filter(
            StudentCourseLink.course_id == course.id
        ).count()
        
        # Add school info
        if course.school:
            course.school = {"id": course.school.id, "name": course.school.name}
    
    return course

# Enhanced Course Joining
class CourseSearchMVP(CourseCreate):
    school_id: int
    crn: str
    semester: str

@router.post("/join-mvp")
async def join_course_mvp(
    course_search: CourseSearchMVP,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join a course using MVP search (school + CRN + semester)"""
    if current_user.role.value != "student":
        raise HTTPException(status_code=403, detail="Only students can join courses")
    
    course = db.query(CourseModel).filter(
        CourseModel.school_id == course_search.school_id,
        CourseModel.crn == course_search.crn,
        CourseModel.semester == course_search.semester
    ).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if already enrolled (check both systems)
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course.id
    ).first()
    
    existing_link = db.query(StudentCourseLink).filter(
        StudentCourseLink.student_id == current_user.id,
        StudentCourseLink.course_id == course.id
    ).first()
    
    if existing_enrollment or existing_link:
        raise HTTPException(status_code=400, detail="Already enrolled in this course")
    
    # Create both for backward compatibility
    enrollment = Enrollment(user_id=current_user.id, course_id=course.id)
    link = StudentCourseLink(
        student_id=current_user.id,
        course_id=course.id,
        student_calendar_token=current_user.google_refresh_token
    )
    
    db.add(enrollment)
    db.add(link)
    db.commit()
    
    return {"message": f"Successfully enrolled in {course.title}"}

# Syllabus Upload (Demo Implementation)
@router.post("/{course_id}/syllabus", response_model=SyllabusUploadResponse)
async def upload_syllabus(
    course_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload and process syllabus for a course"""
    course = db.query(CourseModel).filter(
        CourseModel.id == course_id,
        CourseModel.created_by == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found or access denied")
    
    # TODO: Implement actual AI processing
    # For now, return demo events
    from datetime import datetime, timedelta
    today = datetime.now()
    
    demo_events = [
        CourseEventCreate(
            title="Midterm Exam",
            start_ts=today + timedelta(days=30),
            end_ts=today + timedelta(days=30, hours=2),
            category="Exam",
            location="Room 101"
        ),
        CourseEventCreate(
            title="Assignment 1 Due",
            start_ts=today + timedelta(days=14),
            end_ts=today + timedelta(days=14),
            category="HW",
            location=None
        ),
        CourseEventCreate(
            title="Group Project Presentation",
            start_ts=today + timedelta(days=45),
            end_ts=today + timedelta(days=45, hours=1),
            category="Project",
            location="Conference Room A"
        )
    ]
    
    return SyllabusUploadResponse(
        extracted_events=demo_events,
        course_id=course_id
    )

# Event Publishing
@router.post("/{course_id}/events/publish")
async def publish_events(
    course_id: UUID,
    events: List[CourseEventCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Publish events for a course (creates database records)"""
    course = db.query(CourseModel).filter(
        CourseModel.id == course_id,
        CourseModel.created_by == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found or access denied")
    
    # Clear existing events for this course
    db.query(CourseEvent).filter(CourseEvent.course_id == course_id).delete()
    
    # Create new events
    created_events = []
    for event_data in events:
        db_event = CourseEvent(
            course_id=course_id,
            **event_data.dict()
        )
        db.add(db_event)
        created_events.append(db_event)
    
    db.commit()
    
    # TODO: Create calendar events for professor and students
    
    return {
        "message": f"Successfully published {len(created_events)} events",
        "events_created": len(created_events)
    }

# Student Syllabus Processing
@router.post("/student-syllabus", response_model=SyllabusUploadResponse)
async def process_student_syllabus(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process student-uploaded syllabus and extract events"""
    import PyPDF2
    import io
    import re
    import os
    from datetime import datetime, timedelta
    
    try:
        # Read and validate file
        contents = await file.read()
        print(f"DEBUG: Successfully extracted {len(contents)} chars with PyPDF2")
        
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Extract text from PDF
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
            for page in pdf_reader.pages:
                text += page.extract_text()
        except Exception as e:
            print(f"DEBUG: PDF extraction error: {e}")
            raise HTTPException(status_code=400, detail="Failed to extract text from PDF")
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF")
        
        # Clean and process text
        text = text.strip()
        print(f"DEBUG: Raw text sample: '{text[:50]}'")
        print(f"DEBUG: Processing text length: {len(text)}")
        
        # Extract basic info (semester, dates, etc.)
        semester_match = re.search(r'(20\d{2})(SP|SU|FA|WI)', text)
        semester = semester_match.group(0) if semester_match else "2025SP"
        print(f"DEBUG: Detected semester: {semester}")
        
        # Look for dates in the text
        date_pattern = r'\b(\d{1,2})/(\d{1,2})\b'
        dates = re.findall(date_pattern, text)
        print(f"DEBUG: Found potential dates in text: {dates[:20]}")  # Show first 20 dates
        
        if not dates:
            print("DEBUG: No dates found in regex, returning empty events")
            return SyllabusUploadResponse(
                extracted_events=[],
                course_id=None
            )
        
        print("DEBUG: Regex found dates, proceeding with OpenAI parsing")
        
        # Process with OpenAI (fixed null reference)
        extracted_events = await parse_syllabus_with_openai(text)
        
        return SyllabusUploadResponse(
            extracted_events=extracted_events,
            course_id=None
        )
        
    except Exception as e:
        print(f"DEBUG: OpenAI parsing error: {e}")
        print(f"DEBUG: Error type: {type(e)}")
        raise HTTPException(
            status_code=422, 
            detail=f"Failed to parse syllabus: {str(e)}"
        )

async def parse_syllabus_with_openai(text: str) -> List[CourseEventCreate]:
    """Parse syllabus text using OpenAI API"""
    import openai
    import json
    from datetime import datetime, timedelta
    
    try:
        # Count tokens (approximate)
        token_count = len(text.split())
        print(f"DEBUG: Total text tokens: {token_count}")
        
        # Get OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise Exception("OpenAI API key not configured")
        
        client = openai.OpenAI(api_key=openai_api_key)
        
        # Create prompt for OpenAI
        prompt = f"""
        Parse this syllabus and extract all events (exams, assignments, projects, etc.) with dates.
        
        Return a JSON array of events, each with:
        - title: string
        - date: ISO date string (YYYY-MM-DD)
        - category: one of "Exam", "Quiz", "HW", "Project", "Presentation", "Class", "Other"
        - location: string or None
        
        Syllabus text:
        {text[:4000]}  # Limit text to avoid token limits
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000
        )
        
        # Parse response
        content = response.choices[0].message.content
        
        # Try to parse JSON from response
        try:
            events_data = json.loads(content)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON from text
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                events_data = json.loads(json_match.group(0))
            else:
                events_data = []
        
        # Convert to CourseEventCreate objects
        events = []
        for event_data in events_data:
            try:
                # Parse date
                date_str = event_data.get("date", "")
                if date_str:
                    event_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                else:
                    event_date = datetime.now() + timedelta(days=30)
                
                # Create event
                event = CourseEventCreate(
                    title=event_data.get("title", "Untitled Event"),
                    start_ts=event_date,
                    end_ts=event_date + timedelta(hours=1),
                    category=event_data.get("category", "Other"),
                    location=event_data.get("location") or None  # Fix: use None instead of null
                )
                events.append(event)
            except Exception as e:
                print(f"DEBUG: Error parsing event: {e}")
                continue
        
        return events
        
    except Exception as e:
        print(f"DEBUG: OpenAI parsing error: {e}")
        raise Exception(f"Failed to parse syllabus: {str(e)}")