def is_strong(pwd: str) -> bool:
    return len(pwd) >= 8 and \
        all(any(method(c) for c in pwd) for method in (str.islower, str.isupper, str.isdigit)) and \
        all((pwd.count(c) / len(pwd)) < 0.3 for c in pwd)
        