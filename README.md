# wisemoney
A smart, data-driven personal finance and spending insight platform.
# 💰 WiseMoney – AI-Powered Personal Finance Management System

WiseMoney is a full-stack personal finance management platform that helps users track income, expenses, wallets, financial goals, and spending behavior through an intelligent analytics dashboard.

The platform combines financial tracking with AI-driven insights to help users improve savings habits, monitor financial health, and make informed financial decisions.

---

## 🚀 Features

### 🔐 Secure Authentication

* User Registration
* User Login
* JWT-based Authentication
* Protected API Endpoints

### 💵 Income Management

* Add Income Records
* Track Multiple Income Sources
* Income History Management

### 💸 Expense Management

* Add Expenses
* Categorize Spending
* Expense Tracking and Analysis

### 👛 Wallet Management

* Multiple Wallet Support
* Real-Time Balance Updates
* Automatic Balance Adjustments

### 🎯 Goal Tracking

* Create Financial Goals
* Monitor Goal Progress
* Savings Tracking
* Goal Achievement Analytics

### 📊 Smart Dashboard

* Total Income Overview
* Total Expense Overview
* Wallet Balance Monitoring
* Financial Score Calculation
* Expense Distribution Visualization

### 🤖 AI Financial Advisor

* Personalized Recommendations
* Spending Pattern Analysis
* Goal Progress Evaluation
* Savings Suggestions
* Emergency Fund Guidance

### 📈 Financial Reports

* Financial Summary Reports
* Trend Analysis
* Forecast Generation
* Data Export Functionality

---

## 🏗️ System Architecture

```text
Frontend (HTML, CSS, Bootstrap, JavaScript)
                    │
                    ▼
           FastAPI Backend
                    │
                    ▼
          SQLAlchemy ORM
                    │
                    ▼
              SQLite DB
```

---

## 🛠️ Tech Stack

### Frontend

* HTML5
* CSS3
* Bootstrap 5
* JavaScript
* Chart.js
* Font Awesome

### Backend

* FastAPI
* Python
* SQLAlchemy
* Pydantic
* JWT Authentication
* Uvicorn

### Database

* SQLite

---

## 📂 Project Structure

```text
WiseMoney
│
├── auth.py
├── main.py
├── database.py
├── models.py
├── income.py
├── expense.py
├── wallet.py
├── goals.py
├── dashboard.py
├── advisor.py
├── insights.py
├── report.py
├── transaction.py
│
├── frontend/
│   ├── pages/
│   ├── css/
│   ├── js/
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/akashgowda77/wisemoney.git
cd wisemoney
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / Mac

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run Backend

```bash
python -m uvicorn main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

---

## ▶️ Run Frontend

```bash
cd frontend
python -m http.server 5500
```

Frontend URL:

```text
http://localhost:5500/pages/login.html
```

---

## 📊 Core Modules

### Authentication

* JWT Login
* User Registration
* Secure API Access

### Transactions

* Income Recording
* Expense Recording
* Financial Tracking

### Dashboard

* Financial KPIs
* Charts and Analytics
* Financial Score

### Goals

* Savings Goals
* Progress Monitoring
* Goal Achievement Metrics

### Advisor

* AI-Powered Financial Recommendations
* Spending Analysis
* Savings Optimization

### Reports

* Financial Summaries
* Trend Analysis
* Forecast Reports

---

## 🔮 Future Enhancements

* Bank Account Integration
* UPI Transaction Sync
* AI Chat Assistant
* Budget Planning Engine
* Investment Recommendations
* Mobile Application
* Cloud Deployment
* Multi-Currency Support

---

## ⭐ Project Goal

WiseMoney aims to simplify personal finance management through intelligent analytics, financial goal tracking, and AI-powered recommendations that help users make smarter financial decisions.
