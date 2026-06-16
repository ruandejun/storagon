# Integration test for AccountsCreated Actions
import sys
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storagon.settings')
django.setup()

from telegram_bot.models import AccountsCreated, AccountsType
from django.contrib.auth.models import User

def run_test():
    print("Starting integration test...")
    user = User.objects.first()
    if not user:
        print("No user found in the database. Test cannot proceed.")
        return
    
    # 1. Resolve or create account types
    tiktok_type, _ = AccountsType.objects.get_or_create(value='tiktok', defaults={'label': 'Tiktok'})
    facebook_type, _ = AccountsType.objects.get_or_create(value='facebook', defaults={'label': 'Facebook'})
    print("Resolved types: tiktok, facebook")

    # 2. Add account (simulate add_manual creation logic)
    email = 'test_tiktok_acc@domain.com'
    password = 'securepassword123'
    note = 'Integration test account'
    
    account = AccountsCreated.objects.create(
        owner=user,
        created_by=user,
        email=email,
        password=password,
        type=tiktok_type,
        browser_profiles=None,
        status=0,  # Active
        note=note
    )
    print(f"Created account: ID={account.id}, Email={account.email}, Type={account.type.value}, Status={account.status}")

    # 3. Simulate edit (update) logic
    account.email = 'test_tiktok_edited@domain.com'
    account.type = facebook_type
    account.status = 2  # Banned
    account.save()
    
    account.refresh_from_db()
    print(f"Edited account: ID={account.id}, Email={account.email}, Type={account.type.value}, Status={account.status}")
    if account.email != 'test_tiktok_edited@domain.com' or account.status != 2 or account.type != facebook_type:
        print("Error: Edit verification failed.")
        sys.exit(1)

    # 4. Simulate bulk status change
    updated_count = AccountsCreated.objects.filter(pk=account.id).update(status=3) # Temporary
    account.refresh_from_db()
    print(f"Bulk updated: status={account.status}, count={updated_count}")
    if account.status != 3 or updated_count != 1:
        print("Error: Bulk status update verification failed.")
        sys.exit(1)

    # 5. Simulate bulk delete
    deleted_count, _ = AccountsCreated.objects.filter(pk=account.id).delete()
    print(f"Deleted account count: {deleted_count}")
    if deleted_count != 1:
        print("Error: Delete verification failed.")
        sys.exit(1)

    print("ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_test()
