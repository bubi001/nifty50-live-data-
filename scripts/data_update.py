import requests
import pandas as pd
from datetime import datetime
import subprocess
import io

# --- CONFIG ---
GITHUB_REPO = "USERNAME/REPO"   # replace with your repo
TOKEN = "YOUR_GITHUB_PAT"       # GitHub personal access token

# --- Helper: Commit & Push ---
def git_push(file_path, message):
    subprocess.run(["git", "add", file_path])
    subprocess.run(["git", "commit", "-m", message])
    subprocess.run([
        "git", "push",
        f"https://{TOKEN}@github.com/{GITHUB_REPO}.git",
        "main"
    ])

# --- 1. ETF Bhavcopy ---
def update_etf():
    today = datetime.today()
    dd = today.strftime("%d")
    mmm = today.strftime("%b").upper()
    yyyy = today.strftime("%Y")

    url = f"https://www.nseindia.com/content/historical/EQUITIES/{yyyy}/{mmm}/cm{dd}{mmm}{yyyy}bhav.csv"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print("ETF Bhavcopy not available")
        return

    df = pd.read_csv(io.StringIO(r.text))
    df = df[["TIMESTAMP","SYMBOL","CLOSE"]]

    file_path = "history_etf.csv"
    try:
        history = pd.read_csv(file_path)
        history = pd.concat([history, df])
        history.drop_duplicates(subset=["TIMESTAMP","SYMBOL"], inplace=True)
    except FileNotFoundError:
        history = df

    history.to_csv(file_path, index=False)
    git_push(file_path, f"Update ETF Bhavcopy {dd}-{mmm}-{yyyy}")

# --- 2. Sector Indices ---
def update_sector():
    url = "https://www.nseindia.com/api/index-historical-data?index=all"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print("Sector data not available")
        return

    df = pd.DataFrame(r.json()["data"])
    df = df[["date","indexName","close"]]

    file_path = "history_sector.csv"
    try:
        history = pd.read_csv(file_path)
        history = pd.concat([history, df])
        history.drop_duplicates(subset=["date","indexName"], inplace=True)
    except FileNotFoundError:
        history = df

    history.to_csv(file_path, index=False)
    git_push(file_path, f"Update Sector Rotation {datetime.today().strftime('%d-%b-%Y')}")

# --- 3. Mutual Fund Flows (AMFI monthly) ---
def update_mf():
    url = "https://portal.amfiindia.com/spages/MFMonthlyReportSep2026.xlsx"
    r = requests.get(url)
    if r.status_code != 200:
        print("MF data not available")
        return

    with open("mf.xlsx", "wb") as f:
        f.write(r.content)

    df = pd.read_excel("mf.xlsx")
    df = df[["Category","Inflow","Outflow"]]
    df["Date"] = datetime.today().strftime("%Y-%m")

    file_path = "mf_rotation.csv"
    try:
        history = pd.read_csv(file_path)
        history = pd.concat([history, df])
        history.drop_duplicates(subset=["Date","Category"], inplace=True)
    except FileNotFoundError:
        history = df

    history.to_csv(file_path, index=False)
    git_push(file_path, f"Update MF Rotation {datetime.today().strftime('%Y-%m')}")

# --- Run All ---
update_etf()
update_sector()
update_mf()
