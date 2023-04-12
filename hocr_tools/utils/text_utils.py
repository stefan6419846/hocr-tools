import re


SIMP_RE = re.compile(r'[^a-zA-Z0-9.,!?:;]+')


def normalize(s):
    s = SIMP_RE.sub(' ', s)
    s = s.strip()
    return s
