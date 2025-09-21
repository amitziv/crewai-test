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
