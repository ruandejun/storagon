import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

def debug_remote():
    hostname = "167.233.89.198"
    username = "root"
    password = "fJU9JtkbELfi"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=10)
        print("Connected!")
        
        python_code = """
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storagon.settings_base')
django.setup()
from telegram_bot.models import AccountsCreated
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from dashboard.views import AccountsCreatedViewSet, AccountsEmailsViewSet

factory = APIRequestFactory()

print('=== TESTING ALL USERS FOR GET ACTIVE ACCOUNT ===')
for u in User.objects.all():
    for t in ['apple', 'tiktok', 'hotmail', 'facebook']:
        request = factory.get('/dashboard/api/accounts/get-active-account/?type=' + t)
        request.user = u
        view = AccountsCreatedViewSet.as_view({'get': 'get_active_account'})
        res = view(request)
        if res.data.get('success'):
            acc = res.data.get('account_data')
            acc_id = acc.get('id')
            acc_email = acc.get('email')
            email_id = acc.get('email_id')
            print(f'User {u.username} (type={t}) got account {acc_id} ({acc_email}), email_id={email_id}')
            if email_id:
                req_email = factory.get(f'/dashboard/api/emails/{email_id}/')
                req_email.user = u
                view_email = AccountsEmailsViewSet.as_view({'get': 'retrieve'})
                try:
                    res_e = view_email(req_email, pk=email_id)
                    print(f'   -> Retrieve email {email_id}: status={res_e.status_code}')
                except Exception as ex:
                    print(f'   -> Retrieve email {email_id} FAILED: {ex}')
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
    debug_remote()
