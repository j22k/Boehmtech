# Boehm Tech TaskMaster

A full-stack task management web application built with Flask and SQLite, featuring a futuristic black theme with neon accents. This application supports three user roles (User, Admin, Superadmin) and provides comprehensive task management capabilities.

## Features

### 🎨 Design
- **Futuristic Black Theme**: Sleek dark interface with neon teal, purple, and blue accents
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Modern UI/UX**: Smooth animations, hover effects, and intuitive navigation
- **Professional Branding**: Customized for Boehm Tech with consistent styling

### 👥 User Management (Admin-Only)
- **Admin-Only User Creation**: Only admins and superadmins can create new users
- **No Public Registration**: Public signup has been removed for security
- **Three Role System**: User, Admin, and Superadmin with different permissions
- **Secure Authentication**: JWT-based authentication with password hashing
- **Profile Management**: Users can update their display name and password

### 📋 Task Management
- **Task Creation**: Admins can create tasks with title, description, priority, and due dates
- **Task Assignment**: Assign tasks to specific users
- **Status Tracking**: Track task progress (Pending, In Progress, Completed, Cancelled)
- **Priority Levels**: Four priority levels (Low, Medium, High, Urgent)
- **Task Updates**: Add comments, URLs, and screenshot attachments to tasks
- **File Uploads**: Support for screenshot attachments with secure file handling

### 📊 Dashboard & Analytics
- **Personal Dashboard**: Users see their assigned tasks and statistics
- **Admin Dashboard**: Team overview with task metrics and progress tracking
- **Superadmin Dashboard**: Global system metrics and user management
- **Real-time Statistics**: Live updates of task counts and completion rates

### 🔐 Security Features
- **Role-based Access Control**: Granular permissions based on user roles
- **Password Hashing**: Secure password storage using Werkzeug
- **JWT Tokens**: Secure API authentication with token expiration
- **Input Validation**: Server-side validation for all user inputs
- **CORS Support**: Configured for secure cross-origin requests

## Technology Stack

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Lightweight database for development
- **Flask-JWT-Extended**: JWT authentication
- **Flask-CORS**: Cross-origin resource sharing
- **Werkzeug**: Password hashing and security utilities
- **bcrypt**: Additional password hashing support

### Frontend
- **HTML5**: Modern semantic markup
- **CSS3**: Advanced styling with custom properties and animations
- **JavaScript (ES6+)**: Modern JavaScript with async/await
- **Font Awesome**: Icon library
- **Google Fonts**: Inter and Roboto Mono typography

## Installation & Setup

### Prerequisites
- Python 3.11 or higher
- pip (Python package installer)
- Git (for version control)

### Quick Start

1. **Clone or extract the project**:
   ```bash
   cd boehm-tech-taskmaster
   ```

2. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python src/main.py
   ```

5. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

### Default Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Superadmin

## Project Structure

```
boehm-tech-taskmaster/
├── venv/                   # Virtual environment
├── src/
│   ├── models/            # Database models
│   │   ├── user.py        # User model with authentication
│   │   └── task.py        # Task and TaskUpdate models
│   ├── routes/            # API endpoints
│   │   ├── auth.py        # Authentication routes
│   │   ├── user.py        # User management routes
│   │   └── task.py        # Task management routes
│   ├── static/            # Frontend files
│   │   ├── index.html     # Main HTML template
│   │   ├── styles.css     # CSS with black theme
│   │   ├── script.js      # JavaScript functionality
│   │   └── uploads/       # File upload directory
│   ├── database/          # Database files
│   │   └── app.db         # SQLite database
│   └── main.py            # Flask application entry point
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/change-password` - Change password
- `PUT /api/auth/update-profile` - Update user profile

**Note**: Public registration endpoint has been removed. Only admins can create users through the user management interface.

### User Management (Admin/Superadmin only)
- `GET /api/users` - List all users
- `POST /api/users` - Create new user
- `GET /api/users/{id}` - Get specific user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Deactivate user
- `GET /api/users/search` - Search users

### Task Management
- `GET /api/tasks` - List tasks (filtered by role)
- `POST /api/tasks` - Create new task (Admin/Superadmin only)
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task (Admin/Superadmin only)
- `POST /api/tasks/{id}/updates` - Add task update with file upload

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

## User Roles & Permissions

### User
- View assigned tasks
- Update task status
- Add comments and attachments to assigned tasks
- Update own profile and password

### Admin
- All User permissions
- Create, edit, and delete tasks
- Assign tasks to users
- View team statistics
- Create and manage regular users
- View all tasks and user profiles

### Superadmin
- All Admin permissions
- Create and manage admin users
- Access global system statistics
- Manage all users and roles
- Full system administration

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Hashed password
- `display_name`: User's display name
- `role`: User role (user/admin/superadmin)
- `created_at`: Account creation timestamp
- `is_active`: Account status

### Tasks Table
- `id`: Primary key
- `title`: Task title
- `description`: Task description
- `status`: Task status (pending/in_progress/completed/cancelled)
- `priority`: Task priority (low/medium/high/urgent)
- `due_date`: Task due date
- `created_at`: Task creation timestamp
- `updated_at`: Last update timestamp
- `assignee_uid`: Foreign key to Users
- `created_by_uid`: Foreign key to Users (creator)

### Task Updates Table
- `id`: Primary key
- `comment`: Update comment
- `url`: Related URL
- `screenshot_path`: Path to uploaded screenshot
- `created_at`: Update timestamp
- `task_id`: Foreign key to Tasks
- `updated_by_uid`: Foreign key to Users

## Configuration

### Environment Variables
The application uses the following configuration:
- `SECRET_KEY`: Flask secret key for sessions
- `JWT_SECRET_KEY`: JWT token signing key
- `JWT_ACCESS_TOKEN_EXPIRES`: Token expiration time (24 hours)
- `JWT_REFRESH_TOKEN_EXPIRES`: Refresh token expiration (30 days)

### Database Configuration
- **Development**: SQLite database in `src/database/app.db`
- **Production**: Can be configured for PostgreSQL or MySQL

## Deployment

### Development
The application runs in debug mode by default for development:
```bash
python src/main.py
```

### Production
For production deployment:

1. **Set environment variables**:
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-secret-key
   export JWT_SECRET_KEY=your-jwt-secret
   ```

2. **Use a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
   ```

3. **Configure reverse proxy** (nginx recommended)

4. **Use production database** (PostgreSQL/MySQL)

## Security Considerations

- Change default admin credentials immediately
- Use strong secret keys in production
- Configure HTTPS in production
- Implement rate limiting for API endpoints
- Regular security updates for dependencies
- Backup database regularly

## Troubleshooting

### Common Issues

1. **Database errors**: Delete `src/database/app.db` to reset the database
2. **Permission errors**: Ensure proper file permissions for uploads directory
3. **Port conflicts**: Change port in `main.py` if 5000 is occupied
4. **JWT errors**: Check token expiration and secret key configuration

### Logs
- Flask development server logs appear in the console
- For production, configure proper logging to files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is proprietary software developed for Boehm Tech.

## Support

For technical support or questions, please contact the development team.

---

**Boehm Tech TaskMaster** - Empowering teams with futuristic task management.

