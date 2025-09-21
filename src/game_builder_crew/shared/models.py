"""
Shared data models used across the application.
This module contains common data structures to avoid circular imports.
"""

from dataclasses import dataclass
import datetime
from typing import List, Dict


@dataclass
class Appointment:
    """Represents a calendar appointment."""
    title: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    description: str
    attendees: List[str]


@dataclass
class ScheduleConfig:
    """Configuration for schedule generation."""
    # Probability of having meetings on any given day (0.0 to 1.0)
    daily_meeting_probability: float = 0.7
    
    # Range of meetings per day when there are meetings
    min_meetings_per_day: int = 1
    max_meetings_per_day: int = 4
    
    # Business hours
    business_start_hour: int = 9
    business_end_hour: int = 17
    
    # Meeting duration options (in minutes)
    meeting_durations: List[int] = None
    
    # Probability of different schedule densities
    # These should add up to 1.0
    light_schedule_prob: float = 0.3  # 1-2 meetings
    medium_schedule_prob: float = 0.5  # 2-3 meetings
    heavy_schedule_prob: float = 0.2   # 3-4 meetings
    
    def __post_init__(self):
        if self.meeting_durations is None:
            self.meeting_durations = [30, 60, 90, 120]


# Global appointments storage
APPOINTMENTS_BY_DATE: Dict[datetime.date, List[Appointment]] = {}
