import json
import re
import os
from typing import Set
import unicodedata
import string
import logging
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from PIL import Image

from django.core.files.uploadedfile import UploadedFile

# Logger
logger = logging.getLogger(__name__)

# ?-----------------------------end imports-------------------




def safe_to_decimal(value, max_digits=10, decimal_places=3) -> Decimal:
    """
    Safely convert any value to Decimal, clip to max_digits and decimal_places,
    and quantize safely. Never raises InvalidOperation.
    """
    # Validate parameters
    try:
        max_digits = int(max_digits)
        decimal_places = int(decimal_places)
    except (ValueError, TypeError):
        raise ValueError("max_digits and decimal_places must be integers")

    if max_digits <= decimal_places:
        raise ValueError("max_digits must be greater than decimal_places")

    # Convert safely to Decimal
    try:
        value = Decimal(str(value))
    except (ValueError, TypeError, InvalidOperation):
        value = Decimal('0')

    # Compute max allowed value (e.g., for 10,3 -> 9999999.999)
    int_part = '9' * (max_digits - decimal_places)
    frac_part = '9' * decimal_places
    max_value = Decimal(f"{int_part}.{frac_part}")

    # Clip to range [0, max_value]
    if value > max_value:
        value = max_value
    elif value < 0:
        value = Decimal('0')

    # Quantize using explicit exponent form (preferred)
    try:
        quantizer = Decimal(f"1e-{decimal_places}")
        value = value.quantize(quantizer, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        # Fallback to max value if quantization fails
        value = max_value

    return value



def safe_json_parse(data: str, default=None):
    """
        Safely parses a JSON string, returning a default value if parsing fails.

        Args:
            data (str): JSON string to parse.
            default: Value to return on failure (default: None).

        Returns:
            dict | list | Any: Parsed object or default.
    """
    try:
        return json.loads(data)
    except (ValueError, TypeError):
        return default


def is_valid_json(json_str: str) -> bool:
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False




def is_safe_upload(file: UploadedFile, max_size_mb: int = 10, allowed_types=None) -> bool:
    """
    Validates uploaded files securely:
    - Checks real file type (not just extension or content_type)
    - Enforces size limits
    - Configurable allowed types
    """
    # Configurable allowed types (extension + MIME)
    allowed_types = allowed_types or {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".pdf": "application/pdf",
    }

    ext = os.path.splitext(file.name)[1].lower()
    mime = file.content_type

    # Quick extension + MIME sanity check
    if ext not in allowed_types or mime != allowed_types[ext]:
        return False

    # Enforce max file size
    if file.size > max_size_mb * 1024 * 1024:
        return False

    # Deeper content inspection for images
    if allowed_types[ext].startswith("image/"):
        try:
            img = Image.open(file)
            img.verify()  # ensures file is an actual image
        except Exception:
            return False
        finally:
            file.seek(0)  # reset file pointer for Django’s next use

    return True



def contains_malicious_code(text: str) -> bool:
    """
    Checks for suspicious HTML/JS patterns.
    alternatively use bleach exp: sanitized = bleach.clean(text, tags=[], attributes={}, strip=True)
    """
    patterns = [
        r"<script.*?>.*?</script>",
        r"onerror=",
        r"onload=",
        r"javascript:",
        r"&lt;script&gt;",
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)



class SpamDetector:
    """
    Lightweight, dependency-free spam and abuse text detector.
    Uses regex heuristics for common spam, profanity, and phishing patterns.
    """

    def __init__(self, log_level=logging.WARNING):
        # --- Logging setup ---
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(log_level)

        # --- Patterns and heuristics ---
        allowed_chars = string.ascii_letters + string.digits + string.punctuation + string.whitespace
        allowed_chars_escaped = re.escape(allowed_chars)
        self.allowed_chars_pattern = re.compile(rf"^[{allowed_chars_escaped}À-ÿ]+$")

        self.url_pattern = re.compile(r"(?:https?://|www\.|ftp://)[^\s/$.?#]+\.[^\s]*", re.IGNORECASE)
        self.gibberish_pattern = re.compile(
            r"(?:\b(?=\w*[A-Z])(?=\w*[a-z])[A-Za-z]{4,}\b[\s]*){3,}"
            r"|\b\w*\d+\w*\b|[A-Za-z]{15,}|(?:[^a-zA-Z0-9\s]|_){3,}"
        )
        self.emoji_pattern = re.compile(r"[\U0001F300-\U0001FAD6\U0001FAE0-\U0001FAFF]")

        self.spam_keywords: Set[str] = {"your spammiest words"} # common spam words: https://gist.github.com/prasidhda/13c9303be3cbc4228585a7f1a06040a3
        self.whitelist: Set[str] = {"your meanest words"} # profanity: https://github.com/zacanger/profane-words/blob/master/words.json

    # --- Detection Methods ---

    def contains_spam(self, message: str) -> bool:
        """Detects spammy content: URLs, gibberish, emojis, or spam keywords."""
        message = unicodedata.normalize("NFKC", message)
        message = message.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "")
        message_lower = message.lower()

        if not self.allowed_chars_pattern.fullmatch(message):
            self.logger.debug("Rejected for disallowed characters.")
            return True

        if self.url_pattern.search(message):
            self.logger.debug("Detected URL in message.")
            return True

        if self.gibberish_pattern.search(message):
            self.logger.debug("Detected gibberish pattern.")
            return True

        if len(self.emoji_pattern.findall(message)) > 3:
            self.logger.debug("Detected excessive emojis.")
            return True

        spam_keywords = self.spam_keywords - self.whitelist
        for keyword in spam_keywords:
            if re.search(rf"\b{re.escape(keyword)}\b", message_lower):
                self.logger.debug(f"Matched spam keyword: {keyword!r}")
                return True

        return False

    def contains_contact_info(self, message: str) -> bool:
        """Detects email addresses or phone numbers."""
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        phone_pattern = r"(\+\d{1,3}[-.\s]?)?(\d{3}[-.\s]?){2}\d{4}"
        if re.search(email_pattern, message, re.IGNORECASE) or re.search(phone_pattern, message):
            self.logger.debug("Detected contact info (email or phone).")
            return True
        return False

    def has_excessive_punctuation(self, message: str, max_allowed: int = 3) -> bool:
        """Detects runs of !, ?, or . beyond allowed threshold."""
        if re.search(rf"([!?\.]){{{max_allowed + 1},}}", message):
            self.logger.debug("Detected excessive punctuation.")
            return True
        return False

    def is_all_caps(self, message: str, threshold: float = 0.8) -> bool:
        """Checks if a message is mostly uppercase."""
        if len(message) < 5:
            return False
        uppercase_ratio = sum(c.isupper() for c in message) / len(message)
        if uppercase_ratio > threshold:
            self.logger.debug(f"Message mostly uppercase (ratio={uppercase_ratio:.2f}).")
            return True
        return False

    def has_repeated_chars(self, message: str, max_repeats: int = 3) -> bool:
        """Detects long runs of the same character (e.g. helloooo)."""
        if re.search(rf"(.)\1{{{max_repeats},}}", message):
            self.logger.debug("Detected repeated characters.")
            return True
        return False

    def has_suspicious_unicode(self, message: str) -> bool:
        """Detects Cyrillic or Arabic script mixed with Latin."""
        if re.search(r"[\u0400-\u04FF\u0600-\u06FF]", message):
            self.logger.debug("Detected suspicious Unicode range (Cyrillic/Arabic).")
            return True
        return False

    def contains_profanity(self, message: str, extra_keywords: Set[str]) -> bool:
        """Detects custom profanity or banned words."""
        profanity_words = set(extra_keywords)
        message_lower = message.lower()
        for w in profanity_words:
            if re.search(rf"\b{re.escape(w)}\b", message_lower):
                self.logger.debug(f"Matched profanity: {w!r}")
                return True
        return False

    def is_phishing(self, message: str, extra_keywords: Set[str]) -> bool:
        """Detects phishing-like keywords."""
        phishing_keywords = set(extra_keywords)
        message_lower = message.lower()
        for k in phishing_keywords:
            if k in message_lower:
                self.logger.debug(f"Matched phishing keyword: {k!r}")
                return True
        return False

    def has_hidden_chars(self, message: str) -> bool:
        """Detects invisible Unicode characters."""
        zero_width_chars = {"\u200b", "\u200c", "\u200d", "\ufeff"}
        for c in zero_width_chars:
            if c in message:
                self.logger.debug(f"Detected hidden character: {repr(c)}")
                return True
        return False
