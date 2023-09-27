'''
project_name/              # The project's root directory
│
├── manage.py              # Django's command-line utility for managing the project
├── project_name/          # The main project directory
│   ├── __init__.py
│   ├── asgi.py            # ASGI configuration for web servers (e.g., Daphne)
│   ├── settings.py        # Project-wide settings and configurations
│   ├── urls.py            # Project-wide URL routing
│   └── wsgi.py            # WSGI configuration for web servers (e.g., Gunicorn)
│
├── app1/                   # Django apps within the project
│   ├── migrations/         # Database migration files (auto-generated)
│   ├── __init__.py
│   ├── admin.py            # Admin site configuration
│   ├── apps.py             # App-specific configuration
│   ├── models.py           # App-specific database models
│   ├── views.py            # App-specific views and view functions
│   ├── urls.py             # App-specific URL routing
│   ├── templates/          # HTML templates for the app
│   │   └── app1/
│   │       └── ...
│   ├── static/             # Static files (CSS, JavaScript, images) for the app
│   │   └── app1/
│   │       └── ...
│   └── tests.py            # App-specific test cases
│
├── app2/                   # Additional Django apps (similar structure to app1)
│   └── ...
│
├── templates/              # Project-wide HTML templates (shared across apps)
│   └── project_name/
│       └── ...
│
├── static/                 # Project-wide static files (shared across apps)
│   └── project_name/
│       └── ...
│
├── media/                  # User-uploaded media files (e.g., user profile images)
│   └── ...
│
├── requirements.txt        # List of project dependencies for pip
└── .gitignore              # Specifies files and directories to be ignored by Git

'''


#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'twentyfiveacres.settings')
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

from django.db import models
from django.contrib.auth.models import User
# ... (other imports)

class Property(models.Model):
    # ... (other fields)
    currentBid = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    bidder = models.ForeignKey(
        User, related_name="current_bidder", on_delete=models.CASCADE, null=True
    )

    # ... (other methods if any)
