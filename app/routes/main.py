from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import current_user, login_required
from app import db
from app.models.user import User
from app.models.project import Project, Collaboration
from pygments import highlight
from pygments.lexers import get_lexer_by_name, get_all_lexers
from pygments.formatters import HtmlFormatter
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Get featured public projects for the landing page
    featured_projects = Project.query.filter_by(is_public=True).order_by(Project.updated_at.desc()).limit(6).all()
    return render_template('index.html', featured_projects=featured_projects)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    my_projects = Project.query.filter_by(owner_id=current_user.id).all()
    
    # Get projects the user is collaborating on
    collaborations = Collaboration.query.filter_by(user_id=current_user.id).all()
    collab_project_ids = [collab.project_id for collab in collaborations]
    collab_projects = Project.query.filter(Project.id.in_(collab_project_ids)).all()
    
    return render_template('dashboard.html', 
                           my_projects=my_projects, 
                           collab_projects=collab_projects)

@main_bp.route('/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        language = request.form.get('language', 'python')
        is_public = 'is_public' in request.form
        
        if not title:
            flash('Project title is required', 'danger')
            return render_template('project/new.html', languages=get_languages())
        
        project = Project(
            title=title,
            description=description,
            language=language,
            owner_id=current_user.id,
            is_public=is_public
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash('Project created successfully!', 'success')
        return redirect(url_for('main.view_project', project_id=project.id))
    
    return render_template('project/new.html', languages=get_languages())

@main_bp.route('/project/<int:project_id>')
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access to this project
    if not project.is_public and not current_user.is_authenticated:
        abort(403)
    
    if not project.is_public and project.owner_id != current_user.id:
        # Check if user is a collaborator
        collab = Collaboration.query.filter_by(
            user_id=current_user.id, 
            project_id=project.id
        ).first()
        
        if not collab:
            abort(403)
    
    # Get owner info
    owner = User.query.get(project.owner_id)
    
    # Get collaborators
    collaborators = []
    if current_user.is_authenticated and (project.owner_id == current_user.id):
        collaborations = Collaboration.query.filter_by(project_id=project.id).all()
        for collab in collaborations:
            user = User.query.get(collab.user_id)
            collaborators.append({
                'username': user.username,
                'permission': collab.permission,
                'user_id': user.id
            })
    
    # Format code with syntax highlighting
    lexer = get_lexer_by_name(project.language, stripall=True)
    formatter = HtmlFormatter(linenos=True, cssclass="source")
    highlighted_code = highlight(project.content, lexer, formatter)
    css = formatter.get_style_defs('.source')
    
    return render_template('project/view.html', 
                          project=project,
                          owner=owner,
                          collaborators=collaborators,
                          highlighted_code=highlighted_code,
                          css=css)

@main_bp.route('/project/<int:project_id>/edit')
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check if user has permission to edit
    if project.owner_id != current_user.id:
        collab = Collaboration.query.filter_by(
            user_id=current_user.id, 
            project_id=project.id,
        ).first()
        
        if not collab or collab.permission not in ['write', 'admin']:
            abort(403)
    
    return render_template('project/edit.html', 
                          project=project,
                          languages=get_languages())

@main_bp.route('/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Only owner can delete project
    if project.owner_id != current_user.id:
        abort(403)
    
    db.session.delete(project)
    db.session.commit()
    
    flash('Project deleted successfully', 'success')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/project/<int:project_id>/add_collaborator', methods=['POST'])
@login_required
def add_collaborator(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Only owner can add collaborators
    if project.owner_id != current_user.id:
        abort(403)
    
    username = request.form.get('username')
    permission = request.form.get('permission', 'read')
    
    if not username:
        flash('Username is required', 'danger')
        return redirect(url_for('main.view_project', project_id=project.id))
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        flash(f'User {username} not found', 'danger')
        return redirect(url_for('main.view_project', project_id=project.id))
    
    # Check if user is already a collaborator
    existing_collab = Collaboration.query.filter_by(
        user_id=user.id,
        project_id=project.id
    ).first()
    
    if existing_collab:
        flash(f'{username} is already a collaborator', 'warning')
        return redirect(url_for('main.view_project', project_id=project.id))
    
    # Add collaborator
    collab = Collaboration(
        user_id=user.id,
        project_id=project.id,
        permission=permission
    )
    
    db.session.add(collab)
    db.session.commit()
    
    flash(f'{username} added as collaborator with {permission} permission', 'success')
    return redirect(url_for('main.view_project', project_id=project.id))

@main_bp.route('/project/<int:project_id>/remove_collaborator/<int:user_id>', methods=['POST'])
@login_required
def remove_collaborator(project_id, user_id):
    project = Project.query.get_or_404(project_id)
    
    # Only owner can remove collaborators
    if project.owner_id != current_user.id:
        abort(403)
    
    collab = Collaboration.query.filter_by(
        user_id=user_id,
        project_id=project.id
    ).first_or_404()
    
    user = User.query.get(user_id)
    
    db.session.delete(collab)
    db.session.commit()
    
    flash(f'{user.username} removed from collaborators', 'success')
    return redirect(url_for('main.view_project', project_id=project.id))

@main_bp.route('/explore')
def explore():
    # Get public projects
    public_projects = Project.query.filter_by(is_public=True).order_by(Project.updated_at.desc()).all()
    return render_template('explore.html', projects=public_projects)

def get_languages():
    languages = []
    for lang in get_all_lexers():
        try:
            # Check if lang has at least 2 elements and the second element is not empty
            if len(lang) >= 2 and len(lang[1]) > 0:
                languages.append((lang[1][0], lang[0]))
        except (IndexError, TypeError):
            # Skip lexers with invalid data structure
            continue
    return sorted(languages, key=lambda x: x[1]) 