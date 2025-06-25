from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bc_pool_test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Models ---
class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    strip_type = db.Column(db.String(50), nullable=False)
    results = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- Routes ---
@app.route('/scan-test-strip', methods=['POST'])
def scan_test_strip():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    results = process_image(file)
    return jsonify({"results": results})

@app.route('/save-test-result', methods=['POST'])
def save_test_result():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON data"}), 400

    new_result = TestResult(
        user_id=data['user_id'],
        strip_type=data['strip_type'],
        results=str(data['results'])  # Store as stringified dict
    )
    db.session.add(new_result)
    db.session.commit()
    return jsonify({"message": "Test result saved successfully!"})

@app.route('/get-recommendations', methods=['GET'])
def get_recommendations():
    last_result = TestResult.query.order_by(TestResult.timestamp.desc()).first()
    if not last_result:
        return jsonify({"error": "No test results found"}), 404

    parsed_result = eval(last_result.results)  # 🔥 CAUTION: insecure for real use
    recommendations = recommend_chemicals(parsed_result)
    return jsonify({"recommendations": recommendations})

# --- Utility Logic ---
def process_image(file):
    # Placeholder for actual image processing (OpenCV etc.)
    return {"pH": 7.4, "chlorine": 3.0, "alkalinity": 100}

def recommend_chemicals(results):
    recs = []
    if results["pH"] < 7.2:
        recs.append("Add pH Up")
    elif results["pH"] > 7.8:
        recs.append("Add pH Down")
    if results["chlorine"] < 2.0:
        recs.append("Add Chlorine Tablets")
    return recs

# --- App Start ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Make sure DB tables exist
    app.run(host="0.0.0.0", port=10000, debug=True)
