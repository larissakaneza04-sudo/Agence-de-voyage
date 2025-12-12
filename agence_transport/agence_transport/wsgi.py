"""
WSGI config for agence_transport project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""
import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

# Add the project directory to the Python path
sys.path.insert(0, str(BASE_DIR))

# Add the parent directory to the Python path
sys.path.insert(0, str(PROJECT_ROOT))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agence_transport.settings')

# This application object is used by any WSGI server configured to use this file.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
