import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

def check_500_error():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('167.233.89.198', username='root', password='fJU9JtkbELfi')
    
    cmd = 'cd /root/storagon && docker compose logs storagon --tail=100'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print("LOGS:\n", stdout.read().decode('utf-8', errors='ignore'))
    
    ssh.close()

if __name__ == '__main__':
    check_500_error()
