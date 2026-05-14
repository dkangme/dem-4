import random
import string

def generate_short_code(length: int = 8) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choice(alphabet) for _ in range(length))
