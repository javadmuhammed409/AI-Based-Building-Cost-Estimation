import os
import django
from django.conf import settings
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')
django.setup()

from core.ai_service import analyze_construction_image, configure_genai

# Load .env explicitly to be sure
try:
    import dotenv
    dotenv.load_dotenv(os.path.join(os.getcwd(), '.env'))
    print("Loaded .env file")
except ImportError:
    print("python-dotenv not found")

print(f"GOOGLE_API_KEY from env: {os.environ.get('GOOGLE_API_KEY')}")

# Test configuration
if not configure_genai():
    print("❌ configure_genai returned False. API Key missing or invalid.")
    sys.exit(1)
else:
    print("✅ configure_genai returned True.")

# Test Image Path (using one found in media)
image_path = os.path.join(settings.MEDIA_ROOT, 'ai_estimates', '1650-Sq-Ft-3BHK-Beautiful-Double-Floor-House-and-Free-Plan-3.webp')

if not os.path.exists(image_path):
    print(f"❌ Test image not found at {image_path}")
    sys.exit(1)

print(f"Analyzing image: {image_path}")

try:
    result = analyze_construction_image(image_path)
    print("Result:")
    print(result)
except Exception as e:
    print(f"❌ Exception occurred: {e}")
