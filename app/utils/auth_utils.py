import jwt
import datetime
from flask import current_app
from functools import wraps
from flask import request, jsonify
from app.models.user_health import User

def encode_auth_token(user_id):
    """
    Generates the Auth Token
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return str(e)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check standard Authorization header or custom X-Authorization
        auth_header = request.headers.get('Authorization') or request.headers.get('X-Authorization')
        
        if auth_header:
            if "Bearer " in auth_header:
                token = auth_header.split(" ")[1]
            else:
                token = auth_header
        
        # Fallback for proxy environments
        if not token and request.environ.get('HTTP_AUTHORIZATION'):
            token = request.environ.get('HTTP_AUTHORIZATION').split(" ")[1] if "Bearer " in request.environ.get('HTTP_AUTHORIZATION') else request.environ.get('HTTP_AUTHORIZATION')
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=["HS256"])
            current_user = User.query.get(data['sub'])
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            return jsonify({'message': f'Error: {str(e)}'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated
