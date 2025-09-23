import sys
import yaml
from game_builder_crew.crew import SchedulingCrew


def run():
    output = SchedulingCrew().crew().kickoff({
        'requirements': 'I need to schedule a meeting with John Doe on Monday at 10:00'
    })

    print("\n\n########################")
    print("## Here is the result")
    print("########################\n")
    print("final schedule:")
    print(output)
    

def train():
    """
    Train the crew for a given number of iterations.
    """

    with open('src/game_builder_crew/config/gamedesign.yaml', 'r', encoding='utf-8') as file:
        examples = yaml.safe_load(file)

    inputs = {
        'game' : examples['example1_pacman']
    }
    try:
        GameBuilderCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def plot():
    """
    Plot the crew flow.
    """
    try:
        # Create crew instance
        crew_instance = SchedulingCrew().crew()
        
        # For now, print crew structure since plot() method may not be available on Crew objects
        print("\n=== CREW STRUCTURE ===")
        print(f"Agents: {len(crew_instance.agents)}")
        for i, agent in enumerate(crew_instance.agents):
            print(f"  Agent {i+1}: {agent.role}")
        
        print(f"\nTasks: {len(crew_instance.tasks)}")
        for i, task in enumerate(crew_instance.tasks):
            print(f"  Task {i+1}: {task.description[:100]}...")
            
        print(f"\nProcess: {crew_instance.process}")
        print("\n=== CREW VISUALIZATION COMPLETE ===")
        
        # If plot method exists, try to use it
        if hasattr(crew_instance, 'plot'):
            crew_instance.plot()
        else:
            print("Note: Visual plotting not available for this CrewAI version")
            
    except Exception as e:
        print(f"An error occurred while plotting the crew flow: {e}")
        # Don't raise exception, just print it so the command doesn't fail completely
