import re

def is_email(email):
    """
    Check if the given string is an email.
    """
    if re.fullmatch(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?", email):
        return True
    return False
