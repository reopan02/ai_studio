from __future__ import annotations

import hashlib
import hmac
import shutil
import subprocess
import os
from dataclasses import dataclass
from secrets import token_bytes

from app.config import get_settings


class EncryptionError(RuntimeError):
    pass


_MAGIC = b"EV1"  # Encrypted Value v1
_IV_LEN = 16
_TAG_LEN = 32  # HMAC-SHA256
_KEY_LEN = 32  # AES-256


@dataclass(frozen=True)
class DerivedKeys:
    enc_key: bytes
    mac_key: bytes


def _get_master_key() -> bytes:
    settings = get_settings()
    if not settings.STORAGE_MASTER_KEY:
        raise EncryptionError("STORAGE_MASTER_KEY is required for encrypted storage")
    return settings.STORAGE_MASTER_KEY.encode("utf-8")


def _derive_keys(user_id: str) -> DerivedKeys:
    master_key = _get_master_key()
    uid = str(user_id).encode("utf-8")
    enc_key = hmac.new(master_key, b"enc:" + uid, hashlib.sha256).digest()
    mac_key = hmac.new(master_key, b"mac:" + uid, hashlib.sha256).digest()
    return DerivedKeys(enc_key=enc_key[:_KEY_LEN], mac_key=mac_key[:_KEY_LEN])


def _get_openssl_path() -> str:
    # Try finding in PATH
    path = shutil.which("openssl")
    if path:
        return path
    
    # Fallback to common locations per OS
    if os.name == "nt":
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        common_paths = [
            os.path.join(program_files, "Git", "usr", "bin", "openssl.exe"),
            os.path.join(program_files_x86, "Git", "usr", "bin", "openssl.exe"),
            os.path.join(program_files, "OpenSSL-Win64", "bin", "openssl.exe"),
            os.path.join(program_files_x86, "OpenSSL-Win32", "bin", "openssl.exe"),
            r"C:\OpenSSL-Win64\bin\openssl.exe",
            r"C:\OpenSSL-Win32\bin\openssl.exe",
        ]
    else:
        common_paths = [
            "/opt/homebrew/bin/openssl",
            "/usr/local/bin/openssl",
            "/usr/bin/openssl",
            "/bin/openssl",
        ]
    for p in common_paths:
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p
            
    raise EncryptionError("OpenSSL binary not found in PATH or common locations")


def _openssl_enc_aes_256_cbc(*, key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    if len(key) != _KEY_LEN:
        raise EncryptionError("Invalid encryption key length")
    if len(iv) != _IV_LEN:
        raise EncryptionError("Invalid IV length")

    openssl_bin = _get_openssl_path()
    
    try:
        proc = subprocess.run(
            [openssl_bin, "enc", "-aes-256-cbc", "-K", key.hex(), "-iv", iv.hex()],
            input=plaintext,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        raise EncryptionError(f"OpenSSL binary not found at {openssl_bin}")
    except Exception as e:
        raise EncryptionError(f"Failed to execute OpenSSL: {str(e)}")

    if proc.returncode != 0:
        raise EncryptionError(proc.stderr.decode("utf-8", errors="replace").strip() or "OpenSSL encryption failed")
    return proc.stdout


def _openssl_dec_aes_256_cbc(*, key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    if len(key) != _KEY_LEN:
        raise EncryptionError("Invalid encryption key length")
    if len(iv) != _IV_LEN:
        raise EncryptionError("Invalid IV length")

    openssl_bin = _get_openssl_path()

    try:
        proc = subprocess.run(
            [openssl_bin, "enc", "-d", "-aes-256-cbc", "-K", key.hex(), "-iv", iv.hex()],
            input=ciphertext,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        raise EncryptionError(f"OpenSSL binary not found at {openssl_bin}")
    except Exception as e:
        raise EncryptionError(f"Failed to execute OpenSSL: {str(e)}")

    if proc.returncode != 0:
        raise EncryptionError(proc.stderr.decode("utf-8", errors="replace").strip() or "OpenSSL decryption failed")
    return proc.stdout


def encrypt_for_user(*, user_id: str, plaintext: bytes) -> bytes:
    keys = _derive_keys(user_id)
    iv = token_bytes(_IV_LEN)
    ciphertext = _openssl_enc_aes_256_cbc(key=keys.enc_key, iv=iv, plaintext=plaintext)
    tag = hmac.new(keys.mac_key, iv + ciphertext, hashlib.sha256).digest()
    return _MAGIC + iv + ciphertext + tag


def decrypt_for_user(*, user_id: str, blob: bytes) -> bytes:
    if not blob or len(blob) < len(_MAGIC) + _IV_LEN + _TAG_LEN:
        raise EncryptionError("Invalid encrypted payload")
    if not blob.startswith(_MAGIC):
        raise EncryptionError("Unsupported encrypted payload")

    iv_start = len(_MAGIC)
    ct_start = iv_start + _IV_LEN
    tag_start = len(blob) - _TAG_LEN
    iv = blob[iv_start:ct_start]
    ciphertext = blob[ct_start:tag_start]
    tag = blob[tag_start:]

    keys = _derive_keys(user_id)
    plaintext = _openssl_dec_aes_256_cbc(key=keys.enc_key, iv=iv, ciphertext=ciphertext)
    
    # Verify HMAC
    expected_tag = hmac.new(keys.mac_key, iv + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, expected_tag):
        raise EncryptionError("Integrity check failed (HMAC mismatch)")
        
    return plaintext
