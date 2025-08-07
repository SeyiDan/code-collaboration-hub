# CodeCollaborationHub Documentation

## Overview

CodeCollaborationHub is a web-based platform that enables real-time collaborative code editing and sharing. It allows developers to create, manage, and collaborate on coding projects with features similar to platforms like GitHub Codespaces or repl.it, but focusing specifically on real-time collaboration.

## Technologies Used

### Backend Technologies

1. **Flask (v2.3.3)**: A lightweight Python web framework that provides the foundation for the application
   - **Flask-SQLAlchemy (v3.1.1)**: ORM for database interactions
   - **Flask-Login (v0.6.2)**: Handles user authentication and session management
   - **Flask-SocketIO (v5.3.5)**: Enables real-time bidirectional communication via WebSockets

2. **WebSocket Technology**:
   - **gevent (v23.9.1)**: An asynchronous framework that provides a high-level synchronous API on top of the libev or libuv event loop
   - **gevent-websocket (v0.10.1)**: WebSocket implementation for gevent

3. **Database**:
   - **SQLite** (development): File-based database used in development environment
   - **PostgreSQL** (production): Robust relational database for production deployment

4. **Code Highlighting**:
   - **Pygments (v2.16.1)**: Library for syntax highlighting of source code

5. **Server Deployment**:
   - **Gunicorn (v21.2.0)**: WSGI HTTP Server for production deployment
   - **Docker**: Containerization for consistent deployment

### Frontend Technologies

1. **HTML/CSS/JavaScript**: Standard web technologies for the frontend interface
2. **Socket.IO Client**: JavaScript library that connects to the Socket.IO server
3. **Bootstrap** (likely): For responsive UI components and styling

## Application Architecture

### Project Structure

```
CodeCollaborationHub/
├── app/                      # Application package
│   ├── __init__.py           # Initializes Flask app and extensions
│   ├── models/               # Database models
│   │   ├── user.py           # User model with authentication
│   │   ├── project.py        # Project and Collaboration models
│   ├── routes/               # Route handlers
│   │   ├── auth.py           # Authentication routes (login, register)
│   │   ├── main.py           # Main application routes
│   ├── sockets/              # WebSocket event handlers
│   │   ├── events.py         # Handles real-time events
├── templates/                # HTML templates
├── static/                   # Static assets (CSS, JS, images)
├── requirements.txt          # Python dependencies
├── app.py                    # Application entry point
├── wsgi.py                   # WSGI entry point for production
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose configuration
```

### Key Components

#### 1. Database Models

- **User**: Stores user accounts with secure password hashing
- **Project**: Stores coding projects with metadata and content
- **Collaboration**: Represents a user's access to a project (read/write/admin permissions)

#### 2. Authentication System

- User registration with unique username/email
- Secure password hashing
- Login/logout functionality
- Session management with Flask-Login

#### 3. Real-time Collaboration

- WebSocket connections managed through Flask-SocketIO
- Events for cursor position, code updates, and user presence
- Room-based collaboration (each project has its own "room")
- Permission-based editing

#### 4. Features

- Project creation and management
- Syntax highlighting for multiple programming languages
- Collaborator management with different permission levels
- Public/private project visibility
- Real-time code editing

## How the Real-time Collaboration Works

1. **Connection Establishment**:
   - When a user opens a project, the client establishes a WebSocket connection using Socket.IO
   - The server assigns the user to a "room" specific to that project

2. **Code Synchronization**:
   - When a user makes changes to the code, the client sends an update event to the server
   - The server validates the user's permissions
   - If authorized, the server updates the project in the database
   - The server broadcasts the changes to all other users in the same project room

3. **Cursor Tracking**:
   - Users' cursor positions are tracked and broadcast to other collaborators
   - This helps collaborators see where others are working in real-time

4. **User Presence**:
   - Join/leave events notify other users when someone enters or exits the project

## Deployment

### Docker Setup

The application is containerized using Docker with the following components:

- **Web Service**: The Flask application served by Gunicorn with gevent workers
- **Database Service**: PostgreSQL database for data persistence

The `Dockerfile` configures the environment:
- Uses Python 3.12 as the base image
- Installs required dependencies
- Sets up environment variables
- Configures Gunicorn with gevent to serve the application

### Environment Variables

The application uses the following environment variables:
- `SECRET_KEY`: For securing sessions and cookies
- `DATABASE_URI`: Connection string for the database
- `FLASK_APP`: Entry point for the Flask application
- `FLASK_ENV`: Environment setting (development/production)

## Security Considerations

1. **Authentication**: Secure password hashing with Werkzeug
2. **Authorization**: Permission-based access to projects
3. **Input Validation**: Form validation to prevent injection attacks
4. **CSRF Protection**: Flask's built-in CSRF protection for forms
5. **Database Security**: Parameterized queries via SQLAlchemy

## Recent Updates and Optimizations

1. **WebSocket Backend Change**: 
   - Changed from eventlet to gevent for better compatibility with Python 3.13
   - Updated the Gunicorn configuration to use gevent workers

2. **Pygments Integration Fix**:
   - Added error handling to the `get_languages()` function
   - Added defensive code to handle potential changes in the Pygments library

3. **Docker Optimization**:
   - Updated to use Python 3.12 for better stability
   - Optimized Dockerfile for faster builds

## Running the Application

### Development Mode

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Production Mode (Docker)

```bash
# Build and start containers
docker-compose up -d
```

## Troubleshooting

1. **WebSocket Connection Issues**:
   - Ensure the client is connecting to the correct URL
   - Check if there are any proxy/firewall issues
   - Verify the async_mode matches between client and server

2. **Database Errors**:
   - Check database connection string
   - Ensure tables are created properly with `db.create_all()`

3. **Python Version Compatibility**:
   - The application is optimized for Python 3.12
   - If using Python 3.13, ensure all dependencies are compatible

## Future Enhancement Possibilities

1. **File System Integration**: Allow multiple files per project
2. **Version Control**: Add Git-like versioning
3. **AI Code Assistance**: Integrate with AI coding assistants
4. **Mobile Support**: Responsive design for mobile editing
5. **Testing Infrastructure**: Add automated tests and CI/CD

## License

The project is licensed under the MIT License. 