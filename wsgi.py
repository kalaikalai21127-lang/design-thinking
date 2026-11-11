import os
import sys

# Ensure the backend directory is in the Python search path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)