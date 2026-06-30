import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

def check_remote():
    hostname = "167.233.89.198"
    username = "root"
    password = "fJU9JtkbELfi"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=10)
        python_code = """
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storagon.settings_base')
django.setup()
from telegram_bot.models import AccountsCreated
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from dashboard.views import AccountsCreatedViewSet

factory = APIRequestFactory()
u = User.objects.get(username='thuhong')
request = factory.get('/dashboard/api/accounts/get-active-account/?type=Tiktok')
request.user = u
view = AccountsCreatedViewSet.as_view({'get': 'get_active_account'})
response = view(request)
print(f'User: {u.username} (type=Tiktok case-insensitive) -> status={response.status_code}, data={response.data}')
"""
        cmd = f"cd /root/storagon && docker compose exec -T storagon python -c \"{python_code}\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print("STDOUT:\n", stdout.read().decode('utf-8', errors='ignore'))
        print("STDERR:\n", stderr.read().decode('utf-8', errors='ignore'))
    except Exception as e:
        print("Error:", e)
    finally:
        ssh.close()

if __name__ == "__main__":
    check_remote()
