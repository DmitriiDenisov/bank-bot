import os
import secrets

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

private_key: str = secrets.token_hex(32)

print(private_key)
# with open(os.path.join(PROJECT_PATH, 'credentials', 'private_key_HS256'), "w") as f:
#    f.write(private_key)
