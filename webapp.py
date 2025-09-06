from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import os
import json
import sqlite3
from pathlib import Path
from ctforge import ChallengeGenerator, ChallengeType
import uuid
from werkzeug.utils import secure_filename
import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'custom_challenges'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize challenge generator
challenge_gen = ChallengeGenerator()

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_database():
    """Initialize the custom challenges database"""
    conn = sqlite3.connect('ctf_platform.db')
    cursor = conn.cursor()
    
    # Custom challenges table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_challenges (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            flag TEXT NOT NULL,
            author TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_by TEXT,
            reviewed_at TIMESTAMP,
            review_notes TEXT
        )
    ''')
    
    # Challenge files table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challenge_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_id TEXT,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            FOREIGN KEY (challenge_id) REFERENCES custom_challenges (id)
        )
    ''')
    
    # User roles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_roles (
            username TEXT PRIMARY KEY,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

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

def get_user_role(username):
    """Get user role from database"""
    conn = sqlite3.connect('ctf_platform.db')
    cursor = conn.cursor()
    cursor.execute('SELECT role FROM user_roles WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'user'

def set_user_role(username, role):
    """Set user role in database"""
    conn = sqlite3.connect('ctf_platform.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO user_roles (username, role) VALUES (?, ?)', (username, role))
    conn.commit()
    conn.close()

def get_custom_challenges(status=None):
    """Get custom challenges from database"""
    conn = sqlite3.connect('ctf_platform.db')
    cursor = conn.cursor()
    
    if status:
        cursor.execute('SELECT * FROM custom_challenges WHERE status = ? ORDER BY created_at DESC', (status,))
    else:
        cursor.execute('SELECT * FROM custom_challenges ORDER BY created_at DESC')
    
    challenges = []
    for row in cursor.fetchall():
        challenge = {
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'category': row[3],
            'flag': row[4],
            'author': row[5],
            'status': row[6],
            'created_at': row[7],
            'reviewed_by': row[8],
            'reviewed_at': row[9],
            'review_notes': row[10],
            'solved': session.get('solved_challenges', {}).get(f"custom_{row[0]}", False)
        }
        
        # Get associated files
        cursor.execute('SELECT filename, original_filename FROM challenge_files WHERE challenge_id = ?', (row[0],))
        challenge['files'] = [{'filename': f[0], 'original_filename': f[1]} for f in cursor.fetchall()]
        
        challenges.append(challenge)
    
    conn.close()
    return challenges

def save_custom_challenge(title, description, category, flag, author, files):
    """Save a new custom challenge to database"""
    challenge_id = str(uuid.uuid4())
    
    conn = sqlite3.connect('ctf_platform.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO custom_challenges (id, title, description, category, flag, author)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (challenge_id, title, description, category, flag, author))
    
    # Save file references
    for file_info in files:
        cursor.execute('''
            INSERT INTO challenge_files (challenge_id, filename, original_filename, file_path)
            VALUES (?, ?, ?, ?)
        ''', (challenge_id, file_info['filename'], file_info['original_filename'], file_info['file_path']))
    
    conn.commit()
    conn.close()
    return challenge_id

def update_challenge_status(challenge_id, status, reviewer, notes=None):
    """Update challenge review status"""
    conn = sqlite3.connect('ctf_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE custom_challenges 
        SET status = ?, reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP, review_notes = ?
        WHERE id = ?
    ''', (status, reviewer, notes, challenge_id))
    conn.commit()
    conn.close()

def check_custom_flag(challenge_id, submitted_flag):
    """Check if submitted flag is correct for custom challenge"""
    conn = sqlite3.connect('ctf_platform.db')
    cursor = conn.cursor()
    cursor.execute('SELECT flag FROM custom_challenges WHERE id = ? AND status = "approved"', (challenge_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return submitted_flag.strip() == result[0].strip()
    return False
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
    
    tab = request.args.get('tab', 'generated')
    
    if tab == 'custom':
        challenges = get_custom_challenges(status='approved')
        challenge_type = 'custom'
    else:
        challenges = get_challenges()
        challenge_type = 'generated'
    
    solved_count = len([c for c in challenges if c['solved']])
    total_score = solved_count * 100
    user_role = get_user_role(session['user'])
    
    return render_template('dashboard.html', 
                         challenges=challenges, 
                         solved_count=solved_count, 
                         total_score=total_score,
                         username=session['user'],
                         user_role=user_role,
                         active_tab=tab,
                         challenge_type=challenge_type)

@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('user', '')
    password = request.form.get('password', '')
    
    # Simple authentication - in production, use proper password hashing
    if user and password:  # Allow any non-empty credentials for demo
        session['user'] = user
        session['solved_challenges'] = session.get('solved_challenges', {})
        
        # Set admin role for specific users (demo purposes)
        if user.lower() in ['admin', 'administrator']:
            set_user_role(user, 'admin')
        
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
    challenge_type = request.form.get('challenge_type', 'generated')
    submitted_flag = request.form.get('flag')
    
    if challenge_type == 'custom':
        is_correct = check_custom_flag(challenge_id, submitted_flag)
        session_key = f"custom_{challenge_id}"
    else:
        is_correct = check_flag(challenge_id, submitted_flag)
        session_key = challenge_id
    
    if is_correct:
        # Mark challenge as solved
        if 'solved_challenges' not in session:
            session['solved_challenges'] = {}
        session['solved_challenges'][session_key] = True
        session.modified = True
        
        return jsonify({'success': True, 'message': 'Correct flag! Challenge solved!'})
    else:
        return jsonify({'success': False, 'message': 'Incorrect flag. Try again!'})

@app.route('/create_custom', methods=['GET', 'POST'])
def create_custom_challenge():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        flag = request.form.get('flag')
        
        if not all([title, description, category, flag]):
            flash('All fields are required', 'error')
            return redirect(url_for('create_custom_challenge'))
        
        # Handle file uploads
        uploaded_files = []
        files = request.files.getlist('files')
        
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                uploaded_files.append({
                    'filename': unique_filename,
                    'original_filename': filename,
                    'file_path': file_path
                })
        
        try:
            challenge_id = save_custom_challenge(title, description, category, flag, session['user'], uploaded_files)
            flash(f'Challenge "{title}" submitted for review!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error creating challenge: {str(e)}', 'error')
    
    return render_template('create_custom.html')

@app.route('/review', methods=['GET'])
def review_challenges():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    user_role = get_user_role(session['user'])
    if user_role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    pending_challenges = get_custom_challenges(status='pending')
    all_challenges = get_custom_challenges()
    
    return render_template('review.html', 
                         pending_challenges=pending_challenges,
                         all_challenges=all_challenges)

@app.route('/review_action', methods=['POST'])
def review_action():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    user_role = get_user_role(session['user'])
    if user_role != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    challenge_id = request.form.get('challenge_id')
    action = request.form.get('action')  # 'approve' or 'reject'
    notes = request.form.get('notes', '')
    
    if not challenge_id or not action:
        return jsonify({'success': False, 'message': 'Missing required parameters'})
    
    if action not in ['approve', 'reject']:
        return jsonify({'success': False, 'message': 'Invalid action'})
    
    try:
        # Convert action to past tense properly
        status = 'approved' if action == 'approve' else 'rejected'
        update_challenge_status(challenge_id, status, session['user'], notes)
        return jsonify({'success': True, 'message': f'Challenge {status} successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/custom_challenge/<challenge_id>')
def view_custom_challenge(challenge_id):
    if 'user' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('ctf_platform.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM custom_challenges WHERE id = ? AND status = "approved"', (challenge_id,))
    result = cursor.fetchone()
    
    if not result:
        flash('Challenge not found or not approved', 'error')
        return redirect(url_for('index'))
    
    challenge = {
        'id': result[0],
        'title': result[1],
        'description': result[2],
        'category': result[3],
        'author': result[5],
        'solved': session.get('solved_challenges', {}).get(f"custom_{result[0]}", False)
    }
    
    # Get associated files
    cursor.execute('SELECT filename, original_filename FROM challenge_files WHERE challenge_id = ?', (challenge_id,))
    challenge['files'] = [{'filename': f[0], 'original_filename': f[1]} for f in cursor.fetchall()]
    
    conn.close()
    return render_template('custom_challenge.html', challenge=challenge)

@app.route('/custom_file/<challenge_id>/<filename>')
def serve_custom_file(challenge_id, filename):
    if 'user' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('ctf_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT cf.file_path, cf.original_filename 
        FROM challenge_files cf
        JOIN custom_challenges cc ON cf.challenge_id = cc.id
        WHERE cc.id = ? AND cf.filename = ? AND cc.status = "approved"
    ''', (challenge_id, filename))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        flash('File not found', 'error')
        return redirect(url_for('view_custom_challenge', challenge_id=challenge_id))
    
    file_path, original_filename = result
    try:
        return send_file(file_path, as_attachment=True, download_name=original_filename)
    except Exception as e:
        flash(f'Error serving file: {str(e)}', 'error')
        return redirect(url_for('view_custom_challenge', challenge_id=challenge_id))

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
