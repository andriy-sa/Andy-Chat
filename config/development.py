import os
from datetime import timedelta

ORATOR_DATABASES = {
    'default': 'mysql',
    'mysql': {
        'driver': 'mysql',
        'host': 'localhost',
        'database': 'andy_chat',
        'user': 'root',
        'password': '1',
        'prefix': ''
    }
}
APPLICATION_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DEBUG = True
SECRET_KEY = "c4623a202d5b4e47c9a28380c60de500d5815b78"
STATIC_DIR = os.path.join(APPLICATION_DIR, 'static')
IMAGES_DIR = os.path.join(STATIC_DIR, 'images')
WTF_CSRF_ENABLED = False
JWT_AUTH_HEADER_PREFIX = 'Bearer'
JWT_AUTH_URL_RULE = None
JWT_AUTH_USERNAME_KEY = 'email'
JWT_EXPIRATION_DELTA = timedelta(days=30)