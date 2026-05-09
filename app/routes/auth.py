from flask import Blueprint, request, jsonify
from app import db
from app.models.user_health import User, HealthProfile
from app.utils.auth_utils import encode_auth_token, token_required
from app.services.health_service import HealthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    user = User(username=data.get('username'), email=data.get('email'))
    user.set_password(data.get('password'))
    
    db.session.add(user)
    db.session.commit()
    
    # Create default health profile
    profile = HealthProfile(
        user_id=user.id,
        age=data.get('age'),
        gender=data.get('gender'),
        height=data.get('height'),
        weight=data.get('weight'),
        activity_level=data.get('activity_level', 'sedentary'),
        goal=data.get('goal', 'maintenance')
    )
    HealthService.update_user_targets(profile)
    
    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and user.check_password(data.get('password')):
        auth_token = encode_auth_token(user.id)
        return jsonify({
            'message': 'Logged in successfully',
            'auth_token': auth_token
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    profile = current_user.health_profile
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
        
    return jsonify({
        'username': current_user.username,
        'email': current_user.email,
        'age': profile.age,
        'gender': profile.gender,
        'height': profile.height,
        'weight': profile.weight,
        'activity_level': profile.activity_level,
        'goal': profile.goal,
        'targets': {
            'calories': profile.target_calories,
            'protein': profile.target_protein,
            'carbs': profile.target_carbs,
            'fats': profile.target_fats
        }
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
    profile = current_user.health_profile
    
    if not profile:
        profile = HealthProfile(user_id=current_user.id)
        db.session.add(profile)
    
    # Update fields if provided
    profile.age = data.get('age', profile.age)
    profile.gender = data.get('gender', profile.gender)
    profile.height = data.get('height', profile.height)
    profile.weight = data.get('weight', profile.weight)
    profile.activity_level = data.get('activity_level', profile.activity_level)
    profile.goal = data.get('goal', profile.goal)
    
    # Recalculate targets
    HealthService.update_user_targets(profile)
    
    return jsonify({'message': 'Profile updated successfully'}), 200

@auth_bp.route('/weight', methods=['POST'])
@token_required
def log_weight(current_user):
    data = request.get_json()
    weight = data.get('weight')
    
    if not weight:
        return jsonify({'error': 'Weight is required'}), 400
        
    try:
        weight_val = float(weight)
    except ValueError:
        return jsonify({'error': 'Weight must be a number'}), 400
        
    from app.models.user_health import WeightLog
    new_log = WeightLog(user_id=current_user.id, weight=weight_val)
    db.session.add(new_log)
    
    # Also update the profile weight safely
    if current_user.health_profile:
        current_user.health_profile.weight = weight_val
        try:
            HealthService.update_user_targets(current_user.health_profile)
        except Exception as e:
            print(f"DEBUG: HealthService error: {str(e)}")
            # targets güncellenemese bile kilo günlüğünü kurtar
            db.session.commit()
            return jsonify({'message': 'Weight logged, but targets could not be updated'}), 201
        
    db.session.commit()
    return jsonify({'message': 'Weight logged successfully'}), 201

@auth_bp.route('/weight-history', methods=['GET'])
@token_required
def get_weight_history(current_user):
    from app.models.user_health import WeightLog
    logs = WeightLog.query.filter_by(user_id=current_user.id).order_by(WeightLog.timestamp.asc()).all()
    return jsonify([{
        'weight': log.weight,
        'date': log.timestamp.strftime('%d %b')
    } for log in logs]), 200
