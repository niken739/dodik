import sys
from pathlib import Path

# Add the backend directory to Python path so we can import app
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
