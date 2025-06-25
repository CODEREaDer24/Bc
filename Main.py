from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configuring database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bc_pool_test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models (DB schema)
class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    strip_type = db.Column(db.String(50), nullable=False)
    results = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Routes
@app.route('/scan-test-strip', methods=['POST'])
def scan_test_strip():
    """
    Endpoint to handle test strip image, analyze it and return results
    """
    file = request.files['file']
    # Perform image processing here (use OpenCV or any other tool for recognition)
    results = process_image(file)  # Stub for image processing function
    return jsonify({"results": results})

@app.route('/get-recommendations', methods=['GET'])
def get_recommendations():
    """
    Returns recommendations based on latest results
    """
    # Query for latest test result
    last_result = TestResult.query.order_by(TestResult.timestamp.desc()).first()
    recommendations = recommend_chemicals(last_result)  # Stub for recommendation function
    return jsonify({"recommendations": recommendations})

@app.route('/save-test-result', methods=['POST'])
def save_test_result():
    """
    Endpoint to save the result to DB after analysis
    """
    data = request.json
    new_result = TestResult(user_id=data['user_id'], strip_type=data['strip_type'], results=data['results'])
    db.session.add(new_result)
    db.session.commit()
    return jsonify({"message": "Test result saved successfully!"})

# Utility functions (could be in utils.py)
def process_image(file):
    """
    Process the uploaded image and return the chemical levels.
    """
    # Image processing logic here using OpenCV or other image recognition libraries
    # For now, we'll just return some mock results
    return {"pH": 7.4, "chlorine": 3.0, "alkalinity": 100}

def recommend_chemicals(test_result):
    """
    Based on the test results, return chemical product recommendations.
    """
    # Example logic for recommendations
    recommendations = []
    if test_result['pH'] < 7.2:
        recommendations.append("Add pH Up")
    elif test_result['pH'] > 7.8:
        recommendations.append("Add pH Down")
    if test_result['chlorine'] < 2.0:
        recommendations.append("Add Chlorine Tablets")
    return recommendations

if __name__ == '__main__':
    app.run(debug=True)
