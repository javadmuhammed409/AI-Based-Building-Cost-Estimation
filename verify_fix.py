import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.forms import WorkerAttendanceForm

User = get_user_model()

def verify():
    print("Verifying fix for worker2...")
    try:
        worker = User.objects.get(username='worker2')
        form = WorkerAttendanceForm(worker)
        qs = form.fields['project'].queryset
        print(f"Projects available in form: {qs.count()}")
        for p in qs:
            print(f" - {p.title} (Status: {p.status})")
            
        if qs.count() > 0:
            print("SUCCESS: Worker can see projects.")
        else:
            print("FAILURE: Worker still sees no projects.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    verify()
