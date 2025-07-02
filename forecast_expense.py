import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

# Step 1: Load your Excel data
df = pd.read_excel("forecast_data.xlsx")

# Step 2: Check the data format
print("Original Data:")
print(df.head())

# Step 3: Initialize the Prophet model
model = Prophet()

# Step 4: Train the model
model.fit(df)

# Step 5: Create future dates for prediction (next 30 days)
future = model.make_future_dataframe(periods=30)

# Step 6: Predict future values
forecast = model.predict(future)

# Step 7: Show the forecasted data
print("Forecasted Data:")
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())

# Step 8: Plot the results
model.plot(forecast)
plt.title("Expense Forecast for Next 30 Days")
plt.xlabel("Date")
plt.ylabel("Expense Amount")
plt.tight_layout()
plt.show()
