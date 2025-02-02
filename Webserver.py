from flask import Flask, Response, render_template
import cv2
from threading import Thread

app = Flask(__name__)

class RoboflowWebcamServer:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.frame = None
        self.running = True

        if not self.cap.isOpened():
            raise RuntimeError("Error: Could not open webcam.")

    def get_frame(self):
        ret, frame = self.cap.read()
        if ret:
            _, buffer = cv2.imencode('.jpg', frame)
            return buffer.tobytes()
        return None



    def stop(self):
        self.running = False
        self.cap.release()
        cv2.destroyAllWindows()

webcam_server = RoboflowWebcamServer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(webcam_server.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
