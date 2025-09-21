"""
Random schedule generator utility for creating mock calendar data.
Generates realistic schedules with varying availability between date ranges.
"""

import random
import datetime
from typing import List, Dict
from shared.models import Appointment, ScheduleConfig, APPOINTMENTS_BY_DATE


class RandomScheduleGenerator:
    """Generates random schedules for testing and demonstration purposes."""
    
    def __init__(self, config: ScheduleConfig = None):
        self.config = config or ScheduleConfig()
        self.consultant_names = [
            "Sarah Miller", "David Kim", "Emily Chen", "Michael Brown",
            "Priya Patel", "Carlos Ramirez", "Samantha Lee", "James Wilson",
            "Lisa Zhang", "Robert Taylor", "Maria Garcia", "Kevin O'Connor"
        ]
        self.client_names = [
            "John Doe", "Jane Smith", "Tom Evans", "Emily Johnson",
            "Michael Lee", "Sarah Davis", "Chris Wilson", "Amanda Thompson",
            "Daniel Rodriguez", "Jennifer Kim", "Mark Anderson", "Rachel Green",
            "Alex Parker", "Nicole Brown", "Steven Clark", "Laura Martinez"
        ]
        self.meeting_types = [
            "Initial Consultation",
            "Strategy Planning Session",
            "Digital Transformation Review",
            "Organizational Assessment",
            "Follow-up Meeting",
            "Project Kickoff",
            "Progress Review",
            "Implementation Planning",
            "Stakeholder Alignment",
            "Executive Briefing"
        ]
        self.meeting_descriptions = [
            "Discussion of business objectives and strategic priorities",
            "Review of current processes and identification of improvement opportunities",
            "Planning session for digital transformation initiatives",
            "Assessment of organizational structure and development needs",
            "Follow-up on previous recommendations and action items",
            "Kickoff meeting for new consulting engagement",
            "Progress review and milestone assessment",
            "Detailed planning for implementation phases",
            "Alignment meeting with key stakeholders",
            "Executive briefing on project outcomes and next steps"
        ]

    def _get_schedule_density(self) -> str:
        """Determine the schedule density for a day based on probabilities."""
        rand = random.random()
        if rand < self.config.light_schedule_prob:
            return "light"
        elif rand < self.config.light_schedule_prob + self.config.medium_schedule_prob:
            return "medium"
        else:
            return "heavy"

    def _get_meetings_count(self, density: str) -> int:
        """Get number of meetings based on schedule density."""
        if density == "light":
            return random.randint(1, 2)
        elif density == "medium":
            return random.randint(2, 3)
        else:  # heavy
            return random.randint(3, 4)

    def _generate_meeting_time_slots(self, date: datetime.date, num_meetings: int) -> List[tuple]:
        """Generate non-overlapping time slots for meetings on a given date."""
        slots = []
        business_minutes = (self.config.business_end_hour - self.config.business_start_hour) * 60
        
        # Create potential start times (every 30 minutes)
        potential_starts = []
        for hour in range(self.config.business_start_hour, self.config.business_end_hour):
            for minute in [0, 30]:
                potential_starts.append(hour * 60 + minute)
        
        # Generate meetings
        for _ in range(num_meetings):
            max_attempts = 50
            attempts = 0
            
            while attempts < max_attempts:
                # Pick random duration and start time
                duration = random.choice(self.config.meeting_durations)
                start_minutes = random.choice(potential_starts)
                end_minutes = start_minutes + duration
                
                # Check if it fits in business hours
                if end_minutes > (self.config.business_end_hour * 60):
                    attempts += 1
                    continue
                
                # Check for conflicts with existing slots
                start_time = datetime.datetime.combine(
                    date, 
                    datetime.time(start_minutes // 60, start_minutes % 60)
                )
                end_time = datetime.datetime.combine(
                    date, 
                    datetime.time(end_minutes // 60, end_minutes % 60)
                )
                
                # Check for overlap
                has_conflict = False
                for existing_start, existing_end in slots:
                    if (start_time < existing_end and end_time > existing_start):
                        has_conflict = True
                        break
                
                if not has_conflict:
                    slots.append((start_time, end_time))
                    break
                
                attempts += 1
        
        return sorted(slots)

    def _generate_appointment(self, start_time: datetime.datetime, end_time: datetime.datetime) -> Appointment:
        """Generate a random appointment for the given time slot."""
        meeting_type = random.choice(self.meeting_types)
        client_name = random.choice(self.client_names)
        consultant_name = random.choice(self.consultant_names)
        
        # Sometimes add additional attendees
        attendees = [consultant_name, client_name]
        if random.random() < 0.3:  # 30% chance of additional attendees
            additional_attendee = random.choice(self.consultant_names)
            if additional_attendee not in attendees:
                attendees.append(additional_attendee)
        
        title = f"{meeting_type}: {client_name}"
        description = random.choice(self.meeting_descriptions)
        
        return Appointment(
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            attendees=attendees
        )

    def generate_schedule(self, start_date: datetime.date, end_date: datetime.date, 
                         clear_existing: bool = False) -> Dict[datetime.date, List[Appointment]]:
        """
        Generate a random schedule between start_date and end_date.
        
        Args:
            start_date: First date to generate schedule for
            end_date: Last date to generate schedule for (inclusive)
            clear_existing: Whether to clear existing appointments in the date range
            
        Returns:
            Dictionary mapping dates to lists of appointments
        """
        if clear_existing:
            # Clear existing appointments in the date range
            current_date = start_date
            while current_date <= end_date:
                if current_date in APPOINTMENTS_BY_DATE:
                    del APPOINTMENTS_BY_DATE[current_date]
                current_date += datetime.timedelta(days=1)
        
        generated_schedule = {}
        current_date = start_date
        
        while current_date <= end_date:
            # Skip weekends (assuming business days only)
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                # Decide if this day should have meetings
                if random.random() < self.config.daily_meeting_probability:
                    density = self._get_schedule_density()
                    num_meetings = self._get_meetings_count(density)
                    
                    # Generate time slots
                    time_slots = self._generate_meeting_time_slots(current_date, num_meetings)
                    
                    # Create appointments
                    appointments = []
                    for start_time, end_time in time_slots:
                        appointment = self._generate_appointment(start_time, end_time)
                        appointments.append(appointment)
                    
                    if appointments:
                        generated_schedule[current_date] = appointments
                        # Also update the global calendar
                        if current_date not in APPOINTMENTS_BY_DATE:
                            APPOINTMENTS_BY_DATE[current_date] = []
                        APPOINTMENTS_BY_DATE[current_date].extend(appointments)
            
            current_date += datetime.timedelta(days=1)
        
        return generated_schedule

    def print_schedule_summary(self, schedule: Dict[datetime.date, List[Appointment]]):
        """Print a summary of the generated schedule."""
        print("\n" + "="*60)
        print("GENERATED SCHEDULE SUMMARY")
        print("="*60)
        
        total_days = len(schedule)
        total_meetings = sum(len(appointments) for appointments in schedule.values())
        
        print(f"Total days with meetings: {total_days}")
        print(f"Total meetings generated: {total_meetings}")
        print(f"Average meetings per day: {total_meetings/total_days:.1f}")
        print()
        
        for date in sorted(schedule.keys()):
            appointments = schedule[date]
            print(f"{date.strftime('%A, %B %d, %Y')} - {len(appointments)} meeting(s)")
            for apt in appointments:
                print(f"  {apt.start_time.strftime('%H:%M')}-{apt.end_time.strftime('%H:%M')}: {apt.title}")
        print("="*60)


def generate_random_schedule(start_date_str: str, end_date_str: str, 
                           config: ScheduleConfig = None, clear_existing: bool = False) -> Dict[datetime.date, List[Appointment]]:
    """
    Convenience function to generate a random schedule.
    
    Args:
        start_date_str: Start date in 'YYYY-MM-DD' format
        end_date_str: End date in 'YYYY-MM-DD' format
        config: Optional configuration for schedule generation
        clear_existing: Whether to clear existing appointments in the date range
        
    Returns:
        Dictionary mapping dates to lists of appointments
    """
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
    
    generator = RandomScheduleGenerator(config)
    schedule = generator.generate_schedule(start_date, end_date, clear_existing)
    generator.print_schedule_summary(schedule)
    
    return schedule


def create_very_busy_schedule_config() -> ScheduleConfig:
    """Create a configuration for a very busy schedule."""
    return ScheduleConfig(
        daily_meeting_probability=1.0,
        light_schedule_prob=0.0,
        medium_schedule_prob=0.3,
        heavy_schedule_prob=0.7
    )

# Example usage and presets
def create_busy_schedule_config() -> ScheduleConfig:
    """Create a configuration for a busy schedule."""
    return ScheduleConfig(
        daily_meeting_probability=0.9,
        light_schedule_prob=0.1,
        medium_schedule_prob=0.3,
        heavy_schedule_prob=0.6
    )


def create_light_schedule_config() -> ScheduleConfig:
    """Create a configuration for a light schedule."""
    return ScheduleConfig(
        daily_meeting_probability=0.4,
        light_schedule_prob=0.7,
        medium_schedule_prob=0.3,
        heavy_schedule_prob=0.0
    )


if __name__ == "__main__":
    # Example usage
    print("Generating sample schedules...")
    
    # Generate a normal schedule for the next two weeks
    start_date = datetime.date.today() + datetime.timedelta(days=1)
    end_date = start_date + datetime.timedelta(days=14)
    
    normal_schedule = generate_random_schedule(
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
        clear_existing=True
    )
