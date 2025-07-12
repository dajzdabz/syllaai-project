# app/services/openai_service.py - Production OpenAI Integration
"""
OpenAI service for syllabus parsing using GPT-4o-mini
"""

import openai
import os
import json
import re
from typing import List, Dict, Any
from datetime import datetime, timedelta

def parse_syllabus_text(text: str) -> dict:
    """
    Parse syllabus text using OpenAI GPT-4o-mini
    """
    try:
        # Get OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            return {
                "events": [],
                "status": "error",
                "message": "OpenAI API key not configured"
            }
        
        client = openai.OpenAI(api_key=openai_api_key)
        
        # Enhanced prompt for better extraction
        prompt = f"""
        You are an expert at parsing academic syllabi. Extract all important events with dates from this syllabus.
        
        Return ONLY a valid JSON array of events. Each event should have:
        - "title": descriptive name of the event
        - "date": ISO date string (YYYY-MM-DD) - if year is missing, assume 2025
        - "category": one of "Exam", "Quiz", "HW", "Project", "Presentation", "Class", "Other"
        - "location": room/building or null if not specified
        
        Focus on:
        - Exams (midterms, finals, quizzes)
        - Assignment due dates
        - Project deadlines
        - Presentation dates
        - Important class dates
        
        Syllabus text:
        {text[:6000]}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        
        # Parse JSON response
        try:
            events_data = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from text if direct parsing fails
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                events_data = json.loads(json_match.group(0))
            else:
                events_data = []
        
        return {
            "events": events_data,
            "status": "success",
            "message": f"Extracted {len(events_data)} events"
        }
        
    except Exception as e:
        return {
            "events": [],
            "status": "error",
            "message": f"Failed to parse syllabus: {str(e)}"
        }

async def parse_syllabus_with_openai(syllabus_text: str) -> List[Dict[str, Any]]:
    """
    Async version for use in FastAPI endpoints
    """
    result = parse_syllabus_text(syllabus_text)
    if result["status"] == "success":
        return result["events"]
    else:
        raise Exception(result["message"])