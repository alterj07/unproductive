import cv2 as cv
import base64
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import numpy as np

app = Flask(__name__)
CORS(app)
model = YOLO('yolov8n.pt')
TARGET_OBJECT = "cell phone"
CONFIDENCE_THRESHOLD = 0.5


def process_frame_for_detection(frame_data):
    try:
        results = model(frame_data, verbose=False)
        
        target_found = False
        detections = []
        
        for result in results:
            for box in result.boxes:
                confidence = float(box.conf)
                class_id = int(box.cls)
                class_name = model.names[class_id]
                
                detection_info = {
                    'class': class_name,
                    'confidence': float(confidence),
                    'coordinates': box.xyxy[0].tolist()
                }
                detections.append(detection_info)
                
                if class_name == TARGET_OBJECT and confidence >= CONFIDENCE_THRESHOLD:
                    target_found = True
        
        return {
            'target_found': target_found,
            'detections': detections,
            'total_detections': len(detections)
        }
    
    except Exception as e:
        return {'error': str(e), 'target_found': False}


def annotate_frame_with_detections(frame_data, results):
    annotated = results[0].plot()
    _, buffer = cv.imencode('.jpg', annotated)
    return buffer.tobytes()



@app.route('/api/detect', methods=['POST'])
def detect():
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        image_data = base64.b64decode(data['image'])
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv.imdecode(nparr, cv.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        detection_result = process_frame_for_detection(frame)
        
        model_results = model(frame, verbose=False)
        annotated_jpg = annotate_frame_with_detections(frame, model_results)
        annotated_base64 = base64.b64encode(annotated_jpg).decode('utf-8')
        
        response = {
            'target_found': detection_result['target_found'],
            'detections': detection_result['detections'],
            'annotated_frame': 'data:image/jpeg;base64,' + annotated_base64,
            'message': f"Found {detection_result['total_detections']} object(s)"
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/detect-batch', methods=['POST'])
def detect_batch():
    try:
        data = request.get_json()
        
        if not data or 'images' not in data:
            return jsonify({'error': 'No images provided'}), 400
        
        images = data['images']
        batch_results = []
        
        for image_b64 in images:
            image_data = base64.b64decode(image_b64)
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv.imdecode(nparr, cv.IMREAD_COLOR)
            
            if frame is not None:
                detection_result = process_frame_for_detection(frame)
                batch_results.append(detection_result)
        
        return jsonify({
            'results': batch_results,
            'frames_processed': len(batch_results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'server': 'Running'})


@app.route('/')
def index():
    try:
        with open('templates/index.html', 'r') as f:
            return f.read()
    except:
        return "Frontend not found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

