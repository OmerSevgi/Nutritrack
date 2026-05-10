from flask import Blueprint, request, jsonify
from app import db
from app.models.user_health import Workout, WorkoutRoutine, RoutineExercise, WorkoutSet
from app.utils.auth_utils import token_required
from app.services.ai_service import AIService
from datetime import datetime

fitness_bp = Blueprint('fitness', __name__)

@fitness_bp.route('/routines', methods=['GET'])
@token_required
def get_routines(current_user):
    routines = WorkoutRoutine.query.filter_by(user_id=current_user.id).order_by(WorkoutRoutine.day_of_week).all()
    return jsonify([{
        'id': r.id,
        'day_of_week': r.day_of_week,
        'name': r.name,
        'exercises': [{
            'id': e.id,
            'name': e.exercise_name,
            'sets': e.target_sets,
            'reps': e.target_reps
        } for e in r.exercises]
    } for r in routines]), 200

@fitness_bp.route('/routines', methods=['POST'])
@token_required
def create_routine(current_user):
    data = request.get_json()
    routine = WorkoutRoutine(
        user_id=current_user.id,
        day_of_week=data.get('day_of_week'),
        name=data.get('name')
    )
    db.session.add(routine)
    db.session.flush()
    
    for ex_data in data.get('exercises', []):
        ex = RoutineExercise(
            routine_id=routine.id,
            exercise_name=ex_data.get('name'),
            target_sets=ex_data.get('sets', 3),
            target_reps=ex_data.get('reps', 10)
        )
        db.session.add(ex)
    
    db.session.commit()
    return jsonify({'message': 'Routine created', 'id': routine.id}), 201

@fitness_bp.route('/routines/<int:id>', methods=['DELETE'])
@token_required
def delete_routine(current_user, id):
    routine = WorkoutRoutine.query.filter_by(id=id, user_id=current_user.id).first()
    if not routine:
        return jsonify({'error': 'Routine not found'}), 404
    db.session.delete(routine)
    db.session.commit()
    return jsonify({'message': 'Routine deleted'}), 200

@fitness_bp.route('/today-routine', methods=['GET'])
@token_required
def get_today_routine(current_user):
    today_day = datetime.utcnow().weekday()
    routine = WorkoutRoutine.query.filter_by(user_id=current_user.id, day_of_week=today_day).first()
    if not routine:
        return jsonify({'message': 'No routine for today'}), 404
        
    return jsonify({
        'id': routine.id,
        'name': routine.name,
        'exercises': [{
            'name': e.exercise_name,
            'sets': e.target_sets,
            'reps': e.target_reps
        } for e in routine.exercises]
    }), 200

@fitness_bp.route('/workout/complete', methods=['POST'])
@token_required
def complete_workout(current_user):
    data = request.get_json()
    routine_id = data.get('routine_id')
    
    # Validate routine_id if provided
    routine = None
    if routine_id:
        routine = WorkoutRoutine.query.filter_by(id=routine_id, user_id=current_user.id).first()
        if not routine:
            return jsonify({'error': 'Invalid routine ID'}), 400
    
    workout = Workout(
        user_id=current_user.id,
        routine_id=routine.id if routine else None,
        workout_type="Structured",
        timestamp=datetime.utcnow()
    )
    db.session.add(workout)
    db.session.flush()
    
    structured_data = []
    for ex_data in data.get('exercises', []):
        ex_summary = {
            'name': ex_data.get('name'),
            'sets': []
        }
        for i, set_data in enumerate(ex_data.get('sets', [])):
            w_set = WorkoutSet(
                workout_id=workout.id,
                exercise_name=ex_data.get('name'),
                set_number=i + 1,
                weight=float(set_data.get('weight', 0)),
                reps=int(set_data.get('reps', 0))
            )
            db.session.add(w_set)
            ex_summary['sets'].append({
                'weight': w_set.weight,
                'reps': w_set.reps
            })
        structured_data.append(ex_summary)
    
    ai_service = AIService()
    routine = WorkoutRoutine.query.get(data.get('routine_id')) if data.get('routine_id') else None
    planned_data = []
    if routine:
        planned_data = [{
            'name': e.exercise_name,
            'sets': e.target_sets,
            'reps': e.target_reps
        } for e in routine.exercises]

    user_profile = {
        'goal': current_user.health_profile.goal if current_user.health_profile else 'maintenance',
        'weight': current_user.health_profile.weight if current_user.health_profile else 70
    }
    
    feedback = ai_service.analyze_structured_workout(user_profile, planned_data, structured_data)
    workout.trainer_feedback = feedback
    workout.weight_data = structured_data
    
    db.session.commit()
    return jsonify({'message': 'Workout completed', 'feedback': feedback}), 201

@fitness_bp.route('/workouts', methods=['GET'])
@token_required
def get_workouts(current_user):
    workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.timestamp.desc()).limit(10).all()
    return jsonify([{
        'id': w.id,
        'type': w.workout_type,
        'weight_data': w.weight_data,
        'feedback': w.trainer_feedback,
        'date': w.timestamp.strftime('%d %b %H:%M')
    } for w in workouts]), 200

@fitness_bp.route('/stats/weekly', methods=['GET'])
@token_required
def get_weekly_stats(current_user):
    from datetime import timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    workouts = Workout.query.filter(Workout.user_id == current_user.id, Workout.timestamp >= seven_days_ago).all()
    
    stats = {}
    for w in workouts:
        if w.weight_data:
            for ex in w.weight_data:
                name = ex.get('name', 'Unknown')
                if name not in stats:
                    stats[name] = {'total_volume': 0, 'max_weight': 0, 'history': []}
                
                ex_volume = 0
                for s in ex.get('sets', []):
                    weight = float(s.get('weight', 0))
                    reps = int(s.get('reps', 0))
                    vol = weight * reps
                    ex_volume += vol
                    if weight > stats[name]['max_weight']:
                        stats[name]['max_weight'] = weight
                
                stats[name]['total_volume'] += ex_volume
                stats[name]['history'].append({
                    'date': w.timestamp.strftime('%d %b'),
                    'volume': ex_volume
                })
    
    return jsonify(stats), 200

@fitness_bp.route('/workout/<int:workout_id>', methods=['DELETE'])
@token_required
def delete_workout(current_user, workout_id):
    workout = Workout.query.filter_by(id=workout_id, user_id=current_user.id).first()
    if not workout:
        return jsonify({'error': 'Workout not found'}), 404
    
    db.session.delete(workout)
    db.session.commit()
    return jsonify({'message': 'Workout deleted successfully'}), 200
