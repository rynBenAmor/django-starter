import datetime
import secrets
import string
import re

from django.utils.text import slugify
from django.contrib.auth.hashers import identify_hasher
# * ==========================================================
# * String & miscellaneous Utilities
# * ==========================================================


def mask_email(email: str) -> str:
    """
    Masks an email address for privacy, keeping only the first character of the username
    and the full domain.

    Args:
        email (str): The email address to mask.

    Returns:
        str: Masked email.

    Example:
        >>> mask_email("johndoe@example.com")
        'j*****@example.com'
    """
    if not email or "@" not in email:
        return email
    name, domain = email.split("@", 1)
    if len(name) <= 1:
        return "*" + "@" + domain
    return name[0] + "*" * (len(name) - 1) + "@" + domain


def mask_string(s: str, visible_start: int = 2, visible_end: int = 2, mask_char: str = "*") -> str:
    """
    Masks the middle part of a string (e.g., for phone numbers or emails).

    Args:
        s (str): The string to be masked.
        visible_start (int): Number of characters to leave visible at the start.
        visible_end (int): Number of characters to leave visible at the end.
        mask_char (str): Character to use for masking.

    Returns:
        str: The masked string.

    Example:
        mask_string("1234567890") -> "12******90"
    """
    try:
        if not isinstance(s, str) or len(s) < visible_start + visible_end:
            return s  # not enough length to mask

        return (
            s[:visible_start]
            + (mask_char * (len(s) - visible_start - visible_end))
            + s[-visible_end:]
        )
    except Exception:
        return s  # fallback if something weird happens


def humanize_timedelta(dt):
    """
    Returns a human-readable string for a timedelta or seconds.
    """
    if isinstance(dt, (int, float)):
        dt = datetime.timedelta(seconds=dt)
    seconds = int(dt.total_seconds())
    periods = [
        ("year", 60 * 60 * 24 * 365),
        ("month", 60 * 60 * 24 * 30),
        ("day", 60 * 60 * 24),
        ("hour", 60 * 60),
        ("minute", 60),
        ("second", 1),
    ]
    strings = []
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            strings.append(
                f"{period_value} {period_name}{'s' if period_value > 1 else ''}"
            )
    return ", ".join(strings) or "0 seconds"


def random_string(length=12, chars=string.ascii_letters + string.digits):
    """
    Generates a random string of given length.
    """
    # Use secrets.choice for cryptographic randomness when generating tokens
    return "".join(secrets.choice(chars) for _ in range(length))


def unique_slugify(instance, value, slug_field_name="slug"):
    """
    Generates a unique slug for a model instance.
    """
    slug = slugify(value)
    ModelClass = instance.__class__
    unique_slug = slug
    num = 1
    while (
        ModelClass.objects.filter(**{slug_field_name: unique_slug})
        .exclude(pk=instance.pk)
        .exists()
    ):
        unique_slug = f"{slug}-{num}"
        num += 1
    setattr(instance, slug_field_name, unique_slug)
    return unique_slug




def secure_random_code(length: int = 6, digits_only: bool = True) -> str:
    """Return a cryptographically secure random code.

    Uses the `secrets` module and is suitable for 2FA codes or short tokens.
    """
    if digits_only:
        alphabet = '0123456789'
    else:
        alphabet = string.digits + string.ascii_letters
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def raw_text(value: str) -> str:
    """
    Clean a text string by removing emojis, newlines, and non-alphanumeric/punctuation characters.

    Args:
        value (str): The input text.

    Returns:
        str: A cleaned string containing only letters, digits, punctuation, and spaces.
    """
    if not isinstance(value, str):
        return ""

    # Replace newlines and tabs with a space
    text = re.sub(r'[\r\n\t]+', ' ', value)

    # Remove emojis and other non-standard unicode symbols
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)

    # Keep only alphanumeric, punctuation, and spaces
    allowed = string.ascii_letters + string.digits + string.punctuation + " " + "éèêëàâäôöûüùçÉÈÊËÀÂÄÔÖÛÜÙÇ"
    text = ''.join(ch for ch in text if ch in allowed)

    # Collapse multiple spaces
    text = re.sub(r'\s{2,}', ' ', text)

    return text.strip()


def is_strong_password(password: str) -> bool:
    """
    Checks if a password is strong (min 8 chars, mixed case, numbers, symbols).
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):  # At least 1 uppercase
        return False
    if not re.search(r"[a-z]", password):  # At least 1 lowercase
        return False
    if not re.search(r"[0-9]", password):  # At least 1 digit
        return False
    if not re.search(r"[^A-Za-z0-9]", password):  # At least 1 symbol
        return False
    return True




def check_if_hashed(password: str) -> bool:
    """
    Returns True if `password` is a recognized Django password hash.
    Uses Django's hasher introspection instead of regex guessing.
    """
    if not password or not isinstance(password, str):
        return False

    try:
        identify_hasher(password)  # raises ValueError if unrecognized
        return True
    except ValueError:
        return False
