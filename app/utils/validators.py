import re


PHONE_RE = re.compile(r"^\+?\d{9,15}$")


def is_valid_full_name(value: str) -> bool:
    parts = [part for part in value.strip().split() if part]
    return len(parts) >= 2 and all(len(part) >= 2 for part in parts)


def normalize_phone(value: str) -> str | None:
    phone = value.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if phone.startswith("998") and not phone.startswith("+"):
        phone = f"+{phone}"
    if PHONE_RE.fullmatch(phone):
        return phone
    return None
