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
    instructions = [{"BreadBoardConnection":'PowerLine+'}, {"BreadBoardConnection":'PowerLine-'}, {'BreadBoardConnection': {'connect': ['PowerLine+', 'a1']}}]
    trigger = False

    def __init__(self, roboflow_model, instructions):
        """
        Initializes the InstructionParse class with a Roboflow model instance.

        Args:
            roboflow_model (RoboflowWebcam): Instance of the RoboflowWebcam class.
        """
        self.funcs = []
        self.model: RoboflowWebcam = roboflow_model  # Store the model instance
        self.instructions = instructions

    def describe_instruction(self, instruction: dict):
        if "BreadBoardConnection" in instruction:
            BreadBoardConnection = instruction.get("BreadBoardConnection")
            if BreadBoardConnection == "PowerLine+":
                self.funcs.append((self.model.draw_power_line_dot,"top_power_line", "+", 1))
                pass
            elif BreadBoardConnection == "PowerLine-":
                self.funcs.append((self.model.draw_power_line_dot,"top_power_line", "-", 1))
                pass
            elif isinstance(BreadBoardConnection, dict) and "connect" in BreadBoardConnection:
                ptA = BreadBoardConnection.get("connect")[0]
                if ptA  == "PowerLine+":
                    self.funcs.append((self.model.draw_power_line_dot, "top_power_line", "+", 4))
                elif ptA  == "PowerLine-":
                    self.funcs.append((self.model.draw_power_line_dot, "top_power_line", "-", 4))
                else:
                    letter, number = split_alpha_numeric(ptA)
                    self.funcs.append((self.model.draw_single_dot, letter, int(number)))
                ptB = BreadBoardConnection.get("connect")[1]

                if ptB == "PowerLine+":
                    self.funcs.append((self.model.draw_power_line_dot, "top_power_line", "+", 4))
                elif ptB == "PowerLine-":
                    self.funcs.append((self.model.draw_power_line_dot, "top_power_line", "-", 4))
                else:
                    letter, number = split_alpha_numeric(ptB)
                    self.funcs.append((self.model.draw_single_dot, letter, int(number)))
                pass
        elif "ResistorConnection" in instruction:
            ResistorConnection = instruction.get("ResistorConnection")
            if isinstance(ResistorConnection, dict) and "connect" in ResistorConnection:
                ptA = ResistorConnection.get("connect")[0]
                if ptA == "PowerLine+":
                    self.funcs.append((self.model.draw_power_line_dot, "top_power_line", "+", 4))
                elif ptA == "PowerLine-":
                    self.funcs.append((self.model.draw_power_line_dot, "top_power_line", "-", 4))
                else:
                    letter, number = split_alpha_numeric(ptA)
                    self.funcs.append((self.model.draw_single_dot, letter, int(number)))
                ptB = ResistorConnection.get("connect")[1]

                if ptB == "PowerLine+":
                    self.funcs.append((self.model.draw_power_line_dot, "top_power_line", "+", 4))
                elif ptB == "PowerLine-":
                    self.funcs.append((self.model.draw_power_line_dot, "top_power_line", "-", 4))
                else:
                    letter, number = split_alpha_numeric(ptB)
                    self.funcs.append((self.model.draw_single_dot, letter, int(number)))

    def next_task(self):
        self.trigger = False
        self.index += 1
        # self.describe_instruction(self.instructions[self.index])

    def prev_task(self):
        self.trigger = False
        self.index -= 1

    def current_task(self):
        self.describe_instruction(self.instructions[self.index])

    import threading

    def input_listener(self):
        """Thread function to handle user input separately."""
        while True:
            user_input = input("Next task: ")
            print(f"User entered: {user_input}")  # Process user input here
            if user_input == 'n':
                self.trigger = True
            elif user_input == 'b':
                self.prev_task()

    def run_camera_with_input(self):
        """Runs the camera in a loop while handling input in a separate thread."""

        # Start the input listener thread
        input_thread = threading.Thread(target=self.input_listener, daemon=True)
        input_thread.start()

        while True:
            if self.trigger:
                self.next_task()
            else:
                self.current_task()

            # Run self.model.run() in a loop

            if not self.model.run(self.funcs):
                break
        self.model.stop()

