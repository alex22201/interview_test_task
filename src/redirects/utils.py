import secrets
import string

_ALPHABET = string.ascii_letters + string.digits
_IDENTIFIER_LENGTH = 8


def generate_redirect_identifier() -> str:
    """Generate a short random base62-style identifier for a redirect rule."""
    return "".join(secrets.choice(_ALPHABET) for _ in range(_IDENTIFIER_LENGTH))
