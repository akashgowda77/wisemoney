
from database import SessionLocal
from models import User, Wallet, Income, Expense
from auth import hash_password
import datetime
import random

db = SessionLocal()

def seed():
    print("Seeding data...")
    
    # 1. Create/Get User
    email = "demo@example.com"
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"Creating user: {email} / password123")
        user = User(
            name="Demo User",
            email=email,
            password_hash=hash_password("password123")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        print(f"User exists: {email}. Updating password to 'password123'...")
        user.password_hash = hash_password("password123")
        db.commit()

    # 2. Create Wallet
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if not wallet:
        print("Creating wallet...")
        wallet = Wallet(name="Main Wallet", balance=5000, user_id=user.id)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)

    # 3. Add Transactions (Historical & Recent)
    print("Adding 50+ transactions...")
    today = datetime.date.today()
    
    # Income Sources
    sources = ["Salary", "Freelance", "Dividend", "Gift"]
    # Expense Categories
    categories = ["Food", "Transport", "Rent", "Entertainment", "Utilities", "Shopping"]

    for i in range(60): # Past 60 days
        date = today - datetime.timedelta(days=i)
        
        # Add Expense (Daily logic: Random chance)
        if random.random() > 0.3: # 70% chance of spending
            amount = round(random.uniform(10, 150), 2)
            cat = random.choice(categories)
            expense = Expense(
                amount=amount,
                category=cat,
                date=date,
                user_id=user.id,
                wallet_id=wallet.id
            )
            wallet.balance -= amount
            db.add(expense)

        # Add Income (Weekly logic)
        if i % 15 == 0: # Every 15 days
            amount = round(random.uniform(2000, 3000), 2)
            income = Income(
                amount=amount,
                source=random.choice(sources),
                date=date,
                user_id=user.id,
                wallet_id=wallet.id
            )
            wallet.balance += amount
            db.add(income)

    db.commit()
    print("Data seeded successfully!")
    print(f"Login with: {email} / password123")

if __name__ == "__main__":
    try:
        seed()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()
