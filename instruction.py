import threading
import re

def split_alpha_numeric(s):
    match = re.match(r"([a-zA-Z]+)(\d+)", s)
    if match:
        return match.group(1), int(match.group(2))  # Letter and number
    return None, None  # Handle invalid input

speak_lines = [
"Grab your power supply",
"Connect your positive wire of your power supply to the positive power line",
"Connect your negative wire of your power supply to the negative power line",
"Grab your resistor",
"Connect your resistor to power line to a-20",
"Grab your LED",
"Connect your LED to b-23 to b-20",
"Connect a wire to negative power line to a-23",
"At this point you should see your LED light up!"
]

class InstructionsRun:
    index = 0
    instructions = [{"BreadBoardConnection":'PowerLine+'}, {"BreadBoardConnection":'PowerLine-'}, {'BreadBoardConnection': {'connect': ['PowerLine+', 'a1']}}]
    trigger = False
    engine = None

    def __init__(self, roboflow_model, instructions):
        """
        Initializes the InstructionParse class with a Roboflow model instance.

        Args:
            roboflow_model (RoboflowWebcam): Instance of the RoboflowWebcam class.
        """
        self.spoke = None
        self.isStart = False
        self.funcs = []
        self.model = roboflow_model  # Store the model instance
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
        self.spoke = False
        self.index += 1
        # self.describe_instruction(self.instructions[self.index])

    def prev_task(self):
        self.trigger = False
        self.index -= 1

    def current_task(self):
        self.funcs = []
        self.describe_instruction(self.instructions[self.index])
        if not self.spoke:
            print(speak_lines[self.index] + "\nIs task done? (n: Next): ")
            self.spoke = True
            self.engine.say(speak_lines[self.index])
            self.engine.runAndWait()
            return

    import threading

    def input_listener(self):
        """Thread function to handle user input separately."""
        while True:
            if not self.isStart:
                continue

            if not self.spoke:
                continue
            user_input = input("")

            if user_input == 'n':
                self.trigger = True
            elif user_input == 'b':
                self.prev_task()

    def run_camera_with_input(self, engine):
        """Runs the camera in a loop while handling input in a separate thread."""
        self.engine = engine
        # Start the input listener thread
        input_thread = threading.Thread(target=self.input_listener, daemon=True)
        input_thread.start()

        while True:
            if not self.model.run(self.funcs):
                break
            self.isStart = True

            if self.trigger:
                if self.index + 1 < len(self.instructions) - 1:
                    self.next_task()
                else:
                    break
            else:
                self.current_task()
        print("Great! You have finished your circuits.")
        self.engine.say("Great! You have finished your circuit.")
        self.engine.runAndWait()
        print("There are no instructions available, Virtuino is shutting down.")
        self.engine.say("There are no instructions available, Virtuino is shutting down.")
        self.engine.runAndWait()
        self.model.stop()
        exit(0)


