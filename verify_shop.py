import os
import django
import sys

# Add the project root to the python path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')
django.setup()

from core.models import Product

def verify():
    # Create test products
    categories = ['Bedroom', 'Kitchen', 'Bathroom', 'Toilet', 'Visiting Room', 'Living Room', 'Interior Paint', 'Exterior Paint']
    created_products = []
    
    print("Creating test products...")
    for cat in categories:
        p = Product.objects.create(
            name=f"Test {cat} Item",
            description=f"Description for {cat}",
            price=100.00,
            stock=10,
            category=cat
        )
        created_products.append(p)
        print(f"Created: {p.name} ({p.category})")
        
    # Verify filtering
    print("\nVerifying filtering...")
    for cat in categories:
        count = Product.objects.filter(category=cat).count()
        if count >= 1:
            print(f"[PASS] Found {count} items for category '{cat}'")
        else:
            print(f"[FAIL] No items found for category '{cat}'")
            
    # cleanup
    print("\nCleaning up...")
    for p in created_products:
        p.delete()
    print("Cleanup complete.")

if __name__ == '__main__':
    verify()
