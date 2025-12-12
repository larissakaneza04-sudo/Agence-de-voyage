"""
WSGI config for agence_transport project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

# Add the project directory to the Python path
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# Add the parent directory to the Python path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agence_transport.settings')

# Get the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
