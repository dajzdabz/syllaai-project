# app/services/openai_service.py - COMMENTED OUT VERSION (to avoid import errors)
"""
OpenAI service for syllabus parsing - TEMPORARILY DISABLED
"""

# import openai
# import os
# from typing import List, Dict, Any
# from ..schemas.event import ParsedSyllabus

def parse_syllabus_text(text: str) -> dict:
    """
    Parse syllabus text using OpenAI - PLACEHOLDER
    TODO: Implement actual OpenAI integration
    """
    return {
        "events": [],
        "status": "not_implemented",
        "message": "OpenAI integration coming soon"
    }

# TODO: Uncomment and implement when schemas are ready
"""
async def parse_syllabus_with_openai(syllabus_text: str) -> ParsedSyllabus:
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        prompt = f'''
        Parse this syllabus and extract all events (exams, assignments, projects, etc.) with dates.
        
        Syllabus text:
        {syllabus_text}
        
        Return a JSON object with an array of events, each containing:
        - title: string
        - date: ISO datetime string
        - category: one of "exam", "hw", "project", "class", "other"
        - description: string (optional)
        '''
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        # Parse the response and return structured data
        return ParsedSyllabus.parse_raw(response.choices[0].message.content)
        
    except Exception as e:
        raise Exception(f"Failed to parse syllabus: {str(e)}")
"""