#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

def main():
    """Run administrative tasks."""
    # Set up the path
    BASE_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = BASE_DIR.parent
    
    # Add the project directory to the Python path
    if str(BASE_DIR) not in sys.path:
        sys.path.append(str(BASE_DIR))
    
    # Add the parent directory to the Python path
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.append(str(PROJECT_ROOT))
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agence_transport.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()