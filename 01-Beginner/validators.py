MIN_CHARS = 20
MAX_CHARS = 6000


def validate_input(text: str) -> tuple[bool, str]:
    """Return (is_valid, error_message)."""
    if not text or not text.strip():
        return False, "Please enter some text first."
    cleaned = text.strip()
    if len(cleaned) < MIN_CHARS:
        return False, f"Input is too short. Please enter at least {MIN_CHARS} characters."
    if len(cleaned) > MAX_CHARS:
        return False, f"Input is too long ({len(cleaned)} characters). Maximum is {MAX_CHARS}."
    if not any(c.isalpha() for c in cleaned):
        return False, "Input must contain readable text, not just numbers or symbols."
    return True, ""