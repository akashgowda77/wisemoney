
from database import SessionLocal
from models import User

db = SessionLocal()
users = db.query(User).all()
print(f"Users found: {len(users)}")
for u in users:
    print(f"ID: {u.id} | Name: {u.name} | Email: {u.email} | Hash: {u.password_hash[:10]}...")
db.close()
