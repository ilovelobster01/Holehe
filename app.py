#!/usr/bin/env python3
"""
Holehe Web Interface
A simple Flask web application for the Holehe email OSINT tool
"""

import os
import sys
import json
import subprocess
import tempfile
import csv
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import zipfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import threading
import time
import asyncio
import trio
from contextlib import asynccontextmanager

# Add the holehe source to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'holehe_source'))

# Import holehe modules
from holehe.core import import_submodules, get_functions, launch_module, is_email
from holehe.instruments import TrioProgress
import httpx

app = Flask(__name__)
app.config['SECRET_KEY'] = 'holehe-web-interface-secret-key'

# Global variable to store search results
search_results = {}
search_status = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    email = request.form.get('email', '').strip()
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    if not is_email(email):
        return jsonify({'error': 'Please enter a valid email address'}), 400
    
    # Generate unique search ID
    search_id = f"{email}_{int(time.time())}"
    
    # Initialize search status
    search_status[search_id] = {
        'status': 'running',
        'progress': 0,
        'message': 'Starting search...'
    }
    
    # Start search in background thread
    thread = threading.Thread(target=run_holehe_search, args=(email, search_id))
    thread.daemon = True
    thread.start()
    
    return jsonify({'search_id': search_id})

@app.route('/status/<search_id>')
def get_status(search_id):
    return jsonify(search_status.get(search_id, {'status': 'not_found'}))

@app.route('/results/<search_id>')
def get_results(search_id):
    if search_id in search_results:
        return jsonify(search_results[search_id])
    return jsonify({'error': 'Results not found'}), 404

@app.route('/download/<search_id>')
def download_pdf(search_id):
    if search_id not in search_results:
        return jsonify({'error': 'Results not found'}), 404
    
    results = search_results[search_id]
    email = results.get('email', 'unknown')
    
    # Create PDF
    pdf_path = create_pdf_report(results, email)
    
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f'holehe_results_{email.replace("@", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
        mimetype='application/pdf'
    )

def run_holehe_search(email, search_id):
    """Run Holehe search in background using trio"""
    try:
        search_status[search_id]['message'] = 'Loading modules...'
        search_status[search_id]['progress'] = 10
        
        # Import Modules
        modules = import_submodules("holehe.modules")
        websites = get_functions(modules)
        
        search_status[search_id]['progress'] = 20
        search_status[search_id]['message'] = f'Checking {len(websites)} websites...'
        
        # Run the trio search
        results = trio.run(run_holehe_async, email, websites)
        
        search_status[search_id]['progress'] = 90
        search_status[search_id]['message'] = 'Processing results...'
        
        # Process results
        found_profiles = []
        not_found_profiles = []
        rate_limited_profiles = []
        error_profiles = []
        
        for result in results:
            profile_data = {
                'site': result['name'],
                'domain': result['domain'],
                'method': result.get('method', 'unknown'),
                'emailrecovery': result.get('emailrecovery'),
                'phoneNumber': result.get('phoneNumber'),
                'others': result.get('others')
            }
            
            if result.get('error'):
                error_profiles.append({
                    **profile_data,
                    'status': 'error',
                    'reason': 'Error occurred during check'
                })
            elif result.get('rateLimit'):
                rate_limited_profiles.append({
                    **profile_data,
                    'status': 'rate_limited',
                    'reason': 'Rate limited'
                })
            elif result.get('exists'):
                found_profiles.append({
                    **profile_data,
                    'status': 'found'
                })
            else:
                not_found_profiles.append({
                    **profile_data,
                    'status': 'not_found'
                })
        
        search_results[search_id] = {
            'email': email,
            'found_profiles': found_profiles,
            'not_found_profiles': not_found_profiles,
            'rate_limited_profiles': rate_limited_profiles,
            'error_profiles': error_profiles,
            'total_sites': len(websites),
            'found_count': len(found_profiles),
            'not_found_count': len(not_found_profiles),
            'rate_limited_count': len(rate_limited_profiles),
            'error_count': len(error_profiles),
            'search_time': datetime.now().isoformat()
        }
        
        search_status[search_id]['status'] = 'completed'
        search_status[search_id]['progress'] = 100
        search_status[search_id]['message'] = f'Found {len(found_profiles)} accounts'
            
    except Exception as e:
        search_status[search_id]['status'] = 'error'
        search_status[search_id]['message'] = f'Error: {str(e)}'

async def run_holehe_async(email, websites):
    """Run holehe async search"""
    timeout = 10
    client = httpx.AsyncClient(timeout=timeout)
    out = []
    
    try:
        # Use trio for concurrent execution
        async with trio.open_nursery() as nursery:
            for website in websites:
                nursery.start_soon(launch_module, website, email, client, out)
    finally:
        await client.aclose()
    
    # Sort by module names
    return sorted(out, key=lambda i: i['name'])

def create_pdf_report(results, email):
    """Create PDF report from search results"""
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, f'holehe_report_{email.replace("@", "_")}_{int(time.time())}.pdf')
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.darkblue
    )
    story.append(Paragraph(f'Holehe Results for: {email}', title_style))
    story.append(Spacer(1, 20))
    
    # Summary
    summary_data = [
        ['Search Date', results.get('search_time', 'Unknown')],
        ['Email Address', email],
        ['Total Sites Checked', str(results.get('total_sites', 0))],
        ['Accounts Found', str(results.get('found_count', 0))],
        ['Not Found', str(results.get('not_found_count', 0))],
        ['Rate Limited', str(results.get('rate_limited_count', 0))],
        ['Errors', str(results.get('error_count', 0))],
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 30))
    
    # Found Profiles Only
    found_profiles = results.get('found_profiles', [])
    if found_profiles:
        story.append(Paragraph('Found Accounts:', styles['Heading2']))
        story.append(Spacer(1, 12))
        
        profile_data = [['Site', 'Domain', 'Additional Info']]
        for profile in found_profiles:
            additional_info = []
            if profile.get('emailrecovery'):
                additional_info.append(f"Email Recovery: {profile['emailrecovery']}")
            if profile.get('phoneNumber'):
                additional_info.append(f"Phone: {profile['phoneNumber']}")
            if profile.get('others'):
                for key, value in profile['others'].items():
                    additional_info.append(f"{key}: {value}")
            
            profile_data.append([
                profile['site'],
                profile['domain'],
                '\n'.join(additional_info) if additional_info else 'No additional info'
            ])
        
        profile_table = Table(profile_data, colWidths=[1.5*inch, 2*inch, 2.5*inch])
        profile_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(profile_table)
    else:
        story.append(Paragraph('No accounts found for this email address.', styles['Normal']))
    
    doc.build(story)
    return pdf_path

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Holehe Web Interface')
    parser.add_argument('--port', type=int, default=5001, help='Port to run the server on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind the server to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    app.run(debug=args.debug, host=args.host, port=args.port)