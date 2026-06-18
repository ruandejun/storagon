import sys
import os

# Add cwd to path
sys.path.append(os.getcwd())

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storagon.settings_dev')

import django
django.setup()

from telegram_bot.models import AccountsEmails, AccountsCreated

print("--- AccountsEmails fields ---")
for f in AccountsEmails._meta.get_fields():
    print(f"{f.name}: {type(f).__name__}")

print("\n--- AccountsCreated fields ---")
for f in AccountsCreated._meta.get_fields():
    print(f"{f.name}: {type(f).__name__}")
