#!/usr/bin/env python3
import os
from pathlib import Path

def create_flask_templates():
    """Auto-generate all required Flask templates"""
    
    # Base directory (current directory)
    base_dir = Path(".")
    templates_dir = base_dir / "templates"
    static_dir = base_dir / "static"
    
    # Create directories
    templates_dir.mkdir(exist_ok=True)
    (static_dir / "css").mkdir(parents=True, exist_ok=True)
    (static_dir / "js").mkdir(parents=True, exist_ok=True)
    
    print("📁 Creating Flask template directories...")
    
    # Template files content
    templates = {
        "base.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Flask Blog{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="icon" type="image/x-icon" href="data:image/x-icon;base64,">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('home') }}">🚀 Flask Blog</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{{ url_for('home') }}">Home</a>
                <a class="nav-link" href="{{ url_for('create_post') }}">Create Post</a>
                <a class="nav-link" href="{{ url_for('contact') }}">Contact</a>
                <a class="nav-link" href="{{ url_for('dashboard') }}">Dashboard</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-success alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <footer class="bg-dark text-white text-center py-3 mt-5">
        <div class="container">
            <p>&copy; 2025 Flask Blog. Made with ❤️ and Python</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>""",

        "home.html": """{% extends "base.html" %}

{% block title %}Home - Flask Blog{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <h1 class="mb-4">📝 Latest Blog Posts</h1>
        
        {% if posts.items %}
            {% for post in posts.items %}
                <div class="card mb-4 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="badge bg-primary">{{ post.category.title() }}</span>
                            <small class="text-muted">{{ post.date_posted.strftime('%B %d, %Y') }}</small>
                        </div>
                        <h5 class="card-title">{{ post.title }}</h5>
                        <p class="card-text text-muted">{{ post.content[:200] }}{% if post.content|length > 200 %}...{% endif %}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                ✍️ By {{ post.author }}
                            </small>
                            <a href="{{ url_for('post_detail', post_id=post.id) }}" class="btn btn-outline-primary btn-sm">Read More →</a>
                        </div>
                    </div>
                </div>
            {% endfor %}
            
            <!-- Pagination -->
            {% if posts.pages > 1 %}
                <nav aria-label="Posts pagination">
                    <ul class="pagination justify-content-center">
                        {% if posts.has_prev %}
                            <li class="page-item">
                                <a class="page-link" href="{{ url_for('home', page=posts.prev_num) }}">← Previous</a>
                            </li>
                        {% endif %}
                        
                        {% for page_num in posts.iter_pages() %}
                            {% if page_num %}
                                {% if page_num != posts.page %}
                                    <li class="page-item">
                                        <a class="page-link" href="{{ url_for('home', page=page_num) }}">{{ page_num }}</a>
                                    </li>
                                {% else %}
                                    <li class="page-item active">
                                        <span class="page-link">{{ page_num }}</span>
                                    </li>
                                {% endif %}
                            {% endif %}
                        {% endfor %}
                        
                        {% if posts.has_next %}
                            <li class="page-item">
                                <a class="page-link" href="{{ url_for('home', page=posts.next_num) }}">Next →</a>
                            </li>
                        {% endif %}
                    </ul>
                </nav>
            {% endif %}
        {% else %}
            <div class="text-center py-5">
                <h3>📄 No posts yet!</h3>
                <p class="text-muted">Be the first to share something awesome.</p>
                <a href="{{ url_for('create_post') }}" class="btn btn-primary">✨ Create First Post</a>
            </div>
        {% endif %}
    </div>
    
    <div class="col-md-4">
        <div class="card shadow-sm">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">🚀 Quick Actions</h5>
            </div>
            <div class="card-body">
                <a href="{{ url_for('create_post') }}" class="btn btn-success mb-2 w-100">📝 Create New Post</a>
                <a href="{{ url_for('contact') }}" class="btn btn-info mb-2 w-100">📧 Contact Us</a>
                <a href="{{ url_for('dashboard') }}" class="btn btn-warning w-100">📊 Dashboard</a>
            </div>
        </div>
        
        <div class="card shadow-sm mt-4">
            <div class="card-header">
                <h6>💡 Tips</h6>
            </div>
            <div class="card-body">
                <ul class="list-unstyled">
                    <li>• Write engaging titles</li>
                    <li>• Use proper categories</li>
                    <li>• Share your knowledge</li>
                </ul>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",

        "create_post.html": """{% extends "base.html" %}

{% block title %}Create Post - Flask Blog{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card shadow">
            <div class="card-header bg-success text-white">
                <h2 class="mb-0">✨ Create New Post</h2>
            </div>
            <div class="card-body">
                <form method="POST">
                    {{ form.hidden_tag() }}
                    
                    <div class="mb-3">
                        {{ form.title.label(class="form-label fw-bold") }}
                        {{ form.title(class="form-control", placeholder="Enter an engaging title...") }}
                        {% if form.title.errors %}
                            <div class="text-danger mt-1">
                                {% for error in form.title.errors %}
                                    <small>{{ error }}</small>
                                {% endfor %}
                            </div>
                        {% endif %}
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                {{ form.author.label(class="form-label fw-bold") }}
                                {{ form.author(class="form-control", placeholder="Your name") }}
                                {% if form.author.errors %}
                                    <div class="text-danger mt-1">
                                        {% for error in form.author.errors %}
                                            <small>{{ error }}</small>
                                        {% endfor %}
                                    </div>
                                {% endif %}
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                {{ form.category.label(class="form-label fw-bold") }}
                                {{ form.category(class="form-control") }}
                                {% if form.category.errors %}
                                    <div class="text-danger mt-1">
                                        {% for error in form.category.errors %}
                                            <small>{{ error }}</small>
                                        {% endfor %}
                                    </div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        {{ form.content.label(class="form-label fw-bold") }}
                        {{ form.content(class="form-control", rows="12", placeholder="Write your amazing content here...") }}
                        {% if form.content.errors %}
                            <div class="text-danger mt-1">
                                {% for error in form.content.errors %}
                                    <small>{{ error }}</small>
                                {% endfor %}
                            </div>
                        {% endif %}
                        <div class="form-text">Minimum 10 characters required.</div>
                    </div>
                    
                    <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                        <a href="{{ url_for('home') }}" class="btn btn-secondary me-md-2">Cancel</a>
                        {{ form.submit(class="btn btn-success") }}
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",

        "contact.html": """{% extends "base.html" %}

{% block title %}Contact - Flask Blog{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card shadow">
            <div class="card-header bg-info text-white">
                <h2 class="mb-0">📧 Contact Us</h2>
            </div>
            <div class="card-body">
                <p class="lead">We'd love to hear from you! Send us a message and we'll get back to you soon.</p>
                
                <form method="POST">
                    {{ form.hidden_tag() }}
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                {{ form.name.label(class="form-label fw-bold") }}
                                {{ form.name(class="form-control", placeholder="Your full name") }}
                                {% if form.name.errors %}
                                    <div class="text-danger mt-1">
                                        {% for error in form.name.errors %}
                                            <small>{{ error }}</small>
                                        {% endfor %}
                                    </div>
                                {% endif %}
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                {{ form.email.label(class="form-label fw-bold") }}
                                {{ form.email(class="form-control", placeholder="your.email@example.com") }}
                                {% if form.email.errors %}
                                    <div class="text-danger mt-1">
                                        {% for error in form.email.errors %}
                                            <small>{{ error }}</small>
                                        {% endfor %}
                                    </div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        {{ form.message.label(class="form-label fw-bold") }}
                        {{ form.message(class="form-control", rows="6", placeholder="Write your message here...") }}
                        {% if form.message.errors %}
                            <div class="text-danger mt-1">
                                {% for error in form.message.errors %}
                                    <small>{{ error }}</small>
                                {% endfor %}
                            </div>
                        {% endif %}
                        <div class="form-text">Minimum 10 characters required.</div>
                    </div>
                    
                    <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                        <a href="{{ url_for('home') }}" class="btn btn-secondary me-md-2">Back to Home</a>
                        {{ form.submit(class="btn btn-info") }}
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",

        "post_detail.html": """{% extends "base.html" %}

{% block title %}{{ post.title }} - Flask Blog{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8 mx-auto">
        <article class="card shadow">
            <div class="card-header">
                <div class="d-flex justify-content-between align-items-center">
                    <span class="badge bg-primary fs-6">{{ post.category.title() }}</span>
                    <small class="text-muted">{{ post.date_posted.strftime('%B %d, %Y at %I:%M %p') }}</small>
                </div>
            </div>
            <div class="card-body">
                <h1 class="card-title mb-3">{{ post.title }}</h1>
                <div class="mb-4">
                    <small class="text-muted">
                        ✍️ Written by <strong>{{ post.author }}</strong>
                    </small>
                </div>
                <div class="post-content">
                    {{ post.content | replace('\\n', '<br>') | safe }}
                </div>
            </div>
            <div class="card-footer bg-light">
                <div class="row align-items-center">
                    <div class="col">
                        <small class="text-muted">
                            📅 Published on {{ post.date_posted.strftime('%B %d, %Y') }}
                        </small>
                    </div>
                    <div class="col-auto">
                        <a href="{{ url_for('home') }}" class="btn btn-outline-primary btn-sm">← Back to Home</a>
                    </div>
                </div>
            </div>
        </article>
        
        <div class="text-center mt-4">
            <a href="{{ url_for('create_post') }}" class="btn btn-success">✨ Write Your Own Post</a>
        </div>
    </div>
</div>
{% endblock %}""",

        "dashboard.html": """{% extends "base.html" %}

{% block title %}Dashboard - Flask Blog{% endblock %}

{% block content %}
<h1 class="mb-4">📊 Dashboard</h1>

<div class="row mb-4">
    <div class="col-md-4">
        <div class="card text-center shadow">
            <div class="card-body">
                <h5 class="card-title text-primary">📝 Total Posts</h5>
                <h2 class="display-4 text-primary">{{ stats.total_posts }}</h2>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card text-center shadow">
            <div class="card-body">
                <h5 class="card-title text-success">📧 Total Contacts</h5>
                <h2 class="display-4 text-success">{{ stats.total_contacts }}</h2>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card shadow">
            <div class="card-header bg-warning text-dark">
                <h5 class="mb-0">📂 Categories</h5>
            </div>
            <div class="card-body">
                {% if stats.categories %}
                    {% for category, count in stats.categories.items() %}
                        <span class="badge bg-secondary me-2 mb-1">{{ category.title() }}: {{ count }}</span>
                    {% endfor %}
                {% else %}
                    <p class="text-muted mb-0">No categories yet</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-12">
        <div class="card shadow">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">📰 Recent Posts</h5>
            </div>
            <div class="card-body">
                {% if stats.recent_posts %}
                    <div class="list-group list-group-flush">
                        {% for post in stats.recent_posts %}
                            <div class="list-group-item d-flex justify-content-between align-items-start">
                                <div class="ms-2 me-auto">
                                    <div class="fw-bold">{{ post.title }}</div>
                                    <small class="text-muted">by {{ post.author }} | {{ post.date_posted.strftime('%B %d, %Y') }}</small>
                                </div>
                                <span class="badge bg-primary rounded-pill">{{ post.category }}</span>
                            </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="text-center py-4">
                        <h5>📄 No posts yet</h5>
                        <p class="text-muted">Create your first post to get started!</p>
                        <a href="{{ url_for('create_post') }}" class="btn btn-primary">Create Post</a>
                    </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-12">
        <div class="card shadow">
            <div class="card-header">
                <h5 class="mb-0">🔗 Quick Links</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-3">
                        <a href="{{ url_for('create_post') }}" class="btn btn-success w-100 mb-2">✨ New Post</a>
                    </div>
                    <div class="col-md-3">
                        <a href="{{ url_for('home') }}" class="btn btn-primary w-100 mb-2">🏠 View Blog</a>
                    </div>
                    <div class="col-md-3">
                        <a href="{{ url_for('api_posts') }}" class="btn btn-info w-100 mb-2" target="_blank">🔌 API Posts</a>
                    </div>
                    <div class="col-md-3">
                        <a href="{{ url_for('contact') }}" class="btn btn-warning w-100 mb-2">📧 Contact Form</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",

        "404.html": """{% extends "base.html" %}

{% block title %}Page Not Found - Flask Blog{% endblock %}

{% block content %}
<div class="text-center py-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card shadow">
                <div class="card-body">
                    <h1 class="display-1 text-muted">404</h1>
                    <h2 class="mb-3">🔍 Page Not Found</h2>
                    <p class="lead">Sorry, the page you're looking for doesn't exist.</p>
                    <p class="text-muted">It might have been moved, deleted, or you entered the wrong URL.</p>
                    <div class="mt-4">
                        <a href="{{ url_for('home') }}" class="btn btn-primary me-2">🏠 Go Home</a>
                        <a href="{{ url_for('create_post') }}" class="btn btn-success">✨ Create Post</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",

        "500.html": """{% extends "base.html" %}

{% block title %}Server Error - Flask Blog{% endblock %}

{% block content %}
<div class="text-center py-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card shadow">
                <div class="card-body">
                    <h1 class="display-1 text-danger">500</h1>
                    <h2 class="mb-3">⚠️ Server Error</h2>
                    <p class="lead">Something went wrong on our end.</p>
                    <p class="text-muted">We're working to fix this issue. Please try again later.</p>
                    <div class="mt-4">
                        <a href="{{ url_for('home') }}" class="btn btn-primary me-2">🏠 Go Home</a>
                        <button onclick="location.reload()" class="btn btn-secondary">🔄 Refresh Page</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""
    }
    
    # Create all template files
    created_files = []
    for filename, content in templates.items():
        file_path = templates_dir / filename
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            created_files.append(filename)
            print(f"✅ Created: {filename}")
        except Exception as e:
            print(f"❌ Error creating {filename}: {e}")
    
    # Create a simple favicon file (empty but valid)
    favicon_path = static_dir / "favicon.ico"
    try:
        # Create empty favicon file to prevent 404 errors
        favicon_path.touch()
        print("✅ Created: favicon.ico")
    except Exception as e:
        print(f"❌ Error creating favicon: {e}")
    
    print(f"\n🎉 Template generation complete!")
    print(f"📊 Created {len(created_files)} template files")
    print(f"📁 Templates directory: {templates_dir.absolute()}")
    print(f"📁 Static directory: {static_dir.absolute()}")
    
    print(f"\n🚀 Now restart your Flask app:")
    print(f"   python3 flask_blog_app.py")
    print(f"\n🌐 Then visit: http://localhost:5000")
    
    return created_files

if __name__ == "__main__":
    create_flask_templates()

