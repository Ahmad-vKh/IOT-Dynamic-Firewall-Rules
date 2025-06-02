import os
import json
import ascon
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

# Global encryption key
_encryption_key = None


def _initialize_key():
    global _encryption_key
    if _encryption_key is not None:
        return

    try:
        with open("key.conf", "r") as f:
            key_line = f.read().strip()
            hex_key = key_line.split("=")[1]
            print(f"[+] hex_key is ready == {hex_key}\n")

            if len(hex_key) != 64:
                raise ValueError("Key must be 64 hex chars (32 bytes)")

            master_key = bytes.fromhex(hex_key)

            # Derive 16-byte key using HKDF
            _encryption_key = HKDF(
                algorithm=hashes.SHA256(),
                length=16,
                salt=None,
                info=b"ascon-encryption",
            ).derive(master_key)

    except FileNotFoundError:
        raise RuntimeError("Missing key.conf file")
    except Exception as e:
        raise RuntimeError(f"Key error: {str(e)}")


def encrypt(data):
    """Encrypt data (dict/str) with ASCON AEAD"""
    _initialize_key()
    print("start of encryption function\n")
    print("[+] _initialize_key() is ready\n")

    print("payload before encryption")
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True, separators=(",", ":"))
    print(f"[+] data =={data} --> ciphertext\n")
    print("payload after encryption")
    nonce = os.urandom(16)
    ciphertext = ascon.ascon_encrypt(
        key=_encryption_key,
        nonce=nonce,
        associateddata=b"",
        plaintext=data.encode(),
        variant="Ascon-AEAD128",
    )
    print(f"[+] --> nonce + ciphertext == {(nonce + ciphertext).hex()}\n")
    print("#" * 5)
    return nonce + ciphertext


def decrypt(encrypted_data):
    """Decrypt and verify ASCON AEAD data"""
    _initialize_key()
    print("start of decryption function\n")
    print("[+] _initialize_key() is ready\n")
    try:
        nonce = encrypted_data[:16]
        ciphertext_with_tag = encrypted_data[16:]
        print("payload before decryption\n")
        print(
            f"[+] --> nonce + ciphertext_with_tag == {(nonce + ciphertext_with_tag).hex()}\n"
        )
        plaintext = ascon.ascon_decrypt(
            key=_encryption_key,
            nonce=nonce,
            associateddata=b"",
            ciphertext=ciphertext_with_tag,
            variant="Ascon-AEAD128",
        )
        print("payload after decryption\n")
        print(f"[+] --> plaintext == {plaintext.hex()}\n")

        try:
            return json.loads(plaintext.decode())
        except json.JSONDecodeError:
            return plaintext.decode()

    except Exception as e:
        print(f"Decryption failed: {str(e)}")
        return None


if __name__ == "__main__":
    # Quick test
    test_data = {"status": "secure", "value": 42}
    encrypted = encrypt(test_data)
    decrypted = decrypt(encrypted)
    print(f"Test: {test_data} ? Encrypted ? {decrypted}")
