import cv2
import base64
from inference_sdk import InferenceHTTPClient
from parse import parse_file

input_file = "input.txt"
data = parse_file(input_file)

class RoboflowWebcam:
    def __init__(self, api_key, model_id, inference_interval=1):
        self.client = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key=api_key
        )
        self.model_id = model_id
        self.inference_interval = inference_interval
        self.cap = cv2.VideoCapture(0)
        self.frame_counter = 0
        self.highlight_list = []
        self.show_predictions = True

        if not self.cap.isOpened():
            raise Exception("Error: Could not open webcam.")

    def toggle_predictions(self):
        self.show_predictions = not self.show_predictions

    def set_highlight_list(self, highlight_list):
        self.highlight_list = highlight_list

    def draw_power_lines_and_pins(self, frame, x1, y1, x2, y2):
        self.draw_power_line_dot(frame, x1, y1, x2, y2, "top", "+", 5)
        self.draw_power_line_dot(frame, x1, y1, x2, y2, "top", "-", 5)
        self.draw_power_line_dot(frame, x1, y1, x2, y2, "bottom", "+", 5)
        self.draw_power_line_dot(frame, x1, y1, x2, y2, "bottom", "-", 5)
        self.draw_single_dot(frame, x1, y1, x2, y2, "A", 1)

    def draw_power_line_dot(self, frame, x1, y1, x2, y2, power_line_type, rail_type, position):
        if "power_line" not in self.highlight_list:
            return
        power_line_width = x2 - x1
        power_line_height = (y2 - y1) // 6
        dot_spacing = power_line_width // 30
        y = y1 + power_line_height // 2 if power_line_type == "top" else y2 - power_line_height // 2
        x = x1 + (position - 1) * (dot_spacing * 1.5) + dot_spacing // 2
        y += 0 if rail_type == "+" else dot_spacing
        cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 0), -1)

    def draw_single_dot(self, frame, x1, y1, x2, y2, col_label, row_label):
        if "pins" not in self.highlight_list:
            return
        pins_width = x2 - x1
        pins_height = y2 - y1
        col_spacing = pins_width // 10
        row_spacing = pins_height // 30
        col_index = 9 - (ord(col_label.lower()) - ord("a"))
        row_index = row_label - 1
        dot_x = x1 + col_index * col_spacing + col_spacing // 2
        dot_y = y1 + row_index * row_spacing + row_spacing // 2
        cv2.circle(frame, (dot_x, dot_y), 5, (0, 255, 0), -1)

    def process_frame(self, frame):
        if not self.show_predictions:
            return

        _, buffer = cv2.imencode(".jpg", frame)
        base64_image = base64.b64encode(buffer).decode("utf-8")
        result = self.client.infer(base64_image, model_id=self.model_id)

        for prediction in result.get("predictions", []):
            x, y, width, height = int(prediction["x"]), int(prediction["y"]), int(prediction["width"]), int(
                prediction["height"])
            label, confidence = prediction["class"], prediction["confidence"]
            cv2.rectangle(frame, (x - width // 2, y - height // 2), (x + width // 2, y + height // 2), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} {confidence:.2f}", (x - width // 2, y - height // 2 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            if label == "Bboard":
                x1, y1, x2, y2 = x - width // 2, y - height // 2, x + width // 2, y + height // 2
                self.draw_power_lines_and_pins(frame, x1, y1, x2, y2)


if __name__ == "__main__":
    roboflow_cam = RoboflowWebcam(api_key="Qg9dfpa6K6c31GIewZ00", model_id="lastsurvivor/2")
    while True:
        ret, frame = roboflow_cam.cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (640, 480))
        roboflow_cam.frame_counter += 1
        if roboflow_cam.frame_counter % roboflow_cam.inference_interval == 0:
            roboflow_cam.process_frame(frame)
        cv2.imshow('Webcam', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('t'):
            roboflow_cam.toggle_predictions()
    roboflow_cam.cap.release()
    cv2.destroyAllWindows()