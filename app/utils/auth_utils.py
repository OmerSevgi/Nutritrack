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
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
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
        # Check standard Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if len(auth_header.split(" ")) > 1:
                token = auth_header.split(" ")[1]
            else:
                token = auth_header
        # Fallback for proxy/server environments
        elif request.environ.get('HTTP_AUTHORIZATION'):
            auth_header = request.environ.get('HTTP_AUTHORIZATION')
            if len(auth_header.split(" ")) > 1:
                token = auth_header.split(" ")[1]
            else:
                token = auth_header
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # Note: Ensure SECRET_KEY in env is > 32 chars
            data = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=["HS256"])
            current_user = User.query.get(data['sub'])
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            return jsonify({'message': f'Error decoding token: {str(e)}'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated
