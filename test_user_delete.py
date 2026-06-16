import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storagon.settings')
django.setup()

from django.contrib.auth.models import User
print("EXISTING USERS:")
for u in User.objects.all():
    print(f"ID={u.id}, Username={u.username}, Active={u.is_active}")

# Let's try to delete user ID 10
try:
    user = User.objects.get(id=10)
    print(f"Attempting to delete user ID={user.id} ({user.username})...")
    user.delete()
    print("SUCCESSFULLY DELETED!")
except User.DoesNotExist:
    print("User ID 10 does not exist.")
except Exception as e:
    import traceback
    print("DELETE FAILED WITH ERROR:")
    traceback.print_exc()
