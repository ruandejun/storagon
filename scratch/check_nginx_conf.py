import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

def check_nginx_conf():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('167.233.89.198', username='root', password='fJU9JtkbELfi')
    
    cmd = 'cat /root/storagon/storagon/nginx/nginx.conf'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print("NGINX CONF:\n", stdout.read().decode('utf-8', errors='ignore'))
    
    cmd2 = 'cat /root/storagon/storagon/nginx/Dockerfile'
    stdin, stdout, stderr = ssh.exec_command(cmd2)
    print("NGINX DOCKERFILE:\n", stdout.read().decode('utf-8', errors='ignore'))
    
    cmd3 = 'cat /root/fitviet-frontend/Dockerfile'
    stdin, stdout, stderr = ssh.exec_command(cmd3)
    print("FRONTEND DOCKERFILE:\n", stdout.read().decode('utf-8', errors='ignore'))
    
    ssh.close()

if __name__ == '__main__':
    check_nginx_conf()
