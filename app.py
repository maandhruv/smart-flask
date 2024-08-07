from flask import Flask, render_template, request, url_for, redirect, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import json
from functools import wraps
import bcrypt
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth.db'
app.config['SECRET_KEY'] = 'mykey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    date_of_joining = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.date_of_joining = datetime.utcnow()
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('You need to be logged in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect('/register')
        
        new_user = User(password=password, username=username)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect('/login')
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = user.username
            user.last_login = datetime.utcnow()  # Update last login time
            db.session.commit()
            return redirect('/dashboard')
        else:
            flash('Incorrect password.', 'error')
            return render_template('login.html', error='Invalid User')
        
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if session['username']:
        user = User.query.filter_by(username=session['username']).first()
        device_data = []
        device_ids = [1, 2, 3, 4, 5]
        for device_id in device_ids:
            file_path = os.path.join(app.root_path, "devices", f"data_{device_id}.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, dict):
                            data = [data]
                        device_data.extend(data) 
                    except (json.JSONDecodeError, ValueError):
                        continue 
        return render_template('dashboard.html', user=user, device_data=device_data)
    return redirect('/login')

@app.route('/device_data')
@login_required
def device_data():
    device_data = []
    device_ids = [1, 2, 3, 4, 5]
    for device_id in device_ids:
        file_path = os.path.join(app.root_path, "devices", f"data_{device_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict):
                        data = [data]
                    device_data.extend(data)
                except (json.JSONDecodeError, ValueError):
                    continue 
    return jsonify(device_data)

@app.route('/profile')
@login_required
def profile():
    user = User.query.filter_by(username=session['username']).first()
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == "__main__":
    db.create_all()  # This will create the new database with the updated schema
    app.run(debug=True, port=8000)
