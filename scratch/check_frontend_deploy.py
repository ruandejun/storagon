import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

def check_remote_frontend():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('167.233.89.198', username='root', password='fJU9JtkbELfi')
    
    cmd = 'cat /root/storagon/docker-compose.yml'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print("DOCKER COMPOSE:\n", stdout.read().decode('utf-8', errors='ignore'))
    
    cmd2 = 'cd /root/fitviet-frontend && git log -n 3 --oneline'
    stdin, stdout, stderr = ssh.exec_command(cmd2)
    print("REMOTE FRONTEND GIT LOG:\n", stdout.read().decode('utf-8', errors='ignore'))
    
    ssh.close()

if __name__ == '__main__':
    check_remote_frontend()
