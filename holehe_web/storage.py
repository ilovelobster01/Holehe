import os
import json
from datetime import datetime

STORAGE_DIR = os.path.join(os.path.dirname(__file__), 'storage')
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def get_search_path(search_id):
    """Returns the path to the JSON file for a given search ID."""
    return os.path.join(STORAGE_DIR, f"{search_id}.json")

def save_search_data(search_id, data):
    """Saves search data to a JSON file."""
    filepath = get_search_path(search_id)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_search_data(search_id):
    """Loads search data from a JSON file."""
    filepath = get_search_path(search_id)
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as f:
        return json.load(f)

def init_search(email, search_id):
    """Initializes the search data file."""
    initial_data = {
        'search_id': search_id,
        'email': email,
        'status': 'running',
        'progress': 0,
        'message': 'Starting search...',
        'results': None,
        'created_at': datetime.now().isoformat()
    }
    save_search_data(search_id, initial_data)
    return initial_data

def update_search_status(search_id, progress, message, status='running'):
    """Updates the status of a search."""
    data = load_search_data(search_id)
    if not data:
        return
    data['progress'] = progress
    data['message'] = message
    data['status'] = status
    save_search_data(search_id, data)

def save_results(search_id, results):
    """Saves the final results of a search."""
    data = load_search_data(search_id)
    if not data:
        return
    data['results'] = results
    data['status'] = 'completed'
    data['progress'] = 100
    data['message'] = f"Found {results.get('found_count', 0)} accounts"
    data['completed_at'] = datetime.now().isoformat()
    save_search_data(search_id, data)

def set_search_error(search_id, error_message):
    """Sets an error status for a search."""
    data = load_search_data(search_id)
    if not data:
        return
    data['status'] = 'error'
    data['message'] = error_message
    save_search_data(search_id, data)
