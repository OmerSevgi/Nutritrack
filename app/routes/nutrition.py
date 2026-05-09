from flask import Blueprint, request, jsonify
from app import db
from app.models.nutrition import FoodItem, DailyLog, LogEntry
from app.utils.auth_utils import token_required
from app.services.nutrition_service import NutritionService
from app.services.ai_service import AIService
from datetime import datetime
import re

nutrition_bp = Blueprint('nutrition', __name__)

@nutrition_bp.route('/food', methods=['POST'])
@token_required
def add_food(current_user):
    data = request.get_json()
    food = FoodItem(
        name=data.get('name'),
        calories=data.get('calories'),
        protein=data.get('protein'),
        carbs=data.get('carbs'),
        fats=data.get('fats')
    )
    db.session.add(food)
    db.session.commit()
    return jsonify({'message': 'Food item created', 'id': food.id}), 201

@nutrition_bp.route('/log', methods=['POST'])
@token_required
def log_meal(current_user):
    data = request.get_json()
    date_str = data.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    log = DailyLog.query.filter_by(user_id=current_user.id, date=date_obj).first()
    if not log:
        log = DailyLog(user_id=current_user.id, date=date_obj)
        db.session.add(log)
        db.session.commit()
    
    entry = LogEntry(
        daily_log_id=log.id,
        food_item_id=data.get('food_item_id'),
        quantity=data.get('quantity'),
        meal_type=data.get('meal_type')
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'message': 'Meal logged successfully'}), 201

@nutrition_bp.route('/log-ai', methods=['POST'])
@token_required
def log_ai_meal(current_user):
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
        
    ai_service = AIService()
    food_names_raw = ai_service.ask_coach(f"Extract only food names as comma-separated list in English from this text: '{text}'. If none found, return empty.")
    food_list = [f.strip() for f in food_names_raw.split(',') if f.strip()]
    
    if not food_list:
        return jsonify({'error': 'Could not parse food items'}), 400
        
    from app.integrations.ninjas_client import CalorieNinjasClient
    ninjas_client = CalorieNinjasClient()
    
    today = datetime.utcnow().date()
    log = DailyLog.query.filter_by(user_id=current_user.id, date=today).first()
    if not log:
        log = DailyLog(user_id=current_user.id, date=today)
        db.session.add(log)
        db.session.flush()
    
    try:
        logged_items = []
        for food_name in food_list:
            data = ninjas_client.get_nutrition(food_name)
            item = data[0] if data and len(data) > 0 else None
            if not item: continue
            
            print(f"DEBUG: Processing item from API: {item}")
            
            name = item.get('name')
            qty = 1.0 
            
            food = FoodItem.query.filter(FoodItem.name.ilike(name)).first()
            if not food:
                food = FoodItem(
                    name=name,
                    calories=float(item.get('calories', 0)),
                    protein=float(item.get('protein_g', 0)),
                    carbs=float(item.get('carbohydrates_total_g', 0)),
                    fats=float(item.get('fat_total_g', 0))
                )
                db.session.add(food)
            else:
                food.calories = float(item.get('calories', 0))
                food.protein = float(item.get('protein_g', 0))
                food.carbs = float(item.get('carbohydrates_total_g', 0))
                food.fats = float(item.get('fat_total_g', 0))
                db.session.add(food)
            
            db.session.flush()
            entry = LogEntry(
                daily_log_id=log.id,
                food_item_id=food.id,
                quantity=qty,
                meal_type='auto',
                prompt_text=text
            )
            db.session.add(entry)
            logged_items.append(item)
        
        db.session.commit()
    except Exception as e:
        import traceback
        print(f"DEBUG: Critical Error in log_ai_meal: {str(e)}")
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': f'Failed to save entries: {str(e)}'}), 500
    
    return jsonify({
        'message': f'{len(logged_items)} items logged',
        'items': logged_items
    }), 201

@nutrition_bp.route('/summary', methods=['GET'])
@token_required
def get_summary(current_user):
    date_str = request.args.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    summary = NutritionService.get_daily_summary(current_user, date_obj)
    return jsonify(summary), 200

@nutrition_bp.route('/weekly-history', methods=['GET'])
@token_required
def get_weekly_history(current_user):
    history = NutritionService.get_weekly_history(current_user)
    return jsonify(history), 200

@nutrition_bp.route('/water', methods=['POST'])
@token_required
def log_water(current_user):
    data = request.get_json()
    amount = data.get('amount', 250)
    
    today = datetime.utcnow().date()
    log = DailyLog.query.filter_by(user_id=current_user.id, date=today).first()
    if not log:
        log = DailyLog(user_id=current_user.id, date=today)
        db.session.add(log)
    
    log.water_intake = max(0, (log.water_intake or 0) + amount)
    db.session.commit()
    
    return jsonify({'message': 'Water intake updated', 'total': log.water_intake}), 200

@nutrition_bp.route('/water', methods=['DELETE'])
@token_required
def reset_water(current_user):
    today = datetime.utcnow().date()
    log = DailyLog.query.filter_by(user_id=current_user.id, date=today).first()
    if log:
        log.water_intake = 0
        db.session.commit()
    return jsonify({'message': 'Water intake reset successfully', 'total': 0}), 200

@nutrition_bp.route('/log/group', methods=['DELETE'])
@token_required
def delete_meal_group(current_user):
    data = request.get_json()
    prompt_text = data.get('prompt_text')
    date_str = data.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    if not prompt_text:
        return jsonify({'error': 'No meal group identified'}), 400
        
    log = DailyLog.query.filter_by(user_id=current_user.id, date=date_obj).first()
    if not log:
        return jsonify({'error': 'Log not found'}), 404
        
    entries_to_delete = LogEntry.query.filter_by(daily_log_id=log.id, prompt_text=prompt_text).all()
    
    for entry in entries_to_delete:
        db.session.delete(entry)
    
    db.session.commit()
    return jsonify({'message': f'{len(entries_to_delete)} items deleted'}), 200

@nutrition_bp.route('/log/<int:entry_id>', methods=['DELETE'])
@token_required
def delete_log_entry(current_user, entry_id):
    entry = LogEntry.query.get(entry_id)
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404
    
    if entry.daily_log.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Entry deleted successfully'}), 200
