from flask import Blueprint, request, jsonify
from app import db
from app.models.nutrition import FoodItem, DailyLog, LogEntry
from app.utils.auth_utils import token_required
from app.services.nutrition_service import NutritionService
from datetime import datetime

nutrition_bp = Blueprint('nutrition', __name__)

@nutrition_bp.route('/food', methods=['POST'])
@token_required
def add_food(current_user):
    data = request.get_json()
    food = FoodItem(
        name=data.get('name'), calories=data.get('calories'),
        protein=data.get('protein'), carbs=data.get('carbs'), fats=data.get('fats')
    )
    db.session.add(food)
    db.session.commit()
    return jsonify({'message': 'Food created', 'id': food.id}), 201

@nutrition_bp.route('/log', methods=['POST'])
@token_required
def log_meal(current_user):
    data = request.get_json()
    NutritionService.log_manual_meal(current_user, {'id': data.get('food_item_id')}, data.get('quantity'), data.get('meal_type'))
    return jsonify({'message': 'Meal logged'}), 201

@nutrition_bp.route('/log-ai', methods=['POST'])
@token_required
def log_ai_meal(current_user):
    data = request.get_json()
    items = NutritionService.log_ai_meal(current_user, data.get('text'))
    if items: return jsonify({'message': 'Logged', 'items': items}), 201
    return jsonify({'error': 'AI parsing failed'}), 400

@nutrition_bp.route('/summary', methods=['GET'])
@token_required
def get_summary(current_user):
    date_str = request.args.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    return jsonify(NutritionService.get_daily_summary(current_user, date_obj)), 200

@nutrition_bp.route('/weekly-history', methods=['GET'])
@token_required
def get_weekly_history(current_user):
    return jsonify(NutritionService.get_weekly_history(current_user)), 200

@nutrition_bp.route('/water', methods=['POST'])
@token_required
def log_water(current_user):
    data = request.get_json()
    today = datetime.utcnow().date()
    log = DailyLog.query.filter_by(user_id=current_user.id, date=today).first() or DailyLog(user_id=current_user.id, date=today)
    log.water_intake = max(0, (log.water_intake or 0) + data.get('amount', 250))
    db.session.add(log); db.session.commit()
    return jsonify({'message': 'Water updated', 'total': log.water_intake}), 200

@nutrition_bp.route('/water', methods=['DELETE'])
@token_required
def reset_water(current_user):
    log = DailyLog.query.filter_by(user_id=current_user.id, date=datetime.utcnow().date()).first()
    if log: log.water_intake = 0; db.session.commit()
    return jsonify({'message': 'Reset', 'total': 0}), 200

@nutrition_bp.route('/log/group', methods=['DELETE'])
@token_required
def delete_meal_group(current_user):
    data = request.get_json()
    log = DailyLog.query.filter_by(user_id=current_user.id, date=datetime.strptime(data.get('date'), '%Y-%m-%d').date()).first()
    if log:
        LogEntry.query.filter_by(daily_log_id=log.id, prompt_text=data.get('prompt_text')).delete()
        db.session.commit()
    return jsonify({'message': 'Group deleted'}), 200
