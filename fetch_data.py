import os
import pandas as pd
import requests
from datetime import datetime

# Fetch live Nifty 50 data from a free public endpoint
url = "https://yahoo.com"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers).json()

# Extract real-time metrics safely
meta = response['chart']['result']['meta']
price = round(meta['regularMarketPrice'], 2)
prev_close = meta['previousClose']
change = round(price - prev_close, 2)
pct_change = round((change / prev_close) * 100, 2)
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Create a new row of data
new_data = pd.DataFrame([[timestamp, "Nifty 50", price, change, pct_change]], 
                        columns=['Timestamp', 'Index', 'Price', 'Change', 'Percent_Change'])

# Append to existing file or create a new one if deleted
file_path = 'nifty50.csv'
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    df = pd.concat([df, new_data], ignore_index=True)
else:
    df = new_data

# Save back to your CSV
df.to_csv(file_path, index=False)
