import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify


from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

# Import models
from src.models.user import db
from src.models.task import Task, TaskUpdate

# Import routes
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.task import task_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = 'boehm-tech-secret-key-2024'
app.config['JWT_SECRET_KEY'] = 'boehm-tech-jwt-secret-2024'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Enable CORS for all routes
CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])

# Initialize JWT
jwt = JWTManager(app)

# JWT Error Handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'error': 'Invalid token'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'error': 'Authorization token is required'}), 401

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(task_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create upload directory for screenshots
upload_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(upload_dir, exist_ok=True)

with app.app_context():
    db.create_all()
    
    # Create default superadmin user if it doesn't exist
    from src.models.user import User
    superadmin = User.query.filter_by(username='admin').first()
    if not superadmin:
        superadmin = User.create_user(
            username='admin',
            email='admin@boehmtech.com',
            password='admin123',
            display_name='Boehm Tech Administrator',
            role='superadmin'
        )
        db.session.add(superadmin)
        db.session.commit()
        print("Default superadmin created: username='admin', password='admin123'")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.errorhandler(404)
def not_found(error):
    return {"error": "Resource not found"}, 404

@app.errorhandler(500)
def internal_error(error):
    return {"error": "Internal server error"}, 500

if __name__ == '__main__':
    # For Render deployment, use the PORT environment variable if available
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

