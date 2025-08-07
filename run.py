"""
Simplified run script for CodeCollaborationHub
Use this to test the application without SocketIO
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Run with regular Flask for troubleshooting
    print("Starting Flask app in debug mode...")
    print("Access the application at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 