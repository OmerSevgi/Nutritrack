from flask import Blueprint, jsonify
from app import db
from app.models.nutrition import FoodItem
from app.utils.auth_utils import token_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/foods', methods=['GET'])
@token_required
def get_all_foods(current_user):
    # Basit güvenlik kontrolü: Sadece admin (id=1) erişebilir
    if current_user.id != 1:
        return jsonify({'error': 'Unauthorized'}), 403
    
    foods = FoodItem.query.all()
    return jsonify([{
        'id': f.id,
        'name': f.name,
        'calories': f.calories,
        'protein': f.protein,
        'carbs': f.carbs,
        'fats': f.fats
    } for f in foods]), 200

@admin_bp.route('/food/<int:food_id>', methods=['DELETE'])
@token_required
def delete_food(current_user, food_id):
    if current_user.id != 1:
        return jsonify({'error': 'Unauthorized'}), 403
        
    food = FoodItem.query.get(food_id)
    if not food:
        return jsonify({'error': 'Food not found'}), 404
        
    db.session.delete(food)
    db.session.commit()
    return jsonify({'message': 'Food deleted successfully'}), 200
