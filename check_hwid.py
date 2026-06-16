import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storagon.settings")
django.setup()

from telegram_bot.models import UserHwid
print("HWID Count:", UserHwid.objects.count())
