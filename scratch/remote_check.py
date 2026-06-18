import paramiko

def remote_check():
    hostname = "167.233.108.214"
    username = "root"
    password = "fJU9JtkbELfi"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {hostname}...")
        ssh.connect(hostname, username=username, password=password, timeout=10)
        print("Connected successfully!")
        
        commands = [
            "hostname",
            "cd /root/storagon && pwd && git branch && git status",
            "docker ps"
        ]
        
        for cmd in commands:
            print(f"\nRunning command: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            out = stdout.read().decode('utf-8')
            err = stderr.read().decode('utf-8')
            if out:
                print(f"STDOUT:\n{out}")
            if err:
                print(f"STDERR:\n{err}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    remote_check()
