from app import db
from datetime import datetime

class AIInteraction(db.Model):
    __tablename__ = 'ai_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    
    context_data = db.Column(db.JSON) # Optional: Store macros/status at time of query
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
