
from auth import hash_password, create_access_token
import traceback

print("--- AUTH DIAGNOSTIC START ---")
try:
    print("Testing password hashing...")
    h = hash_password("secret")
    print(f"Hash success: {h[:10]}...")
    
    print("Testing token creation...")
    t = create_access_token({"sub": "test"})
    print(f"Token success: {t[:10]}...")
    
except Exception as e:
    print("AUTH FAILED!")
    traceback.print_exc()

print("--- AUTH DIAGNOSTIC END ---")
