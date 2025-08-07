#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=postgres psql -h db -U postgres -d codecollaboration -c "SELECT 1" > /dev/null 2>&1; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done
echo "PostgreSQL is ready!"

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
