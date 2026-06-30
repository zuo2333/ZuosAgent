"""
API Key encryption utilities using Fernet symmetric encryption.
Provides secure storage for sensitive API keys in the database.
"""
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings


class EncryptionError(Exception):
    """Exception raised for encryption/decryption errors."""
    pass


def _get_fernet_key() -> bytes:
    """
    Derive a Fernet-compatible key from the encryption key in settings.

    Fernet requires a 32-byte URL-safe base64-encoded key.
    We use PBKDF2 to derive a key from the configured encryption key.
    """
    encryption_key = settings.ENCRYPTION_KEY

    # Use a fixed salt for deterministic key derivation
    # In production, consider storing the salt alongside encrypted data
    salt = b'llm-chat-encryption-salt-v1'

    # Derive a 32-byte key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )

    key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
    return key


def _get_fernet() -> Fernet:
    """Get a Fernet instance with the derived key."""
    key = _get_fernet_key()
    return Fernet(key)


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key for secure storage.

    Args:
        api_key: The plaintext API key to encrypt.

    Returns:
        The encrypted API key as a string.

    Raises:
        EncryptionError: If encryption fails.
    """
    if not api_key:
        return ""

    try:
        fernet = _get_fernet()
        encrypted = fernet.encrypt(api_key.encode())
        return encrypted.decode()
    except Exception as e:
        raise EncryptionError(f"Failed to encrypt API key: {str(e)}")


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Decrypt an encrypted API key.

    Args:
        encrypted_key: The encrypted API key string.

    Returns:
        The decrypted plaintext API key.

    Raises:
        EncryptionError: If decryption fails.
    """
    if not encrypted_key:
        return ""

    try:
        fernet = _get_fernet()
        decrypted = fernet.decrypt(encrypted_key.encode())
        return decrypted.decode()
    except Exception as e:
        raise EncryptionError(f"Failed to decrypt API key: {str(e)}")


def generate_encryption_key() -> str:
    """
    Generate a new encryption key for use in configuration.

    This should be used once during initial setup to generate
    a secure random key for ENCRYPTION_KEY in settings.

    Returns:
        A 64-character hex string (32 bytes) suitable for ENCRYPTION_KEY.
    """
    return os.urandom(32).hex()


if __name__ == "__main__":
    # Example usage and key generation
    print("Generated encryption key (add to .env as ENCRYPTION_KEY):")
    print(generate_encryption_key())

    # Test encryption/decryption
    test_key = "sk-test-api-key-12345"
    encrypted = encrypt_api_key(test_key)
    decrypted = decrypt_api_key(encrypted)
    print(f"\nTest encryption:")
    print(f"Original: {test_key}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {test_key == decrypted}")
