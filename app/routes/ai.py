from flask import Blueprint, request, jsonify
from app import db
from app.models.interaction import AIInteraction
from app.models.user_health import Workout
from app.utils.auth_utils import token_required
from app.services.ai_service import AIService
from app.services.nutrition_service import NutritionService
from datetime import datetime

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ask-coach', methods=['POST'])
@token_required
def ask_coach(current_user):
    data = request.get_json()
    user_query = data.get('query')
    
    if not user_query:
        return jsonify({'error': 'Query is required'}), 400
    
    # Get current status using NutritionService
    today = datetime.utcnow().date()
    daily_status = NutritionService.get_daily_summary(current_user, today)
    
    user_profile = {
        'username': current_user.username,
        'age': current_user.health_profile.age if current_user.health_profile else None,
        'gender': current_user.health_profile.gender if current_user.health_profile else None,
        'height': current_user.health_profile.height if current_user.health_profile else None,
        'weight': current_user.health_profile.weight if current_user.health_profile else None,
        'goal': current_user.health_profile.goal if current_user.health_profile else None,
        'target_calories': daily_status['targets']['calories'],
        'target_protein': daily_status['targets']['protein'],
        'target_carbs': daily_status['targets']['carbs'],
        'target_fats': daily_status['targets']['fats']
    }
    
    ai_service = AIService()
    response_text = ai_service.generate_response(user_profile, daily_status, user_query)
    
    # Save interaction
    interaction = AIInteraction(
        user_id=current_user.id,
        user_message=user_query,
        ai_response=response_text,
        context_data={
            'daily_status': daily_status,
            'user_profile': user_profile
        }
    )
    db.session.add(interaction)
    db.session.commit()
    
    return jsonify({'response': response_text}), 200

@ai_bp.route('/recommend', methods=['POST'])
@token_required
def recommend_food(current_user):
    # Get current status
    today = datetime.utcnow().date()
    daily_status = NutritionService.get_daily_summary(current_user, today)
    
    user_profile = {
        'goal': current_user.health_profile.goal if current_user.health_profile else 'maintenance',
        'target_calories': daily_status['targets']['calories'],
        'target_protein': daily_status['targets']['protein'],
        'calories': daily_status['calories'],
        'protein': daily_status['protein']
    }
    
    ai_service = AIService()
    recommendation = ai_service.get_food_recommendations(user_profile, daily_status)
    
    return jsonify({'recommendation': recommendation}), 200

@ai_bp.route('/fridge-assistant', methods=['POST'])
@token_required
def fridge_assistant(current_user):
    data = request.get_json()
    ingredients = data.get('ingredients')
    
    if not ingredients:
        return jsonify({'error': 'No ingredients provided'}), 400
        
    ai_service = AIService()
    user_profile = {
        'goal': current_user.health_profile.goal if current_user.health_profile else 'maintenance'
    }
    
    recipe = ai_service.generate_fridge_recipe(user_profile, ingredients)
    return jsonify({'recipe': recipe}), 200

@ai_bp.route('/daily-briefing', methods=['GET'])
@token_required
def daily_briefing(current_user):
    from datetime import timedelta
    yesterday = (datetime.utcnow() - timedelta(days=1)).date()
    
    from app.services.nutrition_service import NutritionService
    yesterday_stats = NutritionService.get_daily_summary(current_user, yesterday)
    
    ai_service = AIService()
    user_profile = {
        'goal': current_user.health_profile.goal if current_user.health_profile else 'maintenance'
    }
    
    briefing = ai_service.generate_daily_briefing(user_profile, yesterday_stats)
    return jsonify({'briefing': briefing}), 200

@ai_bp.route('/shopping-list', methods=['GET'])
@token_required
def shopping_list(current_user):
    from datetime import timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    workouts = Workout.query.filter(Workout.user_id == current_user.id, Workout.timestamp >= seven_days_ago).all()
    
    total_volume = 0
    for w in workouts:
        if w.weight_data:
            for ex in w.weight_data:
                total_volume += float(ex.get('weight', 0)) * int(ex.get('sets', 0)) * int(ex.get('reps', 0))
                
    ai_service = AIService()
    user_profile = {
        'goal': current_user.health_profile.goal if current_user.health_profile else 'maintenance'
    }
    
    shopping_list = ai_service.generate_shopping_list(user_profile, {'total_volume': total_volume})
    return jsonify({'shopping_list': shopping_list}), 200
