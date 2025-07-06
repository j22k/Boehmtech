from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from src.models.user import User, db
from src.models.task import Task, TaskUpdate
from datetime import datetime
import os
import uuid

task_bp = Blueprint('task', __name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save uploaded file and return the path"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.static_folder, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Return relative path for database storage
        return f"uploads/{unique_filename}"
    return None

@task_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get tasks based on user role and filters"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        status = request.args.get('status')
        assigned_to = request.args.get('assigned_to')
        created_by = request.args.get('created_by')
        
        # Build query based on user role
        if user.role == 'superadmin':
            # Superadmin can see all tasks
            query = Task.query
        elif user.role == 'admin':
            # Admin can see all tasks (in a real app, this might be team-specific)
            query = Task.query
        else:
            # Regular users can only see their assigned tasks
            query = Task.query.filter_by(assignee_uid=current_user_id)
        
        # Apply filters
        if status:
            query = query.filter_by(status=status)
        if assigned_to and user.has_role('admin'):
            query = query.filter_by(assignee_uid=assigned_to)
        if created_by and user.has_role('admin'):
            query = query.filter_by(created_by_uid=created_by)
        
        tasks = query.order_by(Task.due_date.asc()).all()
        
        return jsonify({
            'tasks': [task.to_dict() for task in tasks]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@task_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only admins and superadmins can create tasks
        if not user.has_role('admin'):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        # Parse due date if provided
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid due date format'}), 400
        
        # Validate assignee if provided
        assignee_uid = data.get('assignee_uid')
        if assignee_uid:
            assignee = User.query.get(assignee_uid)
            if not assignee:
                return jsonify({'error': 'Assignee not found'}), 400
        
        # Create task
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'medium'),
            due_date=due_date,
            assignee_uid=assignee_uid,
            created_by_uid=current_user_id
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'message': 'Task created successfully',
            'task': task.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get a specific task with updates"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        task = Task.query.get_or_404(task_id)
        
        # Check permissions
        if not user.has_role('admin') and task.assignee_uid != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'task': task.to_dict(include_updates=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update a task"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        task = Task.query.get_or_404(task_id)
        
        # Check permissions - admins can edit any task, users can only update status of their tasks
        if not user.has_role('admin') and task.assignee_uid != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Users can only update status and add comments
        if not user.has_role('admin'):
            if 'status' in data:
                task.update_status(data['status'])
        else:
            # Admins can update all fields
            if 'title' in data:
                task.title = data['title']
            if 'description' in data:
                task.description = data['description']
            if 'status' in data:
                task.update_status(data['status'])
            if 'priority' in data:
                task.priority = data['priority']
            if 'assignee_uid' in data:
                assignee = User.query.get(data['assignee_uid'])
                if assignee:
                    task.assignee_uid = data['assignee_uid']
            if 'due_date' in data:
                if data['due_date']:
                    try:
                        task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                    except ValueError:
                        return jsonify({'error': 'Invalid due date format'}), 400
                else:
                    task.due_date = None
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only admins can delete tasks
        if not user.has_role('admin'):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        task = Task.query.get_or_404(task_id)
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'Task deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@task_bp.route('/tasks/<int:task_id>/updates', methods=['POST'])
@jwt_required()
def add_task_update():
    """Add an update to a task"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        task_id = request.view_args['task_id']
        task = Task.query.get_or_404(task_id)
        
        # Check permissions
        if not user.has_role('admin') and task.assignee_uid != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Handle file upload
        screenshot_path = None
        if 'screenshot' in request.files:
            file = request.files['screenshot']
            screenshot_path = save_uploaded_file(file)
        
        # Get form data
        comment = request.form.get('comment')
        url = request.form.get('url')
        
        if not comment and not url and not screenshot_path:
            return jsonify({'error': 'At least one of comment, url, or screenshot is required'}), 400
        
        # Create task update
        update = TaskUpdate(
            comment=comment,
            url=url,
            screenshot_path=screenshot_path,
            task_id=task_id,
            updated_by_uid=current_user_id
        )
        
        db.session.add(update)
        
        # Update task timestamp
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Task update added successfully',
            'update': update.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@task_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        stats = {}
        
        if user.role == 'superadmin':
            # Global statistics
            stats = {
                'total_tasks': Task.query.count(),
                'pending_tasks': Task.query.filter_by(status='pending').count(),
                'in_progress_tasks': Task.query.filter_by(status='in_progress').count(),
                'completed_tasks': Task.query.filter_by(status='completed').count(),
                'overdue_tasks': len(Task.get_overdue_tasks()),
                'total_users': User.query.count(),
                'active_users': User.query.filter_by(is_active=True).count()
            }
        elif user.role == 'admin':
            # Team statistics (simplified - in real app might be team-specific)
            stats = {
                'total_tasks': Task.query.count(),
                'pending_tasks': Task.query.filter_by(status='pending').count(),
                'in_progress_tasks': Task.query.filter_by(status='in_progress').count(),
                'completed_tasks': Task.query.filter_by(status='completed').count(),
                'overdue_tasks': len(Task.get_overdue_tasks())
            }
        else:
            # User-specific statistics
            user_tasks = Task.query.filter_by(assignee_uid=current_user_id)
            stats = {
                'my_tasks': user_tasks.count(),
                'pending_tasks': user_tasks.filter_by(status='pending').count(),
                'in_progress_tasks': user_tasks.filter_by(status='in_progress').count(),
                'completed_tasks': user_tasks.filter_by(status='completed').count(),
                'overdue_tasks': len([t for t in user_tasks.all() if t.is_overdue()])
            }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

