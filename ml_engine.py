
import pandas as pd
try:
    from sklearn.linear_model import LinearRegression
except ImportError:
    LinearRegression = None
from sqlalchemy.orm import Session
from models import Expense
import datetime

class ExpenseForecaster:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.model = LinearRegression()

    def get_data(self):
        # Fetch expenses for the user
        expenses = self.db.query(Expense).filter(Expense.user_id == self.user_id).all()
        if not expenses:
            return pd.DataFrame()
        
        data = [{"date": e.date, "amount": e.amount} for e in expenses]
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        return df

    def train_model(self):
        df = self.get_data()
        if df.empty:
            return None, "Not enough data"

        # Aggregate by day
        daily_expenses = df.groupby('date')['amount'].sum().reset_index()
        
        # Prepare features (convert date to ordinal)
        daily_expenses['date_ordinal'] = daily_expenses['date'].apply(lambda x: x.toordinal())
        
        X = daily_expenses[['date_ordinal']]
        y = daily_expenses['amount']
        
        self.model.fit(X, y)
        return True, "Model trained"

    def predict_next_days(self, days=30):
        is_trained, msg = self.train_model()
        if not is_trained:
            return []

        last_date = datetime.date.today()
        future_dates = [last_date + datetime.timedelta(days=i) for i in range(1, days + 1)]
        future_ordinals = [[d.toordinal()] for d in future_dates]
        
        predictions = self.model.predict(future_ordinals)
        
        result = []
        for d, p in zip(future_dates, predictions):
            result.append({"date": d.strftime("%Y-%m-%d"), "predicted_amount": max(0, round(p, 2))})
            
        return result
