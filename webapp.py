from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import json
import sqlite3
from pathlib import Path
from ctforge import ChallengeGenerator, ChallengeType
import uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize challenge generator
challenge_gen = ChallengeGenerator()

def get_challenges():
    """Get all available challenges from the challenges directory"""
    challenges_dir = Path(__file__).parent / 'challenges'
    challenges = []
    
    if challenges_dir.exists():
        for challenge_dir in challenges_dir.iterdir():
            if challenge_dir.is_dir():
                challenge_info = {
                    'id': challenge_dir.name,
                    'name': challenge_dir.name.replace('_', ' ').title(),
                    'path': str(challenge_dir),
                    'solved': session.get('solved_challenges', {}).get(challenge_dir.name, False)
                }
                
                # Try to read README for description
                readme_path = challenge_dir / 'README.md'
                if readme_path.exists():
                    with open(readme_path, 'r') as f:
                        challenge_info['description'] = f.read()[:200] + '...'
                else:
                    challenge_info['description'] = 'No description available'
                
                challenges.append(challenge_info)
    
    return challenges

def check_flag(challenge_id, submitted_flag):
    """Check if submitted flag is correct for the challenge"""
    challenge_dir = Path(__file__).parent / 'challenges' / challenge_id
    flag_file = challenge_dir / 'flag.txt'
    
    if flag_file.exists():
        with open(flag_file, 'r') as f:
            correct_flag = f.read().strip()
            return submitted_flag.strip() == correct_flag
    return False

@app.route('/', methods=['GET'])
def index():
    if 'user' not in session:
        return render_template('login.html', error=None)
    
    challenges = get_challenges()
    solved_count = len([c for c in challenges if c['solved']])
    total_score = solved_count * 100  # 100 points per challenge
    
    return render_template('dashboard.html', 
                         challenges=challenges, 
                         solved_count=solved_count, 
                         total_score=total_score,
                         username=session['user'])

@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('user', '')
    password = request.form.get('password', '')
    
    # Simple authentication - in production, use proper password hashing
    if user and password:  # Allow any non-empty credentials for demo
        session['user'] = user
        session['solved_challenges'] = session.get('solved_challenges', {})
        return redirect(url_for('index'))
    
    return render_template('login.html', error='Please enter both username and password')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/challenge/<challenge_id>')
def view_challenge(challenge_id):
    if 'user' not in session:
        return redirect(url_for('index'))
    
    challenge_dir = Path(__file__).parent / 'challenges' / challenge_id
    if not challenge_dir.exists():
        flash('Challenge not found', 'error')
        return redirect(url_for('index'))
    
    challenge_info = {
        'id': challenge_id,
        'name': challenge_id.replace('_', ' ').title(),
        'solved': session.get('solved_challenges', {}).get(challenge_id, False)
    }
    
    # Read README
    readme_path = challenge_dir / 'README.md'
    if readme_path.exists():
        with open(readme_path, 'r') as f:
            challenge_info['description'] = f.read()
    
    # List available files
    challenge_info['files'] = []
    for file_path in challenge_dir.iterdir():
        if file_path.is_file() and file_path.name not in ['flag.txt', 'SOLUTION.md']:
            challenge_info['files'].append(file_path.name)
    
    return render_template('challenge.html', challenge=challenge_info)

@app.route('/submit_flag', methods=['POST'])
def submit_flag():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    challenge_id = request.form.get('challenge_id')
    submitted_flag = request.form.get('flag')
    
    if check_flag(challenge_id, submitted_flag):
        # Mark challenge as solved
        if 'solved_challenges' not in session:
            session['solved_challenges'] = {}
        session['solved_challenges'][challenge_id] = True
        session.modified = True
        
        return jsonify({'success': True, 'message': 'Correct flag! Challenge solved!'})
    else:
        return jsonify({'success': False, 'message': 'Incorrect flag. Try again!'})

@app.route('/generate', methods=['GET', 'POST'])
def generate_challenge():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        challenge_type = request.form.get('type')
        
        try:
            # Use existing challenge generator
            challenge_dir = challenge_gen.create_challenge_directory('./challenges')
            flag = challenge_gen.generate_flag()
            challenge_gen.save_flag(challenge_dir, flag)
            
            if challenge_type == 'web':
                challenge_gen.generate_web_challenge(challenge_dir, flag)
            elif challenge_type == 'crypto':
                challenge_gen.generate_crypto_challenge(challenge_dir, flag)
            elif challenge_type == 'forensics':
                challenge_gen.generate_forensics_challenge(challenge_dir, flag)
            
            flash(f'Challenge generated successfully! ID: {challenge_dir.name}', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Error generating challenge: {str(e)}', 'error')
    
    return render_template('generate.html')

@app.route('/file/<challenge_id>/<filename>')
def serve_challenge_file(challenge_id, filename):
    if 'user' not in session:
        return redirect(url_for('index'))
    
    challenge_dir = Path(__file__).parent / 'challenges' / challenge_id
    file_path = challenge_dir / filename
    
    # Security check - prevent access to flag.txt and solution files
    if filename in ['flag.txt', 'SOLUTION.md'] or not file_path.exists():
        flash('File not accessible', 'error')
        return redirect(url_for('view_challenge', challenge_id=challenge_id))
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return f'<pre>{content}</pre>'
    except:
        try:
            # If it's a binary file, provide download link
            return f'<p>Binary file. <a href="/download/{challenge_id}/{filename}">Download {filename}</a></p>'
        except:
            return 'Error reading file'

@app.route('/download/<challenge_id>/<filename>')
def download_challenge_file(challenge_id, filename):
    if 'user' not in session:
        return redirect(url_for('index'))
    
    from flask import send_file
    challenge_dir = Path(__file__).parent / 'challenges' / challenge_id
    file_path = challenge_dir / filename
    
    if filename not in ['flag.txt', 'SOLUTION.md'] and file_path.exists():
        return send_file(file_path, as_attachment=True)
    
    flash('File not found or not accessible', 'error')
    return redirect(url_for('view_challenge', challenge_id=challenge_id))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
