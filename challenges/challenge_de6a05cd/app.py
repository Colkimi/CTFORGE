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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
