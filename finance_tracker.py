import pandas as pd

# Step 1: Read the Excel file
data = pd.read_excel("bank_data2.xlsx")

# Step 2: Define a function to categorize each expense
def categorize(description):
    description = description.lower()
    if "domino" in description or "pizza" in description:
        return "Food"
    elif "uber" in description or "ola" in description:
        return "Transport"
    elif "amazon" in description or "flipkart" in description:
        return "Shopping"
    elif "salary" in description or "freelance" in description:
        return "Income"
    elif "electricity" in description or "bill" in description:
        return "Utilities"
    else:
        return "Other"

# Step 3: Apply the function to each row
data["Category"] = data["Description"].apply(categorize)

# Step 4: Show the updated data
print("Your Categorized Bank Statement:")
print(data)



import matplotlib.pyplot as plt

# Group by category and add the amounts
category_totals = data[data["Type"] == "Debit"].groupby("Category")["Amount"].sum()

# 🥧 Pie Chart: Spending by Category
plt.figure(figsize=(6, 6))
plt.pie(category_totals, labels=category_totals.index, autopct='%1.1f%%', startangle=90)
plt.title("Spending by Category")
plt.axis('equal')
plt.show()




# 📅 Bar Chart: Daily Spending
daily_totals = data[data["Type"] == "Debit"].groupby("Date")["Amount"].sum()

plt.figure(figsize=(8, 4))
plt.bar(daily_totals.index.astype(str), daily_totals.values, color='skyblue')
plt.xticks(rotation=45)
plt.title("Daily Expenses")
plt.xlabel("Date")
plt.ylabel("Amount Spent")
plt.tight_layout()
plt.show()







from sklearn.linear_model import LinearRegression
import numpy as np

# Filter only DEBIT transactions (expenses)
expense_data = data[data["Type"] == "Debit"]

# Group by date and get total expenses per day
daily_expense = expense_data.groupby("Date")["Amount"].sum().reset_index()

# Convert dates to numbers (for ML model)
daily_expense["Day"] = np.arange(len(daily_expense))

# Prepare X and y (input and output)
X = daily_expense[["Day"]]  # Input: Day number (0,1,2...)
y = daily_expense["Amount"]  # Output: Amount spent

# Train model
model = LinearRegression()
model.fit(X, y)

# Predict next 7 days
future_days = np.arange(len(daily_expense), len(daily_expense) + 7).reshape(-1, 1)
predicted_expenses = model.predict(future_days)

# Print predictions
print("\n📅 Predicted Expenses for Next 7 Days:")
for i, amount in enumerate(predicted_expenses):
    print(f"Day {i + 1}: ₹{round(amount, 2)}")









print("\n📢 Smart Alerts & Tips:")

# 1. Total spending this month
total_spent = data[data["Type"] == "Debit"]["Amount"].sum()
print(f"💸 Total spent: ₹{total_spent}")

# 2. Spending by category
category_spending = data[data["Type"] == "Debit"].groupby("Category")["Amount"].sum()

# 3. Alert if any category > ₹1000
for category, amount in category_spending.items():
    if amount > 1000:
        print(f"⚠️ High spending in {category}: ₹{amount}")

# 4. Top spending category
top_category = category_spending.idxmax()
top_amount = category_spending.max()
print(f"📊 You spent the most on {top_category} (₹{top_amount})")

# 5. Simple savings tip
if total_spent > 3000:
    print("💡 Tip: Try to cut down on unnecessary expenses to save at least ₹500 next month.")
else:
    print("✅ Good job! Your spending is within a healthy range.")
