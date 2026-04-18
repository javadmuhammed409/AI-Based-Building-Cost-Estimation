import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings') # Assuming project name is smartbuild or similar, need to check
django.setup()

from django.contrib.auth import get_user_model
from core.forms import WorkerAttendanceForm
from core.models import Project, WorkerProfile

User = get_user_model()

def test_form():
    print("Testing WorkerAttendanceForm...")
    
    # helper: create users if needed
    try:
        user_no_profile = User.objects.create(username='test_no_profile', role='WORKER')
    except:
        user_no_profile = User.objects.get(username='test_no_profile')

    try:
        contractor = User.objects.create(username='test_contractor', role='CONTRACTOR')
    except:
        contractor = User.objects.get(username='test_contractor')

    try:
        user_worker = User.objects.create(username='test_worker', role='WORKER')
        WorkerProfile.objects.create(user=user_worker, contractor=contractor, skill='General', daily_wage=500)
    except:
        user_worker = User.objects.get(username='test_worker')
        if not hasattr(user_worker, 'worker_profile'):
             WorkerProfile.objects.create(user=user_worker, contractor=contractor, skill='General', daily_wage=500)


    print("\n--- Contractors Inspection ---")
    contractors = User.objects.filter(role='CONTRACTOR')
    for c in contractors:
        project_count = Project.objects.filter(contractor=c).count()
        print(f"Contractor: {c.username} (ID: {c.id}) - Projects: {project_count}")
        projects = Project.objects.filter(contractor=c)
        for p in projects:
            print(f"  Project: {p.title} (Status: {p.status})")

    print("\n--- End Inspection ---")

if __name__ == '__main__':
    test_form()
