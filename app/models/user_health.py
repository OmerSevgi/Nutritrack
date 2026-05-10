from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    health_profile = db.relationship('HealthProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    daily_logs = db.relationship('DailyLog', backref='user', lazy='dynamic')
    ai_interactions = db.relationship('AIInteraction', backref='user', lazy='dynamic')
    routines = db.relationship('WorkoutRoutine', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class HealthProfile(db.Model):
    __tablename__ = 'health_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10)) # male, female, other
    height = db.Column(db.Float) # cm
    weight = db.Column(db.Float) # kg
    activity_level = db.Column(db.String(20)) # sedentary, lightly_active, etc.
    goal = db.Column(db.String(50)) # maintenance, hypertrophy, fat_loss
    
    # Gamification
    streak_count = db.Column(db.Integer, default=0)
    last_streak_date = db.Column(db.Date)
    last_nutri_score = db.Column(db.Integer, default=0)
    
    # Calculated targets (will be updated by services)
    target_calories = db.Column(db.Integer)
    target_protein = db.Column(db.Float)
    target_carbs = db.Column(db.Float)
    target_fats = db.Column(db.Float)
    
    fitness_program = db.Column(db.Text) # General program context
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WorkoutRoutine(db.Model):
    __tablename__ = 'workout_routines'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False) # 0=Monday, 6=Sunday
    name = db.Column(db.String(100)) # e.g., "Push Day"
    exercises = db.relationship('RoutineExercise', backref='routine', lazy='dynamic', cascade="all, delete-orphan")

class RoutineExercise(db.Model):
    __tablename__ = 'routine_exercises'
    id = db.Column(db.Integer, primary_key=True)
    routine_id = db.Column(db.Integer, db.ForeignKey('workout_routines.id'), nullable=False)
    exercise_name = db.Column(db.String(100), nullable=False)
    target_sets = db.Column(db.Integer, default=3)
    target_reps = db.Column(db.Integer, default=10)

class Workout(db.Model):
    __tablename__ = 'workouts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    routine_id = db.Column(db.Integer, db.ForeignKey('workout_routines.id'), nullable=True)
    
    description = db.Column(db.Text, nullable=True)
    workout_type = db.Column(db.String(50)) 
    duration = db.Column(db.Integer) 
    calories_burned = db.Column(db.Integer)
    weight_data = db.Column(db.JSON) # Kept for backward compatibility or general storage
    
    trainer_feedback = db.Column(db.Text) 
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_rel = db.relationship('User', backref=db.backref('workouts', lazy='dynamic'))
    sets = db.relationship('WorkoutSet', backref='workout', lazy='dynamic', cascade="all, delete-orphan")

class WorkoutSet(db.Model):
    __tablename__ = 'workout_sets'
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_name = db.Column(db.String(100), nullable=False)
    set_number = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float)
    reps = db.Column(db.Integer)

class WeightLog(db.Model):
    __tablename__ = 'weight_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    weight = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('weight_history', lazy='dynamic'))
