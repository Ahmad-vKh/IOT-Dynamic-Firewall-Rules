import socket
import threading
import logging
from encryption_decryption import encrypt, decrypt


class CentralServer:
    def __init__(self, host="0.0.0.0", port=9999):
        self.host = host
        self.port = port
        self.profiles = {}
        self.active_threads = []
        self.running = False
        self.lock = threading.Lock()

        # Configure logging
        logging.basicConfig(
            filename="server.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def start(self):
        """Start server with graceful shutdown handling"""
        self.running = True
        with socket.socket() as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            sock.listen(5)
            sock.settimeout(2)

            logging.info(f"Server started on {self.host}:{self.port}")
            print(f"[+] Server running on {self.host}:{self.port}\n")

            while self.running:
                try:
                    conn, addr = sock.accept()
                    print(f"[+] Connection accepted from {addr}")
                    client_thread = threading.Thread(
                        target=self.handle_client, args=(conn, addr), daemon=True
                    )
                    with self.lock:
                        self.active_threads.append(client_thread)
                    client_thread.start()

                except socket.timeout:
                    # Expected during shutdown checks
                    continue
                except Exception as e:
                    logging.error(f"Accept error: {str(e)}")
                    print(f"[!] Accept error: {e}")

        self.cleanup()

    def handle_client(self, conn, addr):
        """Thread-safe client handler with full error handling"""
        try:

            print(f"[+] Connection from {addr}")
            encrypted_data = conn.recv(4096)
            print(f"[+] Received {len(encrypted_data)} bytes")
            if not encrypted_data:
                logging.warning(f"[!] Empty data from {addr}")
                return

            try:
                data = decrypt(encrypted_data)
                print(f"[+] Edge Node Decrypted Payload: {data}\n")
                source_ip = data.get("source_ip")
                if not source_ip:
                    raise ValueError("[!] Missing source_ip in payload")

                new_profile = self.decide_profile(data)
                print(f"Profile Set to >>>>> {new_profile}\n")
                with self.lock:
                    self.profiles[source_ip] = new_profile
                    logging.info(f"Updated {source_ip} to {new_profile}")

                encrypted_res = encrypt({"profile": new_profile})
                conn.sendall(encrypted_res)  # Ensure full transmission
                print(f"{encrypted_res}")

            except Exception as e:
                logging.error(f"[!] Processing error from {addr}: {str(e)}")
                conn.sendall(encrypt({"error": str(e)}))

        except ConnectionResetError:
            logging.warning(f"Connection reset by {addr}")
        finally:
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            conn.close()
            print(f"[+] Connection with {addr} closed\n")

    def decide_profile(self, data):
        """Enhanced decision logic with validation"""
        try:
            cpu = float(data["cpu"])
            print(f"CPU: {cpu}\n")
            ram = float(data["ram"])
            print(f"RAM: {ram}\n")
            traffic = float(data["traffic"].replace("Mbps", ""))

            if cpu > 70 and ram > 50:
                return "Critical Task"
            elif cpu > 70 and ram < 50:
                return "High Activity"
            elif 30 < cpu <= 70 and ram > 50:
                return "High Activity"
            elif 30 < cpu <= 70 and ram <= 50:
                return "Low Activity"
            elif cpu < 20 and ram < 25:
                return "Idle"

            return "Low Activity"

        except KeyError as e:
            logging.error(f"[!] Missing metric: {str(e)}")
            return "Low Activity"

    def cleanup(self):
        """Graceful shutdown procedure"""
        logging.info("Initiating shutdown sequence")
        with self.lock:
            logging.info(f"Active threads: {len(self.active_threads)}")
            for t in self.active_threads:
                try:
                    if t.is_alive():
                        t.join(timeout=1)
                except Exception as e:
                    logging.error(f"Thread join error: {str(e)}")
        logging.info("Server shutdown complete")

    def stop(self):
        """External shutdown trigger"""
        self.running = False
        logging.info("Shutdown signal received")


if __name__ == "__main__":
    server = CentralServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
