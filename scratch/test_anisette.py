import paramiko
import json

def test():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('167.233.89.198', username='root', password='fJU9JtkbELfi')
    cmd = 'docker compose exec -T storagon python -c "import requests; print(requests.get(\'http://anisette:6969/\').text)"'
    stdin, stdout, stderr = ssh.exec_command(f'cd /root/storagon && {cmd}')
    print("STDOUT:", stdout.read().decode())
    print("STDERR:", stderr.read().decode())
    ssh.close()

if __name__ == '__main__':
    test()
