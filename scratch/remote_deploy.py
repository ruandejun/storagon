import paramiko
import sys

# Ensure UTF-8 output encoding to handle Vietnamese characters in git logs/errors
sys.stdout.reconfigure(encoding='utf-8')

def deploy():
    hostname = "167.233.89.198"
    username = "root"
    password = "fJU9JtkbELfi"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {hostname}...")
        ssh.connect(hostname, username=username, password=password, timeout=15)
        print("Connected successfully!")
        
        # Helper to execute command and print results
        def run_cmd(cmd):
            print(f"\n>>> Running: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            # wait for command to finish
            exit_status = stdout.channel.recv_exit_status()
            out = stdout.read().decode('utf-8')
            err = stderr.read().decode('utf-8')
            if out:
                print(f"STDOUT:\n{out}")
            if err:
                print(f"STDERR:\n{err}")
            print(f"Exit Status: {exit_status}")
            return exit_status == 0
            
        # 1. Initialize Git in the remote directory
        print("\n--- Initializing Git on remote server ---")
        run_cmd("cd /root/storagon && git init")
        run_cmd("cd /root/storagon && git remote remove origin")
        run_cmd("cd /root/storagon && git remote add origin https://github.com/ruandejun/storagon.git")
        
        # 2. Fetch and checkout main branch
        print("\n--- Pulling latest code changes ---")
        if not run_cmd("cd /root/storagon && git fetch origin"):
            print("Error: Git fetch failed")
            return
            
        if not run_cmd("cd /root/storagon && git checkout -f main"):
            # If main branch doesn't exist locally, create it tracking remote
            run_cmd("cd /root/storagon && git checkout -b main --track origin/main")
            
        if not run_cmd("cd /root/storagon && git reset --hard origin/main"):
            print("Error: Git reset failed")
            return
            
        # 2A. Check and download GeoIP databases
        print("\n--- Checking and downloading GeoIP databases ---")
        run_cmd("test -f /root/storagon/GeoLite2-City.mmdb || wget -O /root/storagon/GeoLite2-City.mmdb https://raw.githubusercontent.com/P3TERX/GeoLite.mmdb/download/GeoLite2-City.mmdb")
        run_cmd("test -f /root/storagon/GeoLite2-ASN.mmdb || wget -O /root/storagon/GeoLite2-ASN.mmdb https://raw.githubusercontent.com/P3TERX/GeoLite.mmdb/download/GeoLite2-ASN.mmdb")
            
        # 2B. Pull latest frontend code changes
        print("\n--- Pulling latest frontend code changes ---")
        run_cmd("mkdir -p /root/c69-frontend")
        run_cmd("cd /root/c69-frontend && git init")
        # Ignore warning/errors from remote remove if it doesn't exist
        run_cmd("cd /root/c69-frontend && git remote remove origin")
        run_cmd("cd /root/c69-frontend && git remote add origin https://github.com/ruandejun/fitviet-frontend.git")
        if not run_cmd("cd /root/c69-frontend && git fetch origin"):
            print("Error: Frontend Git fetch failed")
            return
        if not run_cmd("cd /root/c69-frontend && git checkout -f main"):
            run_cmd("cd /root/c69-frontend && git checkout -b main --track origin/main")
        if not run_cmd("cd /root/c69-frontend && git reset --hard origin/main"):
            print("Error: Frontend Git reset failed")
            return
            
        # 3. Stop containers
        print("\n--- Shutting down active docker compose stack ---")
        run_cmd("cd /root/storagon && docker compose down")
        
        # 4. Rebuild and start containers (clears memcached and redis automatically)
        print("\n--- Building and starting container stack ---")
        run_cmd("cd /root/storagon && docker compose build --no-cache frontend")
        if not run_cmd("cd /root/storagon && docker compose up --build -d"):
            print("Error: docker compose up --build failed")
            return
            
        # 5. Run database migrations inside the storagon container
        print("\n--- Running Django database migrations ---")
        run_cmd("cd /root/storagon && docker compose exec -T storagon python manage.py makemigrations")
        run_cmd("cd /root/storagon && docker compose exec -T storagon python manage.py migrate")
        
        # 6. Verify running containers status
        print("\n--- Verifying container status ---")
        run_cmd("cd /root/storagon && docker compose ps")
        
        print("\nDEPLOYMENT AND CACHE RESET COMPLETED SUCCESSFULLY! [Done]")
        
    except Exception as e:
        print(f"Error during deployment: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()
