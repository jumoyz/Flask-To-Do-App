from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Set up file upload folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'vsgsrhhsehbg5+11rgarwglwd56'
db = SQLAlchemy(app)

# LoginManager Setup
login_manager = LoginManager(app)
#login_manager.login_view = "login"

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email= db.Column(db.String(255), unique=True, nullable=False)
    profile_pic = db.Column(db.String(255), nullable=True)
    theme = db.Column(db.String(50), nullable=False)
    notifications = db.Column(db.Boolean(255), nullable=False)
    google_connected = db.Column(db.Boolean, nullable=False)
    facebook_connected = db.Column(db.Boolean, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)
    favorite = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='tasks', lazy=True)

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose another.', 'danger')
        else:
            # Hash the password
            hashed_password = generate_password_hash(password)
            
            # Create a new user
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful! You can now login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query user from the database
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route('/', methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        task_description = request.form.get("task")
        if task_description:
            new_task = Task(description=task_description, user_id=current_user.id)
            db.session.add(new_task)
            db.session.commit()
        return redirect(url_for("index"))

    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", tasks=tasks)

@app.route('/complete/<int:task_id>')
@login_required
def complete(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("index"))
    task.done = True
    db.session.commit()
    return redirect(url_for("index"))

@app.route('/favorite/<int:task_id>')
@login_required
def favorite(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("index"))
    task.favorite = True
    db.session.commit()
    return redirect(url_for("index"))

@app.route('/delete/<int:task_id>')
@login_required
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("index"))
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("index"))

@app.route('/account', methods=['GET', 'POST'])
def account():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form['username']  # this won't change, just read from form
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        theme = request.form['theme']
        notifications = 'notifications' in request.form  # checked if true
        
        # Handle profile picture upload
        profile_pic = request.files.get('profile-pic')
        if profile_pic:
            filename = secure_filename(profile_pic.filename)
            profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Optionally, save the filename in the database for future reference
            
        # Logic to update user information in database goes here (user_data.update(...))

        # Password change logic
        if password and password == confirm_password:
            # Logic to hash and update the password in the database
            pass
        
        # Here, you can add more logic to update the user data, such as social connections or theme.
        # For example, save the theme preference and notification setting to the user's profile.

        flash("Account settings updated successfully!", "success")
        return redirect(url_for('account'))
    
    return render_template('account.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        # Handle feedback form submission
        pass
    return render_template('feedback.html')

@app.context_processor
def inject_year():
    return {'year': datetime.now().year}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Initialize the database only if not already initialized
    app.run(debug=False)
