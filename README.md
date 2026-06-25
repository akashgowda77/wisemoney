# 💰 WiseMoney – AI-Powered Personal Finance Management Platform

> **WiseMoney** is a full-stack AI-powered personal finance management platform that helps users track income, expenses, wallets, budgets, savings goals, and financial health while providing intelligent financial insights and spending recommendations.

---

## 🌟 Overview

Managing personal finances can be challenging when income, expenses, savings, and financial goals are scattered across multiple sources.

**WiseMoney** solves this problem by bringing everything together into a single intelligent platform where users can:

* Track income and expenses
* Manage multiple wallets
* Plan monthly budgets
* Monitor financial goals
* Analyze spending behavior
* Detect unusual transactions
* Receive AI-powered financial recommendations
* Visualize financial reports and trends

---

# ✨ Key Features

## 🔐 Authentication

* Secure User Registration
* JWT-based Login
* Protected API Endpoints
* User-specific Financial Data

---

## 💵 Income Management

* Add Income
* Multiple Income Sources
* Wallet Selection
* Automatic Wallet Balance Update
* Income History

---

## 💸 Expense Management

* Add Expenses
* Category-based Expense Tracking
* Wallet Selection
* Automatic Wallet Balance Deduction
* Transaction History

---

## 👛 Wallet Management

* Multiple Wallets
* Real-time Balance Tracking
* Wallet-to-Wallet Transfers
* Automatic Balance Updates

---

## 🎯 Goal Tracking

* Create Financial Goals
* Goal Progress Tracking
* Goal Funding
* Goal Achievement Status

---

## 📊 Budget Intelligence

* Monthly Budgets
* Budget Utilization
* Remaining Budget
* Budget Health Score
* Budget Recommendations
* Budget Breach Detection

---

## 📈 Financial Dashboard

* Total Income
* Total Expenses
* Wallet Balance
* Savings Overview
* Financial Score
* Monthly Trends
* Expense Distribution

---

## 🤖 AI Financial Advisor

WiseMoney provides intelligent recommendations based on user spending.

Examples:

* Reduce unnecessary expenses
* Improve savings habits
* Emergency fund suggestions
* Spending optimization
* Personalized financial advice

---

## 📄 Financial Reports

* Financial Summary
* Monthly Trend Analysis
* Expense Forecasting
* Export Reports (CSV)

---

## ❤️ Financial Health

* Financial Health Score
* Savings Analysis
* Spending Quality
* Overall Financial Wellness

---

## 🚨 Anomaly Detection

Automatically detects:

* Unusual Expenses
* Spending Outliers
* Abnormal Financial Behaviour

---

# 🏗️ System Architecture

```text
                  Frontend
        HTML • CSS • Bootstrap • JS
                     │
                     ▼
             FastAPI Backend
                     │
                     ▼
            SQLAlchemy ORM
                     │
                     ▼
               SQLite Database
```

---

# 🛠 Tech Stack

## Frontend

* HTML5
* CSS3
* Bootstrap 5
* JavaScript (ES6)
* Chart.js
* Font Awesome

---

## Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* JWT Authentication
* Uvicorn

---

## Database

* SQLite

---

# 📂 Project Structure

```text
WiseMoney
│
├── auth.py
├── main.py
├── database.py
├── models.py
│
├── income.py
├── expense.py
├── wallet.py
├── transaction.py
│
├── goals.py
├── budget.py
├── budget_crud.py
├── dashboard.py
├── advisor.py
├── report.py
├── anomaly.py
├── insights.py
├── financial_health.py
│
├── frontend/
│   ├── pages/
│   ├── css/
│   ├── js/
│   └── assets/
│
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/akashgowda77/wisemoney.git
cd wisemoney
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run Backend

```bash
uvicorn main:app --reload
```

Backend

```
http://127.0.0.1:8000
```

Swagger API

```
http://127.0.0.1:8000/docs
```

---

# ▶️ Run Frontend

```bash
cd frontend
python -m http.server 5500
```

Open

```
http://localhost:5500/pages/login.html
```

---

# 📊 Core Modules

| Module            | Description                        |
| ----------------- | ---------------------------------- |
| Authentication    | Secure JWT Authentication          |
| Dashboard         | Financial Overview                 |
| Wallet            | Multi-wallet Management            |
| Income            | Income Tracking                    |
| Expense           | Expense Tracking                   |
| Transactions      | Financial Ledger                   |
| Goals             | Savings Goal Management            |
| Budget            | Budget Planning & Monitoring       |
| Reports           | Reports & Forecasting              |
| Financial Health  | Financial Wellness Analysis        |
| AI Advisor        | Personalized Recommendations       |
| Anomaly Detection | Fraud & Spending Outlier Detection |

---

# 🔮 Future Enhancements

* Bank Account Integration
* UPI Synchronization
* Mobile Application
* Cloud Deployment
* OCR Bill Scanner
* Investment Portfolio Tracking
* AI Chat Assistant
* Voice-based Expense Entry
* Multi-currency Support
* Notification & Email Alerts

---

# 🎯 Project Goal

WiseMoney aims to make personal finance management smarter through AI-powered analytics, budgeting, financial health monitoring, anomaly detection, and intelligent recommendations, enabling users to make informed financial decisions and improve long-term financial well-being.


