import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

def test_raw_login():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('167.233.89.198', username='root', password='fJU9JtkbELfi')
    
    python_cmd = (
        "import sys, logging; "
        "logging.basicConfig(level=logging.DEBUG); "
        "from dashboard.apple_auth import AppleAuthClient; "
        "client = AppleAuthClient(); "
        "res = client.login('tuan.storagon@gmail.com', 'Goldcoast123!@#'); "
        "print('RESULT:', res)"
    )
    
    cmd = f'cd /root/storagon && docker compose exec -T storagon python -c "{python_cmd}"'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print("STDOUT:\n", stdout.read().decode('utf-8', errors='ignore'))
    print("STDERR:\n", stderr.read().decode('utf-8', errors='ignore'))
    ssh.close()

if __name__ == '__main__':
    test_raw_login()
