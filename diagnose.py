
from database import SessionLocal, engine
from models import Base, User
import traceback
import sys

print("--- DIAGNOSTIC START ---")
print(f"Python executable: {sys.executable}")
print(f"Database URL: {engine.url}")

try:
    # 1. Force table creation
    print("Step 1: Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    # 2. Try inserting a user directly
    print("Step 2: Attempting to insert a test user...")
    db = SessionLocal()
    try:
        # Check if user exists
        existing = db.query(User).filter(User.email == "diag@example.com").first()
        if existing:
            print("Test user already exists. Skipping insert.")
        else:
            user = User(name="Test Diagnostics", email="diag@example.com", password_hash="dummyhash")
            db.add(user)
            db.commit()
            print("User inserted successfully!")
            
    except Exception as e:
        print("\n!!! INSERTION FAILED !!!")
        traceback.print_exc()
    finally:
        db.close()

except Exception as e:
    print("\n!!! GLOBAL FAILURE !!!")
    traceback.print_exc()

print("--- DIAGNOSTIC END ---")
