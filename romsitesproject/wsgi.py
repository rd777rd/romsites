"""
WSGI config for romsitesproject project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'romsitesproject.settings')

application = get_wsgi_application()
