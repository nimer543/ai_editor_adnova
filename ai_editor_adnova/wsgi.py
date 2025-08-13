import os
import sys

# Add the path to the project in sys.path
project_path = '/home/nimer543/ai_editor_adnova'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Set environment variables before importing Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_editor_adnova.settings')
os.environ.setdefault('GEMINI_API_KEY', 'AIzaSyDUiBx3v2Y-SH4mTba-80OMae2lyt7-Zek')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
