from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime

app = Flask(__name__, static_folder='assets', static_url_path='/assets')

# Mock data - în memorie, fără bază de date
USER_DATA = {
    'name': 'Mark',
    'score': 75,
    'brief_summaries': {
        'consum': '2 meals, 1.5L water',
        'somn': '7h good sleep',
        'vitale': 'BP: 120/80, HR: 72',
        'sport': '30min running'
    }
}

MOCK_CHAT = []

CLINICS = [
    {'id': 1, 'nume': 'City Medical Center', 'categorie': 'General', 'rating': 4.8, 'reviews': 245},
    {'id': 2, 'nume': 'Heart Care Clinic', 'categorie': 'Cardiology', 'rating': 4.9, 'reviews': 189},
    {'id': 3, 'nume': 'NeuroHealth', 'categorie': 'Neurology', 'rating': 4.7, 'reviews': 156},
]


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/add-data')
def add_data():
    return render_template('add-data.html')


@app.route('/schedule')
def schedule():
    return render_template('schedule.html')


# API endpoints - returnează date mock
@app.route('/api/v1/generate_alert')
def generate_alert():
    return jsonify({
        'success': True,
        'health_score': USER_DATA['score'],
        'brief_summaries': USER_DATA['brief_summaries'],
        'summary': {},
        'feedback': 'Mock feedback - AI not connected for demo'
    })


@app.route('/api/v1/cabinete')
def get_cabinete():
    return jsonify({
        'success': True,
        'cabinete': CLINICS
    })


@app.route('/ask', methods=['POST'])
def ask():
    question = request.form.get('question', '')
    MOCK_CHAT.append({'role': 'user', 'content': question})
    response = "This is a demo response. AI is not connected."
    MOCK_CHAT.append({'role': 'assistant', 'content': response})

    return jsonify({
        'success': True,
        'generated_feedback': response,
        'question': question,
        'user_id': 'demo',
        'summary': {}
    })


@app.route('/api/v1/add_health_data', methods=['POST'])
def add_health_data():
    # Doar returnează success
    return jsonify({'success': True, 'message': 'Data logged (demo mode)'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)