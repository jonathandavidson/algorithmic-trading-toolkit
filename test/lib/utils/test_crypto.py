import pytest

from lib.utils.crypto import decrypt_secret, encrypt_secret


@pytest.fixture(autouse=True)
def hdc_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HDC_SECRET", "test-secret-value")


def test_encrypt_returns_different_value():
    assert encrypt_secret("mysecret") != "mysecret"


def test_decrypt_roundtrips():
    plaintext = "mysecret"
    assert decrypt_secret(encrypt_secret(plaintext)) == plaintext


def test_different_encryptions_of_same_value_differ():
    # Fernet uses a random IV so two encryptions of the same value differ
    assert encrypt_secret("mysecret") != encrypt_secret("mysecret")


def test_encrypt_raises_without_hdc_secret(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("HDC_SECRET")
    with pytest.raises(ValueError, match="HDC_SECRET"):
        encrypt_secret("mysecret")


def test_decrypt_raises_without_hdc_secret(monkeypatch: pytest.MonkeyPatch):
    ciphertext = encrypt_secret("mysecret")
    monkeypatch.delenv("HDC_SECRET")
    with pytest.raises(ValueError, match="HDC_SECRET"):
        decrypt_secret(ciphertext)


def test_decrypt_raises_with_wrong_key(monkeypatch: pytest.MonkeyPatch):
    from cryptography.fernet import InvalidToken
    ciphertext = encrypt_secret("mysecret")
    monkeypatch.setenv("HDC_SECRET", "wrong-secret")
    with pytest.raises(InvalidToken):
        decrypt_secret(ciphertext)
