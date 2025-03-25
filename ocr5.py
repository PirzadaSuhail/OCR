from flask import Flask, request, jsonify
from celery import Celery
import base64
import io
import pytesseract
import os
from PIL import Image  
app = Flask(__name__)

# Initialize Celery with Redis as the message broker
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Directory to store OCR results
OCR_RESULTS_DIR = "ocr_results"
if not os.path.exists(OCR_RESULTS_DIR):
    os.makedirs(OCR_RESULTS_DIR)

@celery.task
def perform_ocr(image_data, task_id):
    try:
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        recognized_text = pytesseract.image_to_string(image)

        result_file = os.path.join(OCR_RESULTS_DIR, f"{task_id}.txt")
        with open(result_file, "w") as f:
            f.write(recognized_text)

    except Exception as e:
        return str(e)


@app.route('/image-sync', methods=['POST'])
def image_sync():
    try:
        data = request.get_json()
        if 'image_data' not in data:
            return jsonify({'error': 'Missing image_data parameter'}), 400

        image_data = data['image_data']
        image_bytes = base64.b64decode(image_data)

        image = Image.open(io.BytesIO(image_bytes))

        recognized_text = pytesseract.image_to_string(image)

        response_data = {'text': recognized_text}
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/image', methods=['POST'])
def image():
    try:
        data = request.get_json()
        if 'image_data' not in data:
            return jsonify({'error': 'Missing image_data parameter'}), 400

        image_data = data['image_data']
        task_id = str(hash(image_data))  # Generate a unique task_id

        # Perform OCR asynchronously using Celery
        perform_ocr.apply_async(args=(image_data, task_id))

        response_data = {'task_id': task_id}
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/image', methods=['GET'])
def get_image():
    try:
        data = request.get_json()
        if 'task_id' not in data:
            return jsonify({'error': 'Missing task_id parameter'}), 400

        task_id = data['task_id']
        result_file = os.path.join(OCR_RESULTS_DIR, f"{task_id}.txt")

        if os.path.exists(result_file):
            with open(result_file, "r") as f:
                recognized_text = f.read()
            response_data = {task_id: recognized_text}
        else:
            response_data = {task_id: None}

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)