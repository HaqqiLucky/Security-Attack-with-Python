# cara run
# sudo python3 ssh_scanner.py -t 192.168.1.0/24 -w 200

# ssh_scanner.py
import socket
import argparse
import ipaddress
import paramiko
from concurrent.futures import ThreadPoolExecutor, as_completed

# Matikan logging paramiko yang terlalu "berisik"
paramiko.util.log_to_file('/dev/null')

def check_ssh_port(ip, port=22, timeout=1):
    """Mencoba terhubung ke port SSH dan mengembalikan IP jika terbuka."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((str(ip), port))
            return ip
    except (socket.timeout, ConnectionRefusedError):
        return None
    except Exception:
        return None

def get_ssh_details(ip, port=22):
    """Mengambil banner SSH dan metode autentikasi yang diizinkan."""
    banner = "Tidak dapat mengambil banner."
    auth_methods = "Tidak diketahui."
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((str(ip), port))
        
        transport = paramiko.Transport(sock)
        transport.start_client(timeout=2)
        banner = transport.get_remote_server_banner()
        
        try:
            transport.auth_none(username="nonexistentuser")
        except paramiko.AuthenticationException as e:
            auth_methods = ", ".join(e.allowed_types)
        
        transport.close()
        
    except Exception:
        pass
        
    return banner, auth_methods


def main():
    parser = argparse.ArgumentParser(description="Python SSH Scanner - Discovery & Fingerprinting")
    parser.add_argument("-t", "--target", required=True, help="Target IP atau subnet (contoh: 192.168.1.55 atau 192.168.1.0/24)")
    parser.add_argument("-p", "--port", type=int, default=22, help="Port SSH target (default: 22)")
    parser.add_argument("-w", "--workers", type=int, default=100, help="Jumlah threads/pekerja untuk scanning (default: 100)")
    parser.add_argument("--timeout", type=float, default=0.5, help="Timeout koneksi dalam detik (default: 0.5)")

    args = parser.parse_args()

    try:
        target_network = ipaddress.ip_network(args.target, strict=False)
        all_hosts = list(target_network.hosts())
        if not all_hosts:
             all_hosts = [target_network.network_address]
        print(f"[*] Target: {args.target} ({len(all_hosts)} host)")
    except ValueError:
        print(f"[!] Format target salah: {args.target}")
        return

    print(f"[*] Memindai port {args.port} dengan {args.workers} workers...")
    
    live_hosts = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_ip = {executor.submit(check_ssh_port, ip, args.port, args.timeout): ip for ip in all_hosts}
        for future in as_completed(future_to_ip):
            result = future.result()
            if result:
                print(f"[+] Host ditemukan: {result}")
                live_hosts.append(result)

    if not live_hosts:
        print("\n[*] Tidak ada host dengan port SSH terbuka yang ditemukan.")
        return

    print(f"\n[*] Selesai memindai. Ditemukan {len(live_hosts)} host. Memulai fingerprinting...")
    print("-" * 60)
    print(f"{'Alamat IP':<18} | {'Versi SSH (Banner)':<45} | {'Metode Autentikasi Diizinkan'}")
    print("-" * 60)

    for ip in sorted(live_hosts, key=lambda ip: ip.packed):
        banner, auth_methods = get_ssh_details(ip, args.port)
        banner_clean = banner.strip() if banner else "N/A"
        print(f"{str(ip):<18} | {banner_clean:<45} | {auth_methods}")

    print("-" * 60)
    print("[*] Scanning selesai.")


if __name__ == "__main__":
    main()