import threading
from tutorial import RoboflowWebcam
import re

def split_alpha_numeric(s):
    match = re.match(r"([a-zA-Z]+)(\d+)", s)
    if match:
        return match.group(1), int(match.group(2))  # Letter and number
    return None, None  # Handle invalid input

class InstructionsRun:
    index = 0
    instructions = [{"BreadBoardConnection":'PowerLine+'}, {"BreadBoardConnection":'PowerLine-'}]
    trigger = False

    def __init__(self, roboflow_model, instructions):
        """
        Initializes the InstructionParse class with a Roboflow model instance.

        Args:
            roboflow_model (RoboflowWebcam): Instance of the RoboflowWebcam class.
        """
        self.model: RoboflowWebcam = roboflow_model  # Store the model instance
        self.instructions = instructions

    def describe_instruction(self, instruction: dict):
        if instruction.get("BreadBoardConnection"):
            BreadBoardConnection = instruction.get("BreadBoardConnection")
            if BreadBoardConnection == "PowerLine+":
                self.model.draw_power_line_dot("top_power_line", "+", 1)
                pass
            elif BreadBoardConnection == "PowerLine-":
                self.model.draw_power_line_dot("top_power_line", "-", 1)
                pass
            elif BreadBoardConnection == "connect":
                ptA = BreadBoardConnection.get("connect")[0]
                if ptA  == "PowerLine+":
                    self.model.draw_power_line_dot("top_power_line", "+", 4)
                elif ptA  == "PowerLine-":
                    self.model.draw_power_line_dot("top_power_line", "-", 4)
                else:
                    letter, number = split_alpha_numeric(ptA)
                    self.model.draw_single_dot()
                ptB = BreadBoardConnection.get("connect")[1]
                pass
        elif instruction.get("ResistorConnection"):
            ResistorConnection = instruction.get("ResistorConnection")
            if ResistorConnection == "connect":
                ptA = ResistorConnection.get("connect")[0]
                ptB = ResistorConnection.get("connect")[1]
                pass

    def next_task(self):
        self.trigger = False
        self.index += 1
        self.describe_instruction(self.instructions[self.index])

    import threading

    def input_listener(self):
        """Thread function to handle user input separately."""
        while True:
            user_input = input("Next task: ")
            print(f"User entered: {user_input}")  # Process user input here
            if user_input == 'y':
                self.trigger = True

    def run_camera_with_input(self):
        """Runs the camera in a loop while handling input in a separate thread."""

        # Start the input listener thread
        input_thread = threading.Thread(target=self.input_listener, daemon=True)
        input_thread.start()

        while True:
            # if self.trigger:
            #     self.next_task()

            # Run self.model.run() in a loop
            self.model.run()

            # self.model.draw_single_dot("A", 1)
            # self.describe_instruction(self.instructions[self.index])

