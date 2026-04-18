import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Project, WorkerProfile

User = get_user_model()

def fix_data():
    print("Fixing data for worker2...")
    
    try:
        worker = User.objects.get(username='worker2')
        print(f"Found worker: {worker.username}")
    except User.DoesNotExist:
        print("worker2 not found!")
        return

    try:
        contractor = User.objects.get(username='contractor') # Assuming username is 'contractor' based on previous output
        print(f"Found contractor: {contractor.username}")
    except User.DoesNotExist:
        print("Contractor 'contractor' not found!")
        # Fallback to ID 5
        contractor = User.objects.get(pk=5)
        print(f"Found contractor by ID 5: {contractor.username}")

    # 1. Create/Update Profile
    profile, created = WorkerProfile.objects.get_or_create(user=worker, defaults={
        'contractor': contractor,
        'skill': 'General',
        'daily_wage': 800
    })
    if created:
        print("Created WorkerProfile for worker2")
    else:
        profile.contractor = contractor
        profile.save()
        print("Updated WorkerProfile for worker2")
        
    # 2. Update Project Status
    projects = Project.objects.filter(contractor=contractor)
    if projects.exists():
        p = projects.first()
        p.status = 'IN_PROGRESS'
        p.save()
        print(f"Updated project '{p.title}' status to IN_PROGRESS")
    else:
        print("No projects found for contractor!")

if __name__ == '__main__':
    fix_data()
