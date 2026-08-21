from app.shared.file_crypto import FileCryptoError, decrypt_bytes, encrypt_bytes, safe_download_filename


def test_aes_gcm_roundtrip():
    plaintext = b"classified-document-bytes"
    blob = encrypt_bytes(plaintext, "Secret123!")
    assert blob.startswith(b"CSHAKTI1")
    assert decrypt_bytes(blob, "Secret123!") == plaintext


def test_decrypt_wrong_password():
    blob = encrypt_bytes(b"payload", "Secret123!")
    try:
        decrypt_bytes(blob, "WrongPass")
        assert False, "expected FileCryptoError"
    except FileCryptoError as exc:
        assert exc.error_code == "WRONG_PASSWORD"


def test_decrypt_tampered_ciphertext():
    blob = bytearray(encrypt_bytes(b"payload", "Secret123!"))
    blob[-5] ^= 0xFF
    try:
        decrypt_bytes(bytes(blob), "Secret123!")
        assert False, "expected FileCryptoError"
    except FileCryptoError as exc:
        assert exc.error_code == "WRONG_PASSWORD"


def test_safe_download_filename_strips_header_injection():
    name = safe_download_filename('evil\r\nX-Injected: yes.pdf', "file")
    assert "\r" not in name
    assert "\n" not in name
    assert ":" not in name
