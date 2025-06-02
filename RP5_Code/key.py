import os
# 1. Generate a 16-byte (128-bit) key
key = os.urandom(32)  # Use 32 bytes if using HKDF input
hex_key = key.hex()

# 2. Save it in key.conf (in hexadecimal format)
with open("key.conf", "w") as f:
    f.write(f"ASCON_KEY={hex_key}\n")

print(f"Generated Key (in HEX): {hex_key}")
