---
name: flask-apps
description: Flask web application development, debugging, optimization, and deployment. Expert-level assistance for Flask projects including blueprints, SQLAlchemy, authentication, RESTful APIs, and production deployment.
license: MIT
metadata:
  author: agentgsd
  version: "1.0"
  compatibility: Flask>=2.0, Python>=3.8
  tags: flask,web,python,backend,api,rest
  frameworks: Flask,SQLAlchemy,Flask-Login,Flask-WTF,Flask-Migrate
---

# Flask Applications Skill

## Overview
Expert-level Flask web application development skill covering application architecture, database integration, authentication, RESTful API design, error handling, debugging, and production deployment.

## Capabilities

### 1. Application Architecture
- Application factory pattern
- Blueprint organization
- Configuration management
- Extension initialization
- Modular project structure

### 2. Database Integration
- SQLAlchemy ORM models
- Database migrations (Flask-Migrate/Alembic)
- Query optimization
- Relationship management
- Session handling

### 3. Authentication & Authorization
- Flask-Login integration
- User session management
- Password hashing (Werkzeug/bcrypt)
- Role-based access control
- OAuth integration

### 4. RESTful API Development
- API blueprint design
- Request/response handling
- Input validation
- Rate limiting
- API documentation (OpenAPI/Swagger)

### 5. Error Handling & Debugging
- Custom error pages
- Exception handling
- Logging configuration
- Debug toolbar
- Performance profiling

### 6. Production Deployment
- WSGI servers (Gunicorn/uWSGI)
- Reverse proxy (Nginx)
- Environment configuration
- Security hardening
- Monitoring setup

## Project Structure

### Recommended Layout
```
project/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models
│   ├── routes/              # Route blueprints
│   │   ├── __init__.py
│   │   ├── main.py          # Main blueprint
│   │   ├── auth.py          # Authentication routes
│   │   └── api.py           # API endpoints
│   ├── templates/           # Jinja2 templates
│   │   ├── base.html
│   │   ├── errors/
│   │   └── pages/
│   ├── static/              # Static assets
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── utils/               # Helper functions
│   │   ├── decorators.py
│   │   └── validators.py
│   └── forms/               # WTForms
│       └── forms.py
├── migrations/              # Database migrations
├── tests/                   # Test suite
│   ├── conftest.py
│   ├── test_models.py
│   └── test_routes.py
├── config.py                # Configuration classes
├── requirements.txt         # Dependencies
├── .env                     # Environment variables
└── wsgi.py                  # WSGI entry point
```

## Core Patterns

### Application Factory
```python
# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    """Application factory for creating Flask app instances."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    # Register error handlers
    register_error_handlers(app)

    return app

def register_error_handlers(app):
    """Register custom error handlers."""
    from app.utils.errors import register_error_handlers as register_errors
    register_errors(app)
```

### Blueprint Pattern
```python
# app/routes/main.py
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page route."""
    return render_template('pages/index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard (requires authentication)."""
    return render_template('pages/dashboard.html', user=current_user)

@main_bp.route('/profile/<int:user_id>')
def profile(user_id):
    """User profile page."""
    user = User.query.get_or_404(user_id)
    return render_template('pages/profile.html', user=user)
```

### SQLAlchemy Models
```python
# app/models.py
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    """User model with authentication support."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Serialize user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
        }

class Post(db.Model):
    """Blog post model."""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<Post {self.title}>'
```

### Authentication Setup
```python
# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__, template_folder='templates/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)
```

### RESTful API Pattern
```python
# app/routes/api.py
from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, Post

api_bp = Blueprint('api', __name__)

def api_response(data, status=200, message=None):
    """Standardized API response formatter."""
    response = {'data': data}
    if message:
        response['message'] = message
    return jsonify(response), status

def api_error(message, status=400):
    """Standardized API error formatter."""
    return jsonify({'error': message}), status

def require_json(f):
    """Decorator to require JSON content-type."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.is_json:
            abort(400, description='Content-Type must be application/json')
        return f(*args, **kwargs)
    return decorated

@api_bp.route('/users', methods=['GET'])
@login_required
def get_users():
    """Get all users (authenticated only)."""
    users = User.query.all()
    return api_response([u.to_dict() for u in users])

@api_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """Get single user by ID."""
    user = User.query.get_or_404(user_id)
    return api_response(user.to_dict())

@api_bp.route('/posts', methods=['GET'])
def get_posts():
    """Get all posts with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    posts = [post.to_dict() for post in pagination.items]
    return api_response({
        'posts': posts,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
    })

@api_bp.route('/posts', methods=['POST'])
@login_required
@require_json
def create_post():
    """Create new post (authenticated only)."""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('title') or not data.get('content'):
        return api_error('Title and content are required', 400)
    
    post = Post(
        title=data['title'],
        content=data['content'],
        user_id=current_user.id
    )
    db.session.add(post)
    db.session.commit()
    
    return api_response(post.to_dict(), status=201, message='Post created successfully')

@api_bp.route('/posts/<int:post_id>', methods=['PUT'])
@login_required
@require_json
def update_post(post_id):
    """Update existing post."""
    post = Post.query.get_or_404(post_id)
    
    # Check ownership
    if post.user_id != current_user.id:
        return api_error('Permission denied', 403)
    
    data = request.get_json()
    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    db.session.commit()
    
    return api_response(post.to_dict(), message='Post updated successfully')

@api_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    """Delete post."""
    post = Post.query.get_or_404(post_id)
    
    if post.user_id != current_user.id:
        return api_error('Permission denied', 403)
    
    db.session.delete(post)
    db.session.commit()
    
    return api_response({}, message='Post deleted successfully')
```

## Error Handling

### Custom Error Pages
```python
# app/utils/errors.py
from flask import render_template, jsonify, request
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    """Register error handlers for the Flask app."""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        if request.is_json:
            return jsonify({'error': 'Bad Request', 'message': str(error)}), 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(404)
    def not_found_error(error):
        if request.is_json:
            return jsonify({'error': 'Not Found', 'message': str(error)}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        if request.is_json:
            return jsonify({'error': 'Forbidden', 'message': str(error)}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        from app import db
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': 'Internal Server Error', 'message': str(error)}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle uncaught exceptions."""
        if isinstance(error, HTTPException):
            return error
        app.logger.error(f'Unhandled exception: {error}', exc_info=True)
        if request.is_json:
            return jsonify({'error': 'Internal Server Error'}), 500
        return render_template('errors/500.html'), 500
```

## Debugging Guide

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| 404 on all routes | Blueprint not registered | Call `app.register_blueprint()` in factory |
| SQLAlchemy error | App context missing | Use `with app.app_context()` or `@app.context_processor` |
| Session not persisting | Missing commit | Call `db.session.commit()` after changes |
| Circular imports | Import structure | Use local imports or restructure modules |
| Template not found | Wrong template_folder | Check blueprint `template_folder` config |
| Login not working | User loader missing | Implement `@login_manager.user_loader` |
| Migration fails | Model changed | Run `flask db migrate -m "description"` then `flask db upgrade` |

### Debug Commands
```bash
# Run development server with debug mode
flask run --debug

# Or with explicit debug flag
FLASK_DEBUG=1 flask run

# Initialize database
flask db init
flask db migrate -m "initial migration"
flask db upgrade

# Run tests
pytest tests/ -v

# Check routes
flask routes

# Open Flask shell
flask shell
```

## Security Checklist

- [ ] Enable CSRF protection (Flask-WTF)
- [ ] Use environment variables for secrets (python-dotenv)
- [ ] Implement rate limiting (flask-limiter)
- [ ] Sanitize user inputs (bleach for HTML)
- [ ] Use HTTPS in production
- [ ] Set secure cookie flags (SESSION_COOKIE_SECURE, SESSION_COOKIE_HTTPONLY)
- [ ] Implement proper session management
- [ ] Add security headers (flask-talisman)
- [ ] Hash passwords (werkzeug.security or bcrypt)
- [ ] Validate all user inputs
- [ ] Use parameterized queries (SQLAlchemy ORM)

## Testing

### Test Setup
```python
# tests/conftest.py
import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def authenticated_client(client, app):
    """Create authenticated test client."""
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    return client
```

## References
- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Flask Extensions: https://flask.palletsprojects.com/extensions/
- OWASP Flask Security: https://owasp.org/www-community/vulnerabilities/
