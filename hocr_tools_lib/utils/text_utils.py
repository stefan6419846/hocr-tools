import re


SIMP_RE = re.compile(r'[^a-zA-Z0-9.,!?:;]+')


def normalize(s: str) -> str:
    """
    Normalize the given string.
    """
    s = SIMP_RE.sub(' ', s)
    s = s.strip()
    return s
