from database import db

class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)


class JobRecruit(db.Model):
    __tablename__ = 'job_recruit'

    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(
        db.Integer,
        db.ForeignKey('jobs.id'),
        nullable=False
    )

    user_email = db.Column(db.String(100), nullable=False)
    user_phone = db.Column(db.String(12), nullable=False) 
    user_resume = db.Column(db.Text, nullable=False)
    applied_at = db.Column(db.DateTime, server_default=db.func.now())


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

class Admin(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(50), unique=True, nullable=False)
    admin_password = db.Column(db.String(100), nullable=False)
    admin_email = db.Column(db.String(100), unique=True, nullable=False)
