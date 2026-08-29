import os
import yfinance as yf
import pandas as pd

def fetch_nifty_50():
    try:
        print("🔗 Connecting to Yahoo Finance API...")
        # ^NSEI is the exact Yahoo ticker for Nifty 50
        nifty = yf.Ticker("^NSEI")
        
        # Period '1d' with interval '1m' forces live/latest intraday rows
        df = nifty.history(period="1d", interval="1m")
        
        if df.empty:
            print("⚠️ The layout returned empty rows! Check if the market is closed or if yfinance needs an update.")
            return
            
        print("🚀 Success! Data rows retrieved:")
        print(df.tail()) # Prints the latest rows to your GitHub Action logs
        
        # CRITICAL: Yahoo puts the timestamp in the index. 
        # Resetting the index turns it into a row column so your CSV isn't just headers.
        df.reset_index(inplace=True)
        
        # Save payload to file
        df.to_csv("nifty50_live.csv", index=False)
        print("💾 Saved rows to nifty50_live.csv")
        
    except Exception as e:
        print(f"❌ Automation failed due to error: {str(e)}")

if __name__ == "__main__":
    fetch_nifty_50()
