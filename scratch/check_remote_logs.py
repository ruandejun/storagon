import paramiko

def check():
    hostname = "167.233.89.198"
    username = "root"
    password = "fJU9JtkbELfi"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=10)
        print("Connected!")
        
        cmds = [
            "cd /root/storagon && docker compose logs --tail=50 storagon",
            "cd /root/storagon && docker compose logs --tail=50 nginx"
        ]
        for cmd in cmds:
            print(f"\n--- {cmd} ---")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print("STDOUT:", stdout.read().decode('utf-8', errors='ignore'))
            print("STDERR:", stderr.read().decode('utf-8', errors='ignore'))
    except Exception as e:
        print("Error:", e)
    finally:
        ssh.close()

if __name__ == "__main__":
    check()
