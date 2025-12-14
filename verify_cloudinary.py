import os
import django
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

# 2. Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import cloudinary
import cloudinary.uploader

def check_setup():
    print("--- Cloudinary Setup Verification ---")
    
    # Check Variables
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    print(f"CLOUD_NAME found: {'YES' if cloud_name else 'NO'}")
    print(f"API_KEY found: {'YES' if api_key else 'NO'}")
    print(f"API_SECRET found: {'YES' if api_secret else 'NO'}")

    if not all([cloud_name, api_key, api_secret]):
        print("\nERROR: Missing Cloudinary environment variables!")
        print("Please create a .env file in 'investor-dev-backend/' with these keys.")
        return

    # Check Settings
    from django.conf import settings
    print(f"\nDEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
    if "cloudinary" not in settings.DEFAULT_FILE_STORAGE:
        print("WARNING: DEFAULT_FILE_STORAGE does not seem to point to Cloudinary!")

    # Test Upload
    print("\nAttempting Test Upload...")
    try:
        # Create a dummy file
        with open("test_upload.txt", "w") as f:
            f.write("Cloudinary test file")

        # Upload
        response = cloudinary.uploader.upload("test_upload.txt", public_id="test_upload_verification", resource_type="auto")
        print("\nSUCCESS! Upload worked.")
        print(f"File URL: {response.get('url')}")
        
        # Cleanup
        os.remove("test_upload.txt")
        
    except Exception as e:
        print(f"\nFAILED: Upload failed with error: {e}")

if __name__ == "__main__":
    check_setup()
