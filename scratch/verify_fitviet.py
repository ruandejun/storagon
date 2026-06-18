import os
import sys
import django

# Add project path to sys.path
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storagon.settings_dev")
django.setup()

from django.test import Client
from cards_manager.models import Card
from telegram_bot.models import AccountsCreated
from storagon.enum import AccountStatus

def test_choices():
    print("--- Testing Python Model Choices & Enums ---")
    
    # 1. Check card status choices
    card_statuses = [c[0] for c in Card._meta.get_field('status').choices]
    print(f"Card status choices in DB: {card_statuses}")
    assert "Sub OK" in card_statuses, "Sub OK should be in Card status choices"
    assert "Sub lỗi" in card_statuses, "Sub lỗi should be in Card status choices"
    assert "Đã sử dụng" not in card_statuses, "Đã sử dụng should not be in Card status choices"
    print("✓ Card status choices check passed")
    
    # 2. Check account status enum
    print(f"Account status values: normal={AccountStatus.normal}, emailNotActivated={AccountStatus.emailNotActivated}, banned={AccountStatus.banned}, temporary={AccountStatus.temporary}, subOk={AccountStatus.subOk}, subError={AccountStatus.subError}")
    assert AccountStatus.subOk == 4, "subOk value should be 4"
    assert AccountStatus.subError == 5, "subError value should be 5"
    print("✓ Account status enum check passed")

def test_api_client():
    print("\n--- Testing API Client & Views ---")
    client = Client()
    
    # Authenticate
    login_success = client.login(username="Admin", password="admin")
    assert login_success, "Could not log in as Admin"
    print("✓ Logged in successfully as Admin via test client")
    
    # Check stats API
    res = client.get('/dashboard/api/stats/')
    assert res.status_code == 200, f"Stats API failed: {res.status_code}"
    stats_data = res.json()
    print(f"Stats API response: {stats_data}")
    assert 'sub_ok' in stats_data.get('status_counts', {}), "status_counts should include sub_ok count"
    assert 'sub_loi' in stats_data.get('status_counts', {}), "status_counts should include sub_loi count"
    print("✓ Stats API check passed")
    
    # Check card list API
    res = client.get('/dashboard/api/cards/')
    assert res.status_code == 200, f"Cards API failed: {res.status_code}"
    print("✓ Cards API list check passed")
    
    # Check account list API
    res = client.get('/dashboard/api/accounts/')
    assert res.status_code == 200, f"Accounts API failed: {res.status_code}"
    print("✓ Accounts API list check passed")

def test_template_content():
    print("\n--- Testing HTML Template Content ---")
    template_path = os.path.join("dashboard", "templates", "dashboard", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Check for Sub OK and Sub Lỗi options in HTML dropdowns
    assert 'value="Sub OK"' in html, "Should have Sub OK options for cards"
    assert 'value="Sub lỗi"' in html, "Should have Sub lỗi options for cards"
    assert 'value="Đã sử dụng"' not in html, "Should not have Đã sử dụng options for cards"
    assert 'value="4"' in html, "Should have option value 4 (Sub OK) for accounts"
    assert 'value="5"' in html, "Should have option value 5 (Sub Lỗi) for accounts"
    
    # Check for badge styling classes
    assert 'badge-sub-ok' in html, "Should have CSS class badge-sub-ok"
    assert 'badge-sub-error' in html, "Should have CSS class badge-sub-error"
    
    print("✓ HTML template content checks passed")

if __name__ == "__main__":
    try:
        test_choices()
        test_api_client()
        test_template_content()
        print("\nALL TESTS PASSED SUCCESSFULLY! 🎉")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        sys.exit(2)
