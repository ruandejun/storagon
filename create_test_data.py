import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storagon.settings")
django.setup()

from django.contrib.auth.models import User
from servermain.models import UserProfile
from cards_manager.models import Card
from storagon.enum import AccountType, AccountStatus
from django.utils import timezone
from datetime import timedelta

def create_or_update_user(username, email, password, is_staff=False, is_superuser=False, full_name="", account_type=0, account_status=0, storage_space=10737418240, plan_id=0):
    user, created = User.objects.get_or_create(username=username)
    user.email = email
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.set_password(password)
    user.save()
    
    profile, p_created = UserProfile.objects.get_or_create(user=user)
    profile.full_name = full_name if full_name else username
    profile.email = email
    profile.account_type = account_type
    profile.account_status = account_status
    profile.storage_space = storage_space
    profile.plan_id = plan_id
    profile.plan_expired = timezone.now() + timedelta(days=365)
    profile.save()
    
    print(f"{'Created' if created else 'Updated'} user {username} (Profile ID: {profile.id})")

def create_card_if_not_exists(card_number, expiry_date, cvv, status, extra_info):
    card, created = Card.objects.get_or_create(
        card_number=card_number,
        defaults={
            'expiry_date': expiry_date,
            'cvv': cvv,
            'status': status,
            'extra_info': extra_info
        }
    )
    if created:
        print(f"Created card {card_number} ({status})")
    else:
        # update status just for testing if already exists
        card.status = status
        card.save()

print("--- Creating/Updating Test Users ---")
# Admin User
create_or_update_user(
    username="admin", 
    email="admin@storagon.com", 
    password="admin", 
    is_staff=True, 
    is_superuser=True, 
    full_name="Storagon Admin Manager", 
    account_type=2, # Reseller / Admin
    account_status=0 # normal
)

# Client Users
create_or_update_user(
    username="client1", 
    email="client1@storagon.com", 
    password="client123", 
    is_staff=False, 
    is_superuser=False, 
    full_name="Nguyễn Văn A", 
    account_type=0, # User
    account_status=0,
    storage_space=15 * 1024 * 1024 * 1024, # 15 GB
    plan_id=1
)

create_or_update_user(
    username="client2", 
    email="client2@storagon.com", 
    password="client222", 
    is_staff=False, 
    is_superuser=False, 
    full_name="Trần Thị B (Affiliate)", 
    account_type=1, # Affiliate
    account_status=0,
    storage_space=100 * 1024 * 1024 * 1024, # 100 GB
    plan_id=2
)

create_or_update_user(
    username="client3", 
    email="client3@storagon.com", 
    password="client333", 
    is_staff=False, 
    is_superuser=False, 
    full_name="Lê Hoàng C (Banned)", 
    account_type=0, # User
    account_status=2, # Banned
    storage_space=2 * 1024 * 1024 * 1024, # 2 GB
    plan_id=0
)

print("\n--- Creating Test Cards ---")
create_card_if_not_exists("4111222233334444", "12/28", "123", "Chưa sử dụng", "Thẻ test 1")
create_card_if_not_exists("4222333344445555", "06/27", "456", "Đang sử dụng", "Thẻ test 2")
create_card_if_not_exists("4333444455556666", "08/29", "789", "Đã sử dụng", "Thẻ test 3")
create_card_if_not_exists("4444555566667777", "01/26", "000", "Thẻ chết", "Thẻ test 4")
create_card_if_not_exists("4555666677778888", "02/27", "111", "Thẻ sống", "Thẻ test 5")
create_card_if_not_exists("4666777788889999", "03/28", "222", "Thẻ tốt", "Thẻ test 6")
create_card_if_not_exists("4777888899990000", "04/28", "333", "Chưa sử dụng", "Thẻ test 7")
create_card_if_not_exists("4888999900001111", "05/29", "444", "Đang sử dụng", "Thẻ test 8")

print("\nDone populating test data!")
