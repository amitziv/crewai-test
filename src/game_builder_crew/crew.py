from game_builder_crew.services import Calendar, Messaging
from typing import List
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import tool


@CrewBase
class SchedulingCrew:
    """Scheduling crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def scheduling_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['scheduling_agent'],
            allow_delegation=False,
            verbose=True,
            tools=[Calendar.get_tomorrow_appointments, Calendar.get_all_appointments,
            Calendar.get_open_meeting_slots, Calendar.set_meeting, Messaging.send_message]
        )


    @task
    def schedule_task(self) -> Task:
        return Task(
            config=self.tasks_config['schedule_task'],
            agent=self.scheduling_agent()
        )


    @crew
    def crew(self) -> Crew:
        """Creates the SchedulingCrew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True, 
        )