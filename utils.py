import jwt
from django.conf import settings
from job_analysis.models import CustomUser

def jwt_encode(email):
    encoded_token = jwt.encode({'email': email}, settings.SECRET_KEY, algorithm='HS256')
    return encoded_token


def jwt_decode(token):
    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    return decoded_token


def auth_user(token):
    decoded_token = jwt_decode(token)
    email = decoded_token['email']
    obj = CustomUser.objects.filter(email=email).first()
    if obj:
        return True
    else:
        return False