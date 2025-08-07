from flask_socketio import join_room, leave_room, emit
from flask_login import current_user
from app import socketio, db
from app.models.project import Project

@socketio.on('join')
def on_join(data):
    """When a user joins a project editing session"""
    if not current_user.is_authenticated:
        return
    
    project_id = data.get('project_id')
    if not project_id:
        return
    
    # Create a room name based on the project
    room = f"project_{project_id}"
    join_room(room)
    
    # Notify others that user has joined
    emit('user_joined', {
        'username': current_user.username,
        'user_id': current_user.id
    }, room=room, include_self=False)

@socketio.on('leave')
def on_leave(data):
    """When a user leaves a project editing session"""
    if not current_user.is_authenticated:
        return
    
    project_id = data.get('project_id')
    if not project_id:
        return
    
    room = f"project_{project_id}"
    leave_room(room)
    
    # Notify others that user has left
    emit('user_left', {
        'username': current_user.username,
        'user_id': current_user.id
    }, room=room, include_self=False)

@socketio.on('code_update')
def on_code_update(data):
    """When a user updates code in the editor"""
    if not current_user.is_authenticated:
        return
    
    project_id = data.get('project_id')
    content = data.get('content')
    
    if not project_id or content is None:
        return
    
    # Check user has permission to edit
    project = Project.query.get(project_id)
    
    if not project:
        return
        
    # Only allow owner or collaborators with write/admin permissions to update code
    can_edit = False
    
    if project.owner_id == current_user.id:
        can_edit = True
    else:
        for collab in project.collaborations:
            if collab.user_id == current_user.id and collab.permission in ['write', 'admin']:
                can_edit = True
                break
    
    if not can_edit:
        return
        
    # Update project content
    project.content = content
    db.session.commit()
    
    # Broadcast the update to all users in the room except sender
    room = f"project_{project_id}"
    emit('code_updated', {
        'content': content,
        'updated_by': current_user.username
    }, room=room, include_self=False)

@socketio.on('cursor_position')
def on_cursor_position(data):
    """When a user moves their cursor, broadcast to others"""
    if not current_user.is_authenticated:
        return
    
    project_id = data.get('project_id')
    position = data.get('position')
    
    if not project_id or position is None:
        return
    
    room = f"project_{project_id}"
    emit('cursor_moved', {
        'user_id': current_user.id,
        'username': current_user.username,
        'position': position
    }, room=room, include_self=False)

# Add a simple connection test event
@socketio.on('connect')
def test_connect():
    emit('my_response', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected') 