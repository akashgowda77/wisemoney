
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
        if self.model is None:
            return None, "Model not loaded"
        df = self.get_data()
        if df.empty:
            return None, "Not enough data"

        # 1. Aggregate expenses by day
        daily_expenses = df.groupby('date')['amount'].sum().to_frame()
        
        # 2. Generate a complete date range from the first expense to the last expense
        min_date = daily_expenses.index.min()
        max_date = daily_expenses.index.max()
        
        # If the user only has 1 day of expenses, we can't build a range
        if min_date == max_date:
            return None, "Need expenses spanning multiple days"
            
        complete_range = pd.date_range(start=min_date, end=max_date, freq='D')
        
        # 3. Reindex the DataFrame to fill missing dates with 0.0
        daily_expenses = daily_expenses.reindex(complete_range, fill_value=0.0).reset_index()
        daily_expenses.rename(columns={'index': 'date'}, inplace=True)
        
        # 4. Prepare features (convert dates to ordinals)
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
