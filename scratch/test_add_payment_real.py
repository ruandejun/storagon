import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

def test_add_payment():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('167.233.89.198', username='root', password='fJU9JtkbELfi')
    
    python_cmd = (
        "import sys, logging; "
        "logging.basicConfig(level=logging.INFO); "
        "from dashboard.apple_auth import AppleAuthClient, AppleStoreClient; "
        "auth = AppleAuthClient(); "
        "res1 = auth.login('tuan.storagon@gmail.com', 'Goldcoast123!@#'); "
        "print('LOGIN:', res1); "
        "res2 = auth.verify_2fa('tuan.storagon@gmail.com', 'Goldcoast123!@#', '209191'); "
        "print('VERIFY 2FA:', res2); "
        "store = AppleStoreClient(auth); "
        "res3 = store.add_payment_method('4242424242424242', '12', '2028', '123', 'Tuan', 'Nguyen'); "
        "print('ADD PAYMENT RESULT:', res3)"
    )
    
    cmd = f'cd /root/storagon && docker compose exec -T storagon python -c "{python_cmd}"'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print("STDOUT:\n", stdout.read().decode('utf-8', errors='ignore'))
    print("STDERR:\n", stderr.read().decode('utf-8', errors='ignore'))
    ssh.close()

if __name__ == '__main__':
    test_add_payment()
