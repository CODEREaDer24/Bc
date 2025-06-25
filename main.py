from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part in the request", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    image_url = url_for('static', filename='uploads/' + filename)
    results, debug_image_url = analyze_test_kit(filepath)

    return render_template('report.html', image_url=image_url, debug_image_url=debug_image_url, results=results)

def analyze_test_kit(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return {"error": "Could not read image"}, None

    resized = cv2.resize(image, (600, 400))
    debug_image = resized.copy()

    # Define regions of interest (x, y, w, h)
    regions = {
        'pH': (100, 150, 50, 50),
        'Chlorine': (200, 150, 50, 50),
        'Alkalinity': (300, 150, 50, 50)
    }

    results = {}

    for test, (x, y, w, h) in regions.items():
        roi = resized[y:y+h, x:x+w]
        avg_color = roi.mean(axis=0).mean(axis=0)  # BGR
        avg_rgb = avg_color[::-1]  # Convert to RGB
        results[test] = classify_color(test, avg_rgb)

        # Draw rectangle and label
        cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(debug_image, test, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # Save debug image with rectangles
    debug_filename = "debug_" + os.path.basename(image_path)
    debug_filepath = os.path.join(app.config['UPLOAD_FOLDER'], debug_filename)
    cv2.imwrite(debug_filepath, debug_image)

    debug_image_url = url_for('static', filename='uploads/' + debug_filename)
    return results, debug_image_url

def classify_color(test, rgb):
    r, g, b = rgb
    if test == 'pH':
        if r > 200:
            return "High (8.2+)"
        elif r > 150:
            return "Normal (7.4)"
        else:
            return "Low (6.8)"
    elif test == 'Chlorine':
        if g > 180:
            return "High (5.0+)"
        elif g > 120:
            return "Normal (2.0–4.0)"
        else:
            return "Low (<1.0)"
    elif test == 'Alkalinity':
        if b > 180:
            return "High (180+)"
        elif b > 120:
            return "Normal (100–150)"
        else:
            return "Low (<80)"
    return "Unknown"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
