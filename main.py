import cv2 as cv
from ultralytics import YOLO
# import subprocess
import threading
from pydub import AudioSegment
from pydub.playback import play

from flask import Flask, Response

model = YOLO('yolov9c.pt')
TARGET_OBJECT = "cell phone"
audio_file = 'pipe.wav'
dbBoost = 20
isPlaying = False
lock = threading.Lock()
latest_frame = None

app = Flask(__name__)

#increasing the volume of audio_file by dbBoost decibels and playing it
def playIncreasedSound():
    global isPlaying
    isPlaying = True
    audio = AudioSegment.from_file(audio_file, format="wav")
    louder_audio = audio + dbBoost
    # subprocess.run(['afplay', audio_file])
    play(louder_audio)
    isPlaying = False

#checking if the target object is present in the frame with 0.3 threshold
def isTargetPresent(frame, target: str, threshold: float = 0.3) -> bool:
    results = model(frame, verbose=False)

    for result in results:
        for box in result.boxes:
            confidence = float(box.conf)
            class_id = int(box.cls)
            class_name = model.names[class_id]

            if class_name == target and confidence >= threshold:
                return True

    return False

#main function to run detection loop and show frames
def runDetection():
    global latest_frame
    cam = cv.VideoCapture(0)
    
    while True:
        ret, frame = cam.read()

        if not ret:
            print("Failed to grab frame")
            break
        
        results = model(frame)
        annotated_frame = results[0].plot()
        # cv.imshow('Unproductive?', annotated_frame)
        
        # if cv.waitKey(1) & 0xFF == ord('q'):
        #     break
        
        if isTargetPresent(frame, TARGET_OBJECT) and not isPlaying:
        # if isTargetPresent(frame, TARGET_OBJECT):
            # threading.Thread(target=playSound, daemon=True).start()
            threading.Thread(target=playIncreasedSound, daemon=True).start()
        with lock:
            latest_frame = annotated_frame.copy()



    cam.release()
    # cv.destroyAllWindows()

def generate_frames():
    while True:
        with lock:
            if latest_frame is None:
                continue
            _, buffer = cv.imencode('.jpg', latest_frame)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return open('templates/index.html').read()


if __name__ == '__main__':
    # Start detection in background thread, then start Flask
    threading.Thread(target=runDetection, daemon=True).start()
    app.run(host='127.0.0.1', port=5000)

# if __name__ == "__main__":
#     runDetection()