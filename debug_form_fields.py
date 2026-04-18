
import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')
django.setup()

from core.forms import CustomUserCreationForm

form = CustomUserCreationForm()
print("Form Fields:", list(form.fields.keys()))
