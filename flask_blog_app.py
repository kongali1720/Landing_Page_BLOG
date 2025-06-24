from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Database Models
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_submitted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Forms
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=100)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=10)])
    author = StringField('Author', validators=[DataRequired(), Length(max=50)])
    category = SelectField('Category', choices=[
        ('tech', 'Technology'),
        ('business', 'Business'),
        ('lifestyle', 'Lifestyle'),
        ('education', 'Education')
    ], validators=[DataRequired()])
    submit = SubmitField('Publish Post')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Send Message')

# Routes
@app.route('/')
def home():
    """Home page displaying recent blog posts"""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(
        page=page, per_page=5, error_out=False
    )
    return render_template('home.html', posts=posts)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    """Display individual blog post"""
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    """Create new blog post"""
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author=form.author.data,
            category=form.category.data
        )
        db.session.add(post)
        db.session.commit()
        flash('Your post has been published!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form page"""
    form = ContactForm()
    if form.validate_on_submit():
        contact_msg = Contact(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )
        db.session.add(contact_msg)
        db.session.commit()
        flash('Your message has been sent!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

@app.route('/api/posts')
def api_posts():
    """API endpoint to get all posts as JSON"""
    posts = Post.query.all()
    return jsonify([{
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author,
        'category': post.category,
        'date_posted': post.date_posted.isoformat()
    } for post in posts])

@app.route('/api/posts/<int:post_id>')
def api_post_detail(post_id):
    """API endpoint to get specific post as JSON"""
    post = Post.query.get_or_404(post_id)
    return jsonify({
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author,
        'category': post.category,
        'date_posted': post.date_posted.isoformat()
    })

@app.route('/api/posts', methods=['POST'])
def api_create_post():
    """API endpoint to create new post via JSON"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('title', 'content', 'author', 'category')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    post = Post(
        title=data['title'],
        content=data['content'],
        author=data['author'],
        category=data['category']
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify({
        'id': post.id,
        'message': 'Post created successfully'
    }), 201

@app.route('/dashboard')
def dashboard():
    """Admin dashboard showing statistics"""
    total_posts = Post.query.count()
    total_contacts = Contact.query.count()
    recent_posts = Post.query.order_by(Post.date_posted.desc()).limit(5).all()
    
    # Category statistics
    categories = db.session.query(Post.category, db.func.count(Post.id)).group_by(Post.category).all()
    
    stats = {
        'total_posts': total_posts,
        'total_contacts': total_contacts,
        'recent_posts': recent_posts,
        'categories': dict(categories)
    }
    
    return render_template('dashboard.html', stats=stats)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Database initialization
def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()
        
        # Add sample data if tables are empty
        if Post.query.count() == 0:
            sample_posts = [
                Post(
                    title="Getting Started with Python Flask",
                    content="Flask is a lightweight web framework for Python that makes it easy to build web applications...",
                    author="John Doe",
                    category="tech"
                ),
                Post(
                    title="Building RESTful APIs",
                    content="REST APIs are essential for modern web development. Here's how to build them with Flask...",
                    author="Jane Smith",
                    category="tech"
                ),
                Post(
                    title="Database Design Best Practices",
                    content="When designing databases, there are several key principles to follow...",
                    author="Bob Johnson",
                    category="education"
                )
            ]
            
            for post in sample_posts:
                db.session.add(post)
            
            db.session.commit()
            print("Sample data added to database")

# CLI Commands
@app.cli.command()
def init_db():
    """Initialize the database with sample data"""
    create_tables()
    print("Database initialized successfully!")

@app.cli.command()
def reset_db():
    """Reset the database (WARNING: This will delete all data)"""
    db.drop_all()
    create_tables()
    print("Database reset successfully!")

# Application factory pattern (optional)
def create_app(config_name='default'):
    """Application factory for different configurations"""
    app = Flask(__name__)
    
    if config_name == 'testing':
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    elif config_name == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
    
    return app

if __name__ == '__main__':
    # Create tables on first run
    create_tables()
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)

# Usage Instructions:
"""
1. Install required packages:
   pip install flask flask-sqlalchemy flask-wtf wtforms

2. Run the application:
   python app.py

3. Access the application:
   - Home page: http://localhost:5000/
   - Create post: http://localhost:5000/create_post
   - Contact: http://localhost:5000/contact
   - Dashboard: http://localhost:5000/dashboard
   - API endpoints: http://localhost:5000/api/posts

4. Initialize database:
   flask init-db

5. Reset database:
   flask reset-db
"""

