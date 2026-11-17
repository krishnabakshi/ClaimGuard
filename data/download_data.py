"""Re-download the raw dataset into data/fraud_oracle.csv.

Original source: Kaggle, "Vehicle Insurance Claim Fraud Detection" by Shivam Bansal
(https://www.kaggle.com/datasets/shivamb/vehicle-claim-fraud-detection), which needs a login.
This script uses a public GitHub mirror of the same file. Run from the repo root:
    python data/download_data.py
"""

import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/abhisheks008/Car.ly/main/Dataset/fraud_oracle.csv"
OUT = Path(__file__).resolve().parent / "fraud_oracle.csv"

if __name__ == "__main__":
    print(f"Downloading {URL}")
    urllib.request.urlretrieve(URL, OUT)
    print(f"Saved {OUT} ({OUT.stat().st_size / 1e6:.1f} MB)")
