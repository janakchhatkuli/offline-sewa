"""Nonce generation helper."""
import uuid


def generate_nonce() -> str:
    return uuid.uuid4().hex
