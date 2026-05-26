from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

DATABASES['default']['NAME'] = os.environ.get('DB_NAME', 'maven_emailer_dev')
