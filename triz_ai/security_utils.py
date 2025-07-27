"""Security utilities for encryption and signing.

To satisfy the cyber‑security requirements outlined in the technical
specification (see section 2.6 and F5), this module provides simple
functions for encrypting and decrypting data with a password and for
generating and verifying a digital signature.  The implementation uses
standard Python libraries so as not to depend on external packages.

The encryption scheme implemented here is deliberately basic – a
password‑derived key is used to XOR the plaintext and a SHA256 HMAC is
computed for signing.  While this does not provide the full security of
AES‑256 and PKI signatures, it serves as a placeholder that can be
replaced with a proper cryptographic library (e.g., `cryptography` or
PyCrypto) in a production environment.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from typing import Tuple


def _derive_key(password: str, length: int = 32) -> bytes:
    """Derive a pseudo‑random key from a password using SHA256.

    Parameters
    ----------
    password : str
        Password provided by the user.
    length : int, optional
        Length of the derived key in bytes.  Default is 32 bytes
        (suitable for AES‑256 key length).

    Returns
    -------
    bytes
        Derived key of specified length.
    """
    # Use SHA256 digest of password as base and repeat/truncate to length
    digest = hashlib.sha256(password.encode('utf-8')).digest()
    if length <= len(digest):
        return digest[:length]
    out = bytearray()
    while len(out) < length:
        out.extend(digest)
    return bytes(out[:length])


def encrypt_and_sign(data: bytes, password: str) -> Tuple[bytes, bytes]:
    """Encrypt data with a password and produce a signature.

    The encryption algorithm is a simple XOR stream cipher using a
    password‑derived key.  A HMAC‑SHA256 signature of the ciphertext is
    computed using the same key.  Both ciphertext and signature are
    returned.

    Parameters
    ----------
    data : bytes
        Raw bytes to be encrypted.
    password : str
        Password supplied by the user.

    Returns
    -------
    (bytes, bytes)
        A tuple containing the encrypted data and the signature.
    """
    key = _derive_key(password, length=max(32, len(data)))
    # XOR encryption
    encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    # HMAC signature
    signature = hmac.new(key[:32], encrypted, hashlib.sha256).digest()
    return encrypted, signature


def decrypt_and_verify(encrypted: bytes, signature: bytes, password: str) -> bytes:
    """Decrypt data previously encrypted with :func:`encrypt_and_sign`.

    The signature is verified before decryption.  If verification fails
    a :class:`ValueError` is raised.

    Parameters
    ----------
    encrypted : bytes
        The ciphertext to decrypt.
    signature : bytes
        HMAC signature of the ciphertext.
    password : str
        Password used for decryption.

    Returns
    -------
    bytes
        The decrypted plaintext.

    Raises
    ------
    ValueError
        If the signature verification fails.
    """
    key = _derive_key(password, length=max(32, len(encrypted)))
    expected_sig = hmac.new(key[:32], encrypted, hashlib.sha256).digest()
    if not hmac.compare_digest(expected_sig, signature):
        raise ValueError("Signature verification failed")
    # XOR decryption (same as encryption)
    decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(encrypted))
    return decrypted