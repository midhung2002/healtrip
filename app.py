from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime  # ✅ for `now` in dashboard

app = Flask(__name__)
app.secret_key = 'healtrip_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# ---------- User model ----------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            return "User already exists."

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        return "Invalid email or password"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])

        places = [
            {
                "name": "Manali",
                "image": "manali.jpeg",
                "link": "/place/manali",
                "duration": "3 Nights / 4 Days",
                "activities": "Skiing, Trekking, Hot Springs"
            },
            {
                "name": "Goa",
                "image": "goa.jpeg",
                "link": "/place/goa",
                "duration": "2 Nights / 3 Days",
                "activities": "Beaches, Nightlife, Water Sports"
            },
            {
                "name": "Munnar",
                "image": "munnar.jpeg",
                "link": "/place/munnar",
                "duration": "3 Nights / 4 Days",
                "activities": "Tea Gardens, Boating, Trekking"
            },
            {
                "name": "Shimla",
                "image": "shimla.jpeg",
                "link": "/place/shimla",
                "duration": "4 Nights / 5 Days",
                "activities": "Toy Train, Snowfall, Ridge Walk"
            }
        ]

        return render_template('dashboard.html', user=user, places=places, now=datetime.now())

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

# ---------- Run ----------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
