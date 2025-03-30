from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Configure Flask app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///gdpr.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Sample data for demonstration
SAMPLE_TASKS = [
    {
        'id': 1,
        'title': 'Update Privacy Policy',
        'description': 'Review and update privacy policy to comply with GDPR requirements',
        'status': 'pending',
        'deadline': '2024-04-01'
    },
    {
        'id': 2,
        'title': 'Data Processing Audit',
        'description': 'Conduct audit of all data processing activities',
        'status': 'completed',
        'deadline': '2024-03-15'
    }
]

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/tasks')
def get_tasks():
    return jsonify(SAMPLE_TASKS)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    new_task = {
        'id': len(SAMPLE_TASKS) + 1,
        'title': data['title'],
        'description': data.get('description', ''),
        'status': 'pending',
        'deadline': data['deadline']
    }
    SAMPLE_TASKS.append(new_task)
    return jsonify(new_task), 201

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# For local development
if __name__ == '__main__':
    app.run(debug=True) 