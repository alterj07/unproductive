import cv2 as cv
from ultralytics import YOLO
# import subprocess
import threading
from pydub import AudioSegment
from pydub.playback import play


model = YOLO('yolov9c.pt')
TARGET_OBJECT = "cell phone"
audio_file = 'pipe.wav'
isPlaying = False
dbBoost = 20

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
            # threading.Thread(target=playSound, daemon=True).start()
            threading.Thread(target=playIncreasedSound, daemon=True).start()



    cam.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    runDetection()