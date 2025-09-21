import datetime
from crewai.tools import tool
from ..shared.models import Appointment, APPOINTMENTS_BY_DATE
from ..utils.schedule_generator import create_very_busy_schedule_config, generate_random_schedule, create_busy_schedule_config


def generate_calendar_data():
    """
    Generate realistic calendar data using the random schedule generator.
    Creates a busy schedule for the next 30 days for testing and demonstration.
    """
    global APPOINTMENTS_BY_DATE
    
    # Clear existing data
    APPOINTMENTS_BY_DATE.clear()
    
    # Generate busy schedule for next 30 days
    today = datetime.date.today()
    start_date = today
    end_date = today + datetime.timedelta(days=30)
    
    print(f"Generating busy calendar schedule from {start_date} to {end_date}...")
    
    # Use busy configuration for more interesting testing scenarios
    busy_config = create_very_busy_schedule_config()
    schedule = generate_random_schedule(
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
        config=busy_config,
        clear_existing=True
    )
    
    print(f"Calendar data generated successfully! Created appointments for {len(schedule)} days.")
    return schedule

# Generate calendar data when module is imported
generate_calendar_data()

@tool
def get_tomorrow_appointments():
    """Get appointments for tomorrow's date."""
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    return APPOINTMENTS_BY_DATE.get(tomorrow, [])

@tool   
def get_all_appointments():
    """Get all appointments across all dates."""
    return list(APPOINTMENTS_BY_DATE.values())

@tool
def get_open_meeting_slots(date: str, duration_minutes: int = 60):
    """
    Get available meeting slots for a specific date.
    
    Args:
        date: Date in YYYY-MM-DD format
        duration_minutes: Duration of the meeting in minutes (default 60)
    
    Returns:
        List of available time slots as dictionaries with start_time and end_time
    """
    try:
        target_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Invalid date format. Please use YYYY-MM-DD format."}
    
    # Business hours: 9 AM to 5 PM
    business_start = 9
    business_end = 17
    
    # Get existing appointments for the date
    existing_appointments = APPOINTMENTS_BY_DATE.get(target_date, [])
    
    # Generate all possible time slots
    available_slots = []
    current_time = datetime.datetime.combine(target_date, datetime.time(business_start, 0))
    end_of_day = datetime.datetime.combine(target_date, datetime.time(business_end, 0))
    
    while current_time + datetime.timedelta(minutes=duration_minutes) <= end_of_day:
        slot_end = current_time + datetime.timedelta(minutes=duration_minutes)
        
        # Check if this slot conflicts with any existing appointment
        is_available = True
        for appointment in existing_appointments:
            if (current_time < appointment.end_time and slot_end > appointment.start_time):
                is_available = False
                break
        
        if is_available:
            available_slots.append({
                "start_time": current_time.strftime("%Y-%m-%d %H:%M"),
                "end_time": slot_end.strftime("%Y-%m-%d %H:%M")
            })
        
        # Move to next 30-minute slot
        current_time += datetime.timedelta(minutes=30)
    
    return available_slots

@tool
def set_meeting(title: str, start_time: str, end_time: str, description: str, attendees: list[str]):
    """
    Schedule a new meeting appointment.
    
    Args:
        title: Meeting title
        start_time: Start time in YYYY-MM-DD HH:MM format
        end_time: End time in YYYY-MM-DD HH:MM format
        description: Meeting description
        attendees: List of attendee names
    
    Returns:
        Success message or error if scheduling fails
    """
    try:
        start_dt = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        end_dt = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M")
    except ValueError:
        return {"error": "Invalid datetime format. Please use YYYY-MM-DD HH:MM format."}
    
    if start_dt >= end_dt:
        return {"error": "End time must be after start time."}
    
    # Check business hours (9 AM to 5 PM)
    if start_dt.hour < 9 or end_dt.hour > 17:
        return {"error": "Meetings can only be scheduled between 9 AM and 5 PM."}
    
    meeting_date = start_dt.date()
    
    # Check for conflicts with existing appointments
    existing_appointments = APPOINTMENTS_BY_DATE.get(meeting_date, [])
    for appointment in existing_appointments:
        if (start_dt < appointment.end_time and end_dt > appointment.start_time):
            return {
                "error": f"Time slot conflicts with existing appointment: {appointment.title} ({appointment.start_time.strftime('%H:%M')} - {appointment.end_time.strftime('%H:%M')})"
            }
    
    # Create new appointment
    new_appointment = Appointment(
        title=title,
        start_time=start_dt,
        end_time=end_dt,
        description=description,
        attendees=attendees
    )
    
    # Add to calendar
    if meeting_date not in APPOINTMENTS_BY_DATE:
        APPOINTMENTS_BY_DATE[meeting_date] = []
    
    APPOINTMENTS_BY_DATE[meeting_date].append(new_appointment)
    
    return {
        "success": True,
        "message": f"Meeting '{title}' scheduled successfully for {start_time} - {end_time}",
        "appointment": {
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "description": description,
            "attendees": attendees
        }
    }
    