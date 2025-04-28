#import flask for server
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    return '''
        <form action="/login" method="POST">
            <input type="text" name="user" placeholder="Username">
            <input type="password" name="password" placeholder="Password">
            <button type="submit">Login</button>
        </form>
    '''

@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('user', '')
    password = request.form.get('password', '')
    if user == 'admin' and password == '{flag}':
        return 'Welcome, admin! Here is your flag: {flag}'
    return 'Invalid login'

#run local server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

#lfi
from flask import Flask, request
import os

app = Flask(__name__)

# Safe base directory restriction
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    file = request.args.get('file', 'index.html')
    # Prevent directory traversal
    file_path = os.path.join(BASE_DIR, os.path.basename(file))
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return content
    except:
        return "Error reading file"

#execute drafted piece of code
#Run port 5000 on local server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
