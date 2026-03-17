import cv2 as cv
from ultralytics import YOLO
import subprocess
import threading

model = YOLO('yolov8n.pt')
TARGET_OBJECT = "cell phone"
audio_file = 'pipe.wav'
isPlaying = False

def playSound():
    global isPlaying
    isPlaying = True
    subprocess.run(['afplay', audio_file])
    isPlaying = False

def isTargetPresent(frame, target: str, threshold: float = 0.5) -> bool:
    results = model(frame, verbose=False)

    for result in results:
        for box in result.boxes:
            confidence = float(box.conf)
            class_id = int(box.cls)
            class_name = model.names[class_id]

            if class_name == target and confidence >= threshold:
                return True

    return False

def runDetection():
    cam = cv.VideoCapture(0)
    while True:
        ret, frame = cam.read()

        if not ret:
            print("Failed to grab frame")
            break
        
        results = model(frame)
        annotated_frame = results[0].plot()
        cv.imshow('Unproductive?', annotated_frame)
        
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
        
        if isTargetPresent(frame, TARGET_OBJECT) and not isPlaying:
        # if isTargetPresent(frame, TARGET_OBJECT):
            threading.Thread(target=playSound, daemon=True).start()



    cam.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    runDetection()