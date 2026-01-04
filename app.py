from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os
from database import db
from models import Job, JobRecruit, User, Admin



load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('secret_key')

# app.config['SQLALCHEMY_DATABASE_URI'] = (
#     f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
# )
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route('/')
def home():
    try:
        jobs = Job.query.all()
    except Exception as e:
        app.logger.error(e)
        jobs = []

    return render_template('list.html', lists=jobs)

@app.route('/jobs', methods=['GET', 'POST'])
def add_job():
    # if 'admin_id' in session:
        if request.method == 'POST':
            job = Job(
                title=request.form['jobTitle'],
                company=request.form['company'],
                location=request.form['location'],
                salary=request.form['salary'],
                description=request.form['description'],
            )
            db.session.add(job)
            db.session.commit()
            return redirect(url_for('home'))

        return render_template('jobs.html')
        # else:
        # flash("you are not admin")
        # return redirect(url_for('home'))

@app.route('/apply/<int:job_id>', methods=['POST'])
def apply_job(job_id):

    if 'user_id' not in session:
        flash("Please login to apply")
        return redirect(url_for('login'))

    user = db.session.get(User, session['user_id'])

    resume = request.files['resume']
    if resume.filename == '':
        flash("No file selected")
        return redirect(url_for('home'))

    filename = secure_filename(resume.filename)
    os.makedirs('uploads', exist_ok=True)
    resume.save(os.path.join('uploads', filename))

    application = JobRecruit(
        job_id=job_id,
        user_email=user.email,
        user_phone=request.form['phone'],
        user_resume=filename
    )

    db.session.add(application)
    db.session.commit()

    flash("You have successfully applied")
    return redirect(url_for('home'))



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        role = request.form.get('role')

        if role == 'admin':
            flash("Admins cannot sign up")
            return redirect(url_for('login'))

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("User already exists")
            return redirect(url_for('signup'))

        db.session.add(User(username=username, email=email, password=password))
        db.session.commit()

        flash("Account created. Please login.")
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        email = request.form['email']
        password = request.form['password']

        # ---------------- ADMIN LOGIN ----------------
        if role == 'admin':

            # 1️⃣ Try database admin first
            admin = Admin.query.filter_by(admin_email=email).first()
            if admin and admin.admin_password == password:
                session['admin_id'] = admin.id
                return redirect(url_for('home'))

            # 2️⃣ Fallback hardcoded admin (NO SIGNUP)
            if email == 'admin@gmail.com' and password == 'adminpw':
                session['admin_id'] = -1  # system admin
                return redirect(url_for('home'))

            flash("Invalid admin credentials")
            return redirect(url_for('login'))

        # ---------------- USER LOGIN ----------------
        else:
            user = User.query.filter_by(email=email).first()
            if user and user.password == password:
                session['user_id'] = user.id
                session['username'] = user.username
                return redirect(url_for('home'))

            flash("Invalid user credentials")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

with app.app_context():
        db.create_all()
if __name__ == '__main__':
    
    app.run()
