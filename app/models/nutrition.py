from app import db
from datetime import datetime

class FoodItem(db.Model):
    __tablename__ = 'food_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    calories = db.Column(db.Float, default=0)
    protein = db.Column(db.Float, default=0)
    carbs = db.Column(db.Float, default=0)
    fats = db.Column(db.Float, default=0)
    
    # Micronutrients (optional but requested in roadmap)
    fiber = db.Column(db.Float, default=0)
    sugar = db.Column(db.Float, default=0)
    sodium = db.Column(db.Float, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DailyLog(db.Model):
    __tablename__ = 'daily_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=lambda: datetime.utcnow().date(), index=True)
    water_intake = db.Column(db.Integer, default=0) # in ml
    
    entries = db.relationship('LogEntry', backref='daily_log', lazy='dynamic', cascade="all, delete-orphan")
    
    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='_user_date_uc'),)

class LogEntry(db.Model):
    __tablename__ = 'log_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    daily_log_id = db.Column(db.Integer, db.ForeignKey('daily_logs.id'), nullable=False)
    food_item_id = db.Column(db.Integer, db.ForeignKey('food_items.id'), nullable=False)
    
    quantity = db.Column(db.Float, nullable=False) # grams or units
    meal_type = db.Column(db.String(20)) # breakfast, lunch, dinner, snack
    prompt_text = db.Column(db.Text, nullable=True) # To group items by AI prompt
    
    food_item = db.relationship('FoodItem')
