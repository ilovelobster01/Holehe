import time
import threading
from flask import Blueprint, render_template, request, jsonify, send_file
from datetime import datetime

from . import storage
from . import search as holehe_search
from . import reporting
from .utils import is_email

main = Blueprint('main', __name__, static_folder='static', template_folder='templates')

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/search', methods=['POST'])
def search():
    email = request.form.get('email', '').strip()
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    if not is_email(email):
        return jsonify({'error': 'Please enter a valid email address'}), 400

    search_id = f"{email.replace('@', '_').replace('.', '_')}_{int(time.time())}"

    storage.init_search(email, search_id)

    thread = threading.Thread(target=holehe_search.run_holehe_search, args=(email, search_id))
    thread.daemon = True
    thread.start()

    return jsonify({'search_id': search_id})

@main.route('/status/<search_id>')
def get_status(search_id):
    data = storage.load_search_data(search_id)
    if not data:
        return jsonify({'status': 'not_found'}), 404

    return jsonify({
        'status': data.get('status'),
        'progress': data.get('progress'),
        'message': data.get('message')
    })

@main.route('/results/<search_id>')
def get_results(search_id):
    data = storage.load_search_data(search_id)
    if not data or data.get('status') != 'completed':
        return jsonify({'error': 'Results not found or search not completed'}), 404

    return jsonify(data['results'])

@main.route('/download/<search_id>')
def download_pdf(search_id):
    data = storage.load_search_data(search_id)
    if not data or not data.get('results'):
        return jsonify({'error': 'Results not found'}), 404

    results = data['results']
    email = data['email']

    pdf_path = reporting.create_pdf_report(results, email)

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f'holehe_results_{email.replace("@", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
        mimetype='application/pdf'
    )
