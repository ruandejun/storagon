import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storagon.settings')
django.setup()

from telegram_bot.models import AccountsCreated

obj = AccountsCreated.objects.create(
    email='testsub@domain.com',
    subscription='5',
    subscription_owner='John Doe'
)
print('VERIFIED:', obj.id, obj.email, obj.subscription, obj.subscription_owner)
obj.delete()
