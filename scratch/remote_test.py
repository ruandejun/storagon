import paramiko
import logging

logging.basicConfig(level=logging.DEBUG)

def test_conn():
    hostname = "167.233.89.198"
    username = "root"
    password = "fJU9JtkbELfi"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("Starting connection...")
        ssh.connect(hostname, port=22, username=username, password=password, timeout=10)
        print("Success!")
        
        for cmd in ["rm -rf /tmp/test_clone && git clone https://github.com/ruandejun/storagon.git /tmp/test_clone"]:
            print(f"\n--- Running: {cmd} ---")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print("STDOUT:", stdout.read().decode('utf-8'))
            print("STDERR:", stderr.read().decode('utf-8'))
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    test_conn()
