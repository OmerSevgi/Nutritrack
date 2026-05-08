from flask import Blueprint, request, jsonify
from app import db
from app.models.user_health import Workout
from app.utils.auth_utils import token_required
from app.services.ai_service import AIService
from datetime import datetime

fitness_bp = Blueprint('fitness', __name__)

@fitness_bp.route('/workout', methods=['POST'])
@token_required
def log_workout(current_user):
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({'error': 'No workout description provided'}), 400
        
    ai_service = AIService()
    
    # Fetch last 5 workouts for context
    history = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.timestamp.desc()).limit(5).all()
    history_data = [{'date': w.timestamp.strftime('%Y-%m-%d'), 'description': w.description} for w in history]
    
    user_profile = {
        'goal': current_user.health_profile.goal if current_user.health_profile else 'maintenance',
        'weight': current_user.health_profile.weight if current_user.health_profile else 70
    }
    
    analysis = ai_service.analyze_workout(user_profile, text, workout_history=history_data)
    
    if not analysis:
        return jsonify({'error': 'AI could not analyze workout'}), 500
        
    workout = Workout(
        user_id=current_user.id,
        description=text,
        workout_type="Fitness/Weight", # Standardized
        duration=0, # No longer priority
        calories_burned=0, # As requested
        weight_data=analysis.get('exercises'), # Store the list of exercises
        trainer_feedback=analysis.get('feedback')
    )
    
    db.session.add(workout)
    db.session.commit()
    
    return jsonify({
        'message': 'Workout logged successfully',
        'analysis': analysis
    }), 201

@fitness_bp.route('/workouts', methods=['GET'])
@token_required
def get_workouts(current_user):
    workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.timestamp.desc()).limit(10).all()
    return jsonify([{
        'id': w.id,
        'description': w.description,
        'type': w.workout_type,
        'duration': w.duration,
        'calories': w.calories_burned,
        'weight_data': w.weight_data, # New field
        'feedback': w.trainer_feedback,
        'date': w.timestamp.strftime('%d %b %H:%M')
    } for w in workouts]), 200

@fitness_bp.route('/stats/weekly', methods=['GET'])
@token_required
def get_weekly_stats(current_user):
    from datetime import timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    workouts = Workout.query.filter(Workout.user_id == current_user.id, Workout.timestamp >= seven_days_ago).all()
    
    stats = {} # Exercise -> {volume: X, max_weight: Y, dates: []}
    
    for w in workouts:
        if w.weight_data:
            for ex in w.weight_data:
                name = ex.get('name', 'Unknown')
                weight = float(ex.get('weight', 0))
                sets = int(ex.get('sets', 0))
                reps = int(ex.get('reps', 0))
                volume = weight * sets * reps
                
                if name not in stats:
                    stats[name] = {'total_volume': 0, 'max_weight': 0, 'history': []}
                
                stats[name]['total_volume'] += volume
                if weight > stats[name]['max_weight']:
                    stats[name]['max_weight'] = weight
                
                stats[name]['history'].append({
                    'date': w.timestamp.strftime('%d %b'),
                    'weight': weight,
                    'volume': volume
                })
    
    return jsonify(stats), 200

@fitness_bp.route('/stats/report', methods=['GET'])
@token_required
def get_weekly_report(current_user):
    # Reuse get_weekly_stats logic to get data
    from datetime import timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    workouts = Workout.query.filter(Workout.user_id == current_user.id, Workout.timestamp >= seven_days_ago).all()
    
    stats = {}
    for w in workouts:
        if w.weight_data:
            for ex in w.weight_data:
                name = ex.get('name', 'Unknown')
                weight = float(ex.get('weight', 0))
                sets = int(ex.get('sets', 0))
                reps = int(ex.get('reps', 0))
                volume = weight * sets * reps
                if name not in stats:
                    stats[name] = {'total_volume': 0, 'max_weight': 0}
                stats[name]['total_volume'] += volume
                if weight > stats[name]['max_weight']:
                    stats[name]['max_weight'] = weight
    
    ai_service = AIService()
    user_profile = {
        'goal': current_user.health_profile.goal if current_user.health_profile else 'maintenance'
    }
    
    report = ai_service.generate_weekly_fitness_report(user_profile, stats)
    return jsonify({'report': report}), 200

@fitness_bp.route('/workout/<int:workout_id>', methods=['DELETE'])
@token_required
def delete_workout(current_user, workout_id):
    workout = Workout.query.filter_by(id=workout_id, user_id=current_user.id).first()
    if not workout:
        return jsonify({'error': 'Workout not found'}), 404
    
    db.session.delete(workout)
    db.session.commit()
    return jsonify({'message': 'Workout deleted successfully'}), 200
