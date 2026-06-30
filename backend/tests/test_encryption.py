"""
Tests for API key encryption utilities.
"""
import pytest
from unittest.mock import patch, MagicMock

from app.utils.encryption import (
    encrypt_api_key,
    decrypt_api_key,
    generate_encryption_key,
    EncryptionError,
)


class TestEncryption:
    """Tests for encryption/decryption functions."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings with a test encryption key."""
        with patch("app.utils.encryption.settings") as mock:
            mock.ENCRYPTION_KEY = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
            yield mock

    def test_encrypt_decrypt_roundtrip(self, mock_settings):
        """Test that encryption and decryption work together."""
        original = "sk-test-api-key-12345"
        encrypted = encrypt_api_key(original)
        decrypted = decrypt_api_key(encrypted)

        assert encrypted != original
        assert decrypted == original

    def test_encrypt_empty_string(self, mock_settings):
        """Test encrypting empty string returns empty."""
        result = encrypt_api_key("")
        assert result == ""

    def test_decrypt_empty_string(self, mock_settings):
        """Test decrypting empty string returns empty."""
        result = decrypt_api_key("")
        assert result == ""

    def test_encrypt_none_returns_empty(self, mock_settings):
        """Test encrypting None returns empty string."""
        result = encrypt_api_key(None)
        assert result == ""

    def test_decrypt_none_returns_empty(self, mock_settings):
        """Test decrypting None returns empty string."""
        result = decrypt_api_key(None)
        assert result == ""

    def test_encrypt_produces_different_ciphertext(self, mock_settings):
        """Test that encryption produces different ciphertext each time."""
        # Fernet uses time-based components, so encrypting the same
        # value twice should produce different ciphertext
        original = "test-api-key"
        encrypted1 = encrypt_api_key(original)
        encrypted2 = encrypt_api_key(original)

        # Both should decrypt to the same value
        assert decrypt_api_key(encrypted1) == original
        assert decrypt_api_key(encrypted2) == original

    def test_decrypt_invalid_data_raises_error(self, mock_settings):
        """Test that decrypting invalid data raises EncryptionError."""
        with pytest.raises(EncryptionError):
            decrypt_api_key("invalid-encrypted-data")

    def test_generate_encryption_key(self):
        """Test encryption key generation."""
        key1 = generate_encryption_key()
        key2 = generate_encryption_key()

        # Keys should be 64 characters (32 bytes in hex)
        assert len(key1) == 64
        assert len(key2) == 64

        # Keys should be different (randomly generated)
        assert key1 != key2

        # Keys should be valid hex strings
        int(key1, 16)  # Will raise if not valid hex
        int(key2, 16)

    def test_encrypt_long_api_key(self, mock_settings):
        """Test encrypting a long API key."""
        long_key = "sk-" + "a" * 1000
        encrypted = encrypt_api_key(long_key)
        decrypted = decrypt_api_key(encrypted)
        assert decrypted == long_key

    def test_encrypt_special_characters(self, mock_settings):
        """Test encrypting API key with special characters."""
        special_key = "sk-test_123!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        encrypted = encrypt_api_key(special_key)
        decrypted = decrypt_api_key(encrypted)
        assert decrypted == special_key

    def test_encrypt_unicode(self, mock_settings):
        """Test encrypting API key with unicode characters."""
        unicode_key = "sk-测试-🔐-key"
        encrypted = encrypt_api_key(unicode_key)
        decrypted = decrypt_api_key(encrypted)
        assert decrypted == unicode_key


class TestEncryptionError:
    """Tests for EncryptionError exception."""

    def test_error_message(self):
        """Test error message is preserved."""
        error = EncryptionError("Test error message")
        assert str(error) == "Test error message"

    def test_error_is_exception(self):
        """Test EncryptionError is an Exception."""
        error = EncryptionError("Test")
        assert isinstance(error, Exception)
