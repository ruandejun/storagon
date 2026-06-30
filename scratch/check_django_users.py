import paramiko

def check_users():
    hostname = "167.233.89.198"
    username = "root"
    password = "fJU9JtkbELfi"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=10)
        cmd = "cd /root/storagon && docker compose exec -T storagon python manage.py shell -c \"from django.contrib.auth.models import User; print([(u.username, u.is_active, u.is_staff) for u in User.objects.all()[:10]])\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print("Users:", stdout.read().decode('utf-8'))
        print("ERR:", stderr.read().decode('utf-8'))
    finally:
        ssh.close()

if __name__ == '__main__':
    check_users()
