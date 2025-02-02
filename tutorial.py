import cv2
import base64
from inference_sdk import InferenceHTTPClient

import instruction
from parse import parse_file

data = parse_file("input.txt")

class RoboflowWebcam:
    def __init__(self, api_url, api_key, model_id, inference_interval=1):
        self.client = InferenceHTTPClient(api_url=api_url, api_key=api_key)
        self.model_id = model_id
        self.cap = cv2.VideoCapture(0)
        self.frame_counter = 0
        self.inference_interval = inference_interval
        self.bboard_positions = {}
        self.dot_padding_y = 5  # Added padding for dots in the y direction
        self.negative_offset = 10  # Offset for negative power lines
        self.frame = None  # Store the current frame

        if not self.cap.isOpened():
            raise RuntimeError("Error: Could not open webcam.")

    def store_bboard_positions(self, x1, y1, x2, y2, height):
        power_line_height = height // 6
        self.bboard_positions = {
            "top_power_line": (x1, y1, x2, y1 + power_line_height),
            "pins": (x1, y1 + power_line_height, x2, y2 - power_line_height),
            "bottom_power_line": (x1, y2 - power_line_height, x2, y2)
        }

    def draw_bounding_boxes(self):
        if self.frame is None:
            return
        for key, (x1, y1, x2, y2) in self.bboard_positions.items():
            color = (255, 0, 0) if "power_line" in key else (0, 0, 255)
            cv2.rectangle(self.frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(self.frame, key.replace("_", " ").title(), (x1 + 10, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        color, 2)

    def draw_power_line_dot(self, line_type="top_power_line", rail_type="+", position=1):
        if self.frame is None or line_type not in self.bboard_positions:
            return
        x1, y1, x2, y2 = self.bboard_positions[line_type]
        line_width = x2 - x1
        dot_spacing = line_width // 30

        dot_x = x1 + (position - 1) * dot_spacing + dot_spacing // 2 + 23

        dot_y = (y1 + y2) // 2 + (
            0 if rail_type == "+" else self.negative_offset)  # Offset negative rail

        cv2.circle(self.frame, (dot_x, dot_y), radius=5, color=(0, 255, 0), thickness=-1)
        cv2.putText(self.frame, f"{line_type} {rail_type}{position}", (dot_x + 5, dot_y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0), 2)

    def draw_single_dot(self, row_label="a", col_label=1):
        if self.frame is None or "pins" not in self.bboard_positions:
            return
        x1, y1, x2, y2 = self.bboard_positions["pins"]
        pins_width = x2 - x1
        pins_height = y2 - y1
        col_spacing = pins_width // 10
        row_spacing = pins_height // 30

        row_index = ord(row_label.lower()) - ord("a")
        col_index = col_label - 1

        dot_x = x1 + row_index * col_spacing + col_spacing // 2
        dot_y = y1 + col_index * row_spacing + row_spacing // 2 + 20  # Apply y padding

        cv2.circle(self.frame, (dot_x, dot_y), radius=5, color=(0, 255, 0), thickness=-1)
        cv2.putText(self.frame, f"{row_label.upper()}{col_label}", (dot_x + 5, dot_y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2)

    def process_frame(self):
        ret, self.frame = self.cap.read()
        if not ret:
            print("Error: Could not read frame.")
            return None

        self.frame = cv2.resize(self.frame, (640, 480))
        self.frame_counter += 1

        if self.frame_counter % self.inference_interval != 0:
            return self.frame

        _, buffer = cv2.imencode(".jpg", self.frame)
        base64_image = base64.b64encode(buffer).decode("utf-8")
        result = self.client.infer(base64_image, model_id=self.model_id)

        for prediction in result.get("predictions", []):
            x, y, width, height, label, confidence = (
                int(prediction["x"]), int(prediction["y"]),
                int(prediction["width"]), int(prediction["height"]),
                prediction["class"], prediction["confidence"]
            )

            #


            if label == "Bboard":
                x1, y1, x2, y2 = x - width // 2, y - height // 2, x + width // 2, y + height // 2
                self.store_bboard_positions(x1, y1, x2, y2, height)
                # self.draw_bounding_boxes()
                # self.draw_single_dot("A", 1)
                # self.draw_power_line_dot("top_power_line", "+", 1)
                # self.draw_power_line_dot("top_power_line", "-", 1)

        return self.frame

    def run(self, funcs):
        frame = self.process_frame()
        if frame is not None:
            while funcs:
                func, *args = funcs.pop(0)  # Unpack function and arguments
                if args and args[0] is None:  # Handle cases where there's no argument
                    func()  # Call function without arguments
                else:
                    func(*args)  # Call function with arguments

            cv2.imshow('Webcam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return False
            return True

    def stop(self):
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    webcam = RoboflowWebcam(
        api_url="https://detect.roboflow.com",
        api_key="V4t2YZYhTAbOuZcGDmha",
        model_id="lastsurvivor/2",
        inference_interval=1
    )
    print(data.get("Instructions"))
    instruction = instruction.InstructionsRun(webcam, data.get("Instructions"))
    instruction.run_camera_with_input()
