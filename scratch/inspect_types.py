import sys
import os

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storagon.settings_dev')

import django
django.setup()

from telegram_bot.models import AccountsType

for t in AccountsType.objects.all():
    print(f"ID={t.id}, name={t.name}, code={t.code}")
