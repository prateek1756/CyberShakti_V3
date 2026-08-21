"""AES-256-GCM file encryption with Argon2id password-derived keys (ADR-021)."""

from __future__ import annotations

import os
import re
from argon2.low_level import Type, hash_secret_raw
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"CSHAKTI1"
VERSION = 1
NONCE_LEN = 12
SALT_LEN = 32
TAG_LEN = 16
HEADER_LEN = 8 + 1 + NONCE_LEN + SALT_LEN  # 53

# Interim Argon2id parameters (ADR-026 — not production-locked; overridable via env later)
ARGON2_TIME_COST = 3
ARGON2_MEMORY_COST = 65536
ARGON2_PARALLELISM = 4
ARGON2_HASH_LEN = 32


class FileCryptoError(Exception):
    def __init__(self, error_code: str, message: str):
        self.error_code = error_code
        self.message = message
        super().__init__(message)


def derive_file_key(password: str, salt: bytes) -> bytes:
    if len(salt) != SALT_LEN:
        raise FileCryptoError("INVALID_ENCRYPTED_FILE", "Invalid key salt.")
    return hash_secret_raw(
        secret=password.encode("utf-8"),
        salt=salt,
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEMORY_COST,
        parallelism=ARGON2_PARALLELISM,
        hash_len=ARGON2_HASH_LEN,
        type=Type.ID,
    )


def encrypt_bytes(plaintext: bytes, password: str) -> bytes:
    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    key = derive_file_key(password, salt)
    ciphertext_with_tag = AESGCM(key).encrypt(nonce, plaintext, MAGIC)
    return MAGIC + bytes([VERSION]) + nonce + salt + ciphertext_with_tag


def decrypt_bytes(blob: bytes, password: str) -> bytes:
    if len(blob) < HEADER_LEN + TAG_LEN or not blob.startswith(MAGIC):
        raise FileCryptoError(
            "INVALID_ENCRYPTED_FILE",
            "File is not a valid CyberShakti encrypted file.",
        )
    if blob[8] != VERSION:
        raise FileCryptoError("INVALID_ENCRYPTED_FILE", "Unsupported encrypted file version.")

    nonce = blob[9:21]
    salt = blob[21:53]
    ciphertext_with_tag = blob[53:]
    key = derive_file_key(password, salt)
    try:
        return AESGCM(key).decrypt(nonce, ciphertext_with_tag, MAGIC)
    except InvalidTag as exc:
        raise FileCryptoError(
            "WRONG_PASSWORD",
            "Decryption failed. The password is incorrect or the file has been tampered with.",
        ) from exc


def safe_download_filename(name: str | None, fallback: str) -> str:
    raw = (name or fallback).replace("\\", "/").split("/")[-1]
    raw = raw.replace('"', "").replace("'", "").replace(":", "_")
    raw = re.sub(r"[\r\n\x00]", "", raw)
    raw = re.sub(r"[^\w.\- ()]", "_", raw)
    return raw[:180] or fallback
