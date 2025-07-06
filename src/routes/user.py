from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (admin/superadmin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only admins and superadmins can view all users
        if not user.has_role('admin'):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Get query parameters
        role = request.args.get('role')
        is_active = request.args.get('is_active')
        
        # Build query
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        
        if is_active is not None:
            active_filter = is_active.lower() == 'true'
            query = query.filter_by(is_active=active_filter)
        
        users = query.order_by(User.created_at.desc()).all()
        
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """Create a new user (admin/superadmin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only admins and superadmins can create users
        if not current_user.has_role('admin'):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'display_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Role validation - only superadmins can create other admins/superadmins
        requested_role = data.get('role', 'user')
        if requested_role in ['admin', 'superadmin'] and current_user.role != 'superadmin':
            return jsonify({'error': 'Only superadmins can create admin users'}), 403
        
        # Create new user
        user = User.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            display_name=data['display_name'],
            role=requested_role
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get a specific user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Users can view their own profile, admins can view any profile
        if user_id != current_user_id and not current_user.has_role('admin'):
            return jsonify({'error': 'Access denied'}), 403
        
        user = User.query.get_or_404(user_id)
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update a user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        user = User.query.get_or_404(user_id)
        
        # Users can update their own profile, admins can update any profile
        if user_id != current_user_id and not current_user.has_role('admin'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update allowed fields
        if 'display_name' in data:
            user.display_name = data['display_name']
        
        if 'email' in data:
            # Check if email is already taken by another user
            existing_user = User.query.filter(
                User.email == data['email'],
                User.id != user.id
            ).first()
            if existing_user:
                return jsonify({'error': 'Email already exists'}), 400
            user.email = data['email']
        
        # Only admins can update role and active status
        if current_user.has_role('admin'):
            if 'role' in data:
                # Only superadmins can change roles to admin/superadmin
                if data['role'] in ['admin', 'superadmin'] and current_user.role != 'superadmin':
                    return jsonify({'error': 'Only superadmins can assign admin roles'}), 403
                user.role = data['role']
            
            if 'is_active' in data:
                user.is_active = data['is_active']
        
        # Password update (if provided)
        if 'password' in data:
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete a user (superadmin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only superadmins can delete users
        if current_user.role != 'superadmin':
            return jsonify({'error': 'Only superadmins can delete users'}), 403
        
        # Prevent self-deletion
        if user_id == current_user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        user = User.query.get_or_404(user_id)
        
        # Instead of hard delete, deactivate the user to preserve data integrity
        user.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'User deactivated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/search', methods=['GET'])
@jwt_required()
def search_users():
    """Search users by username or display name (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only admins can search users
        if not current_user.has_role('admin'):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'users': []}), 200
        
        # Search by username or display name
        users = User.query.filter(
            (User.username.contains(query)) |
            (User.display_name.contains(query))
        ).filter_by(is_active=True).limit(10).all()
        
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

