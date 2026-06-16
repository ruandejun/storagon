import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storagon.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction

# Let's try to delete user ID 10
try:
    user = User.objects.get(id=10)
    print(f"Attempting to cascade-delete user ID={user.id} ({user.username})...")
    
    from django.apps import apps
    
    with transaction.atomic():
        # Loop through all models in the project
        for model in apps.get_models():
            # Check for fields pointing to User
            for field in model._meta.fields:
                if field.related_model == User:
                    filter_kwargs = {field.name: user}
                    if model.objects.filter(**filter_kwargs).exists():
                        if field.null:
                            print(f"Nullifying {field.name} on model {model.__name__} for user {user.username}")
                            update_kwargs = {field.name: None}
                            model.objects.filter(**filter_kwargs).update(**update_kwargs)
                        else:
                            print(f"Deleting referencing records from model {model.__name__} for user {user.username}")
                            model.objects.filter(**filter_kwargs).delete()

        # Clean up UserProfile just in case
        from servermain.models import UserProfile
        UserProfile.objects.filter(user=user).delete()

        # Delete the user itself
        user.delete()
        print("SUCCESSFULLY DELETED WITH CASCADE!")
        
except User.DoesNotExist:
    print("User ID 10 does not exist.")
except Exception as e:
    import traceback
    print("DELETE FAILED WITH ERROR:")
    traceback.print_exc()
