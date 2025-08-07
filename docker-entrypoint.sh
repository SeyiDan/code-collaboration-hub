#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if nc -z db 5432 2>/dev/null; then
        echo "PostgreSQL is ready!"
        break
    fi
    echo "PostgreSQL is unavailable - sleeping ($i/30)"
    sleep 2
done

# Wait for Redis to be ready
echo "Waiting for Redis to be ready..."
until redis-cli -h redis ping > /dev/null 2>&1; do
    echo "Redis is unavailable - sleeping"
    sleep 2
done
echo "Redis is ready!"

# Initialize database
python -c "
from app import create_app, db
from app.models.user import User
from app.models.project import Project
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Create database tables
    db.create_all()
    print('Database tables created successfully')
    
    # Create default admin user if it doesn't exist
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@codecollabhub.com',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
        db.session.commit()
        print('Default admin user created (username: admin, password: admin123)')
"

# Run the application
exec "$@"
