import time
import socket
import multiprocessing
from crypto import encrypt, decrypt
from client_data_cpu import main as cpu_main
from ram import main as ram_main
import subprocess

# Make sure chmod +x firewall.sh
FIREWALL_SCRIPT = "./firewall.sh"
RP5_IP = "192.168.30.114"

hostname = socket.gethostname()
print(f"({hostname}): Started ")


def send_data_to_server(payload, binary_data, host=RP5_IP, port=9999):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

            print(f"({hostname}): Socket is open")
            sock.connect((host, port))

            print(f"({hostname}): Connection is established")
            source_ip, source_port = sock.getsockname()
            print(f"source_ip = {source_ip} ,source_port = {source_port}\n")
            # Encrypt and send the .json payload
            payload["source_ip"] = source_ip
            payload["source_port"] = source_port
            encrypted_payload = encrypt(payload)
            sock.sendall(encrypted_payload)

            print(f"({hostname}): Payload sent")

            # Encrypt and send the binary data (simulating traffic)
            encrypted_binary = encrypt(binary_data)
            sock.sendall(encrypted_binary)

            print(f"({hostname}): Sent binary data (simulated traffic): {binary_data}")

            # Receive and decrypt the server response
            encrypted_response = sock.recv(4096)
            if encrypted_response:
                response = decrypt(encrypted_response)
                print(f"({hostname}): Received from server: {response}")
                return response
            else:
                print(f"({hostname}): No response received from server")
                return None
            print("#" * 5)
    except Exception as e:
        print(f"({hostname}): Error in communication: {str(e)}")
        return None


def client_loop(period_T=10):
    cpu_queue = multiprocessing.Queue()
    data_queue = multiprocessing.Queue()
    ram_queue = multiprocessing.Queue()
    current_profile = "Low Activity"  # Initial profile

    while True:
        print("\n")
        print("-" * 40)
        print(f"({hostname}): Setting time to {period_T}")
        current_date = time.strftime("%Y-%m-%d")
        current_time = time.strftime("%H-%M-%S")
        print(f"({hostname}): [Date : {current_date}] | [Time : {current_time}]")
        start_time = time.time()

        # Run CPU and data generation
        cpu_process = multiprocessing.Process(
            target=cpu_main, args=(period_T, cpu_queue, data_queue)
        )
        cpu_process.start()

        # Run RAM monitoring
        ram_process = multiprocessing.Process(
            target=ram_main, args=(period_T, ram_queue)
        )
        ram_process.start()

        # Wait for both to complete
        cpu_process.join()
        ram_process.join()

        # Retrieve data
        cpu_usage = cpu_queue.get()
        binary_data = data_queue.get()
        ram_usage = ram_queue.get()
        binary_size_bytes = len(binary_data)

        bits_per_second = (binary_size_bytes * 8) / period_T
        mbps = round(bits_per_second / 1_000_000, 2)

        payload = {}
        # Construct the .json payload with mock traffic
        payload["cpu"] = cpu_usage
        payload["ram"] = ram_usage
        payload["traffic"] = f"{mbps}Mbps"
        payload["current_profile"] = current_profile

        # Send data and get server response
        response = send_data_to_server(payload, binary_data)

        # Update current_profile based on server response
        print(f"({hostname}): Starting the phase of decision\n")
        print(f"received response:{response}")
        if response and isinstance(response, dict):
            if "profile" in response:
                new_profile = response["profile"]
                if new_profile != current_profile:  # Only apply if profile changes
                    current_profile = new_profile
                    print(
                        f"({hostname}): Updated current_profile to: {current_profile}"
                    )
                    # Trigger the firewall script
                    if apply_firewall_profile(current_profile):
                        print(
                            f"({hostname}): Firewall profile '{current_profile}' applied successfully"
                        )
                    else:
                        print(
                            f"({hostname}): Failed to apply firewall profile '{current_profile}'"
                        )
            elif "error" in response:
                print(f"({hostname}): Server error: {response['error']}")
        # Ensure the loop runs every period_T
        elapsed_time = time.time() - start_time
        if elapsed_time < period_T:
            time.sleep(period_T - elapsed_time)


def apply_firewall_profile(profile):
    """Trigger the firewall.sh script with the specified profile."""
    # Map profile names to Bash script arguments
    profile_map = {
        "Idle": "idle",
        "Low Activity": "low",
        "High Activity": "high",
        "Critical Task": "critical",
    }

    if profile not in profile_map:
        print(f"({hostname}): Error: Unknown profile '{profile}'")
        return False

    script_arg = profile_map[profile]
    try:
        # Run the Bash script with sudo (nftables requires root)
        result = subprocess.run(
            ["sudo", FIREWALL_SCRIPT, script_arg],
            check=True,  # Raise an error if the command fails
            capture_output=True,  # Capture stdout/stderr
            text=True,  # Return output as strings
        )
        print(
            f"({hostname}): Successfully applied firewall profile '{profile}': {result.stdout}"
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"({hostname}): Error applying firewall profile '{profile}': {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"({hostname}): Error: {FIREWALL_SCRIPT} not found or not executable")
        return False


if __name__ == "__main__":
    client_loop(period_T=10)
