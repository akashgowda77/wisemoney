
import re
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class NLPRequest(BaseModel):
    text: str

class TransactionParser:
    def __init__(self):
        # Regex patterns for extraction
        self.amount_pattern = r"(\d+(\.\d{1,2})?)"
        
        # Keywords to identify type
        self.income_keywords = ["received", "got", "income", "salary", "deposit", "added"]
        self.expense_keywords = ["spent", "paid", "bought", "expense", "purchase", "cost"]
        
    def parse(self, text: str):
        """
        Parses a natural language string to extract transaction details.
        Returns a dict: {"type": str, "amount": float, "category": str}
        """
        text = text.lower().strip()
        result = {
            "type": None,
            "amount": 0.0,
            "category": "General", # Default
            "confidence": 0.0
        }

        # 1. Extract Amount
        match = re.search(self.amount_pattern, text)
        if match:
            result["amount"] = float(match.group(1))
        else:
            return None # No amount found, cannot process

        # 2. Determine Type (Income vs Expense)
        # Check for income keywords
        if any(word in text for word in self.income_keywords):
            result["type"] = "Income"
            result["confidence"] = 0.8
        # Check for expense keywords
        elif any(word in text for word in self.expense_keywords):
            result["type"] = "Expense"
            result["confidence"] = 0.8
        else:
            # Default to Expense if "spent" format usually
            result["type"] = "Expense"
            result["confidence"] = 0.5

        # 3. Extract Category/Source
        # Strategy: Remove amount and keywords, what's left is likely the category
        clean_text = text
        # Remove amount
        clean_text = re.sub(self.amount_pattern, "", clean_text)
        
        # Remove common prepositions
        for prep in [" on ", " for ", " from ", " at ", " in ", " to "]:
            clean_text = clean_text.replace(prep, " ")
            
        # Remove keywords
        for word in self.income_keywords + self.expense_keywords:
            clean_text = clean_text.replace(word, "")
            
        # Clean up whitespace
        category = clean_text.strip().title()
        
        # If category is empty or just "dollars", set default
        if not category or category in ["Dollars", "Rupees", "Rs"]:
            result["category"] = "Uncategorized"
        else:
            result["category"] = category

        return result

parser = TransactionParser()

@router.post("/parse")
def parse_text(request: NLPRequest):
    return parser.parse(request.text)
