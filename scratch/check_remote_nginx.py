import paramiko

def check_nginx():
    hostname = "167.233.89.198"
    username = "root"
    password = "fJU9JtkbELfi"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=10)
        cmd = "cat /root/storagon/docker-compose.yml"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print("--- docker-compose.yml ---")
        print(stdout.read().decode('utf-8'))
        
        cmd2 = "cd /root/storagon && find . -name 'nginx.conf'"
        stdin, stdout, stderr = ssh.exec_command(cmd2)
        print("--- nginx.conf files ---")
        print(stdout.read().decode('utf-8'))
    finally:
        ssh.close()

if __name__ == '__main__':
    check_nginx()
