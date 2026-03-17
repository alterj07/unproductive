import cv2 as cv
from ultralytics import YOLO

def runDetection():
    model = YOLO('yolov8n.pt')
    cam = cv.VideoCapture(0)
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break
        results = model(frame)
        annotated_frame = results[0].plot()
        cv.imshow('YOLOv8 Detection', annotated_frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    cam.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    runDetection()