"""
Nigeria Fuel Price Intelligence System
Tracks fuel prices vs FX rate and calculates impact on economy.
Stack: Web Scraping, API Ingestion, Data Correlation
"""

import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import requests

WAREHOUSE_FILE = "nigeria_fuel_fx.csv"
CHART_FILE = "fuel_fx_correlation.png"

def extract_fuel_prices():
    """
    Extract: Simulates scraping NNPC + independent marketers
    In production: Use requests + BeautifulSoup to scrape
    """
    # Simulated live market data (replace with real scraper)
    return [
        {"station": "NNPC Dei-Dei", "type": "PMS", "price_raw": "₦1,030 / litre", "source": "official"},
        {"station": "Total Gwarimpa", "type": "PMS", "price_raw": "₦1,150 / litre", "source": "independent"},
        {"station": "AP Kubwa", "type": "PMS", "price_raw": "₦1,180 / litre", "source": "independent"},
        {"station": "Black Market Wuse", "type": "PMS", "price_raw": "₦1,350 / litre", "source": "black_market"},
    ]

def extract_fx_rate():
    """Extract: CBN / parallel market FX rate"""
    # In production: requests.get('https://api.exchangerate-api.com/v4/latest/USD')
    # Simulated for reliability on mobile
    return 1650.50  # NGN per USD - update daily

def clean_price(raw: str) -> int:
    digits = re.sub(r'[^\d]', '', str(raw))
    return int(digits) if digits else 0

def transform_and_join(fuel_data, fx_rate):
    today = datetime.now().strftime("%Y-%m-%d")
    records = []
    for r in fuel_data:
        price = clean_price(r["price_raw"])
        records.append({
            "date": today,
            "station": r["station"],
            "fuel_type": r["type"],
            "fuel_price_per_litre": price,
            "source_type": r["source"],
            "usd_ngn_rate": fx_rate,
            "fuel_price_usd": round(price / fx_rate, 3) if fx_rate else 0,
            "scraped_at": datetime.now().isoformat()
        })
    return pd.DataFrame(records)

def load_warehouse(df: pd.DataFrame):
    path = Path(WAREHOUSE_FILE)
    if path.exists():
        existing = pd.read_csv(path)
        combined = pd.concat([existing, df], ignore_index=True)
        combined.drop_duplicates(subset=["date", "station"], keep="last", inplace=True)
        combined.to_csv(path, index=False)
        print(f"[LOAD] Warehouse updated: {len(combined)} total records")
    else:
        df.to_csv(path, index=False)
        print(f"[LOAD] New warehouse created")

def generate_correlation_analysis():
    df = pd.read_csv(WAREHOUSE_FILE)
    df['fuel_price_per_litre'] = pd.to_numeric(df['fuel_price_per_litre'], errors='coerce')
    
    daily = df.groupby('date').agg({
        'fuel_price_per_litre': 'mean',
        'usd_ngn_rate': 'mean'
    }).sort_index()

    # Chart 1: Fuel trend
    plt.figure(figsize=(10, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(daily.index, daily['fuel_price_per_litre'], marker='o', color='#E74C3C')
    plt.title('Avg Fuel Price Trend (₦)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 2, 2)
    plt.plot(daily.index, daily['usd_ngn_rate'], marker='s', color='#2E86C1')
    plt.title('USD/NGN Exchange Rate')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(CHART_FILE, dpi=150)
    print(f"[ANALYTICS] Correlation chart saved")

    # Intelligence Report
    print("\n" + "="*55)
    print(" FUEL & FX INTELLIGENCE REPORT")
    print("="*55)
    for date, row in daily.iterrows():
        print(f" {date} | Fuel: ₦{row['fuel_price_per_litre']:.0f} | FX: ₦{row['usd_ngn_rate']:.2f}")

    if len(daily) >= 2:
        fuel_change = daily['fuel_price_per_litre'].iloc[-1] - daily['fuel_price_per_litre'].iloc[-2]
        fx_change = daily['usd_ngn_rate'].iloc[-1] - daily['usd_ngn_rate'].iloc[-2]
        print("-"*55)
        print(f" Fuel Change: ₦{fuel_change:+.0f} | FX Change: ₦{fx_change:+.2f}")
        if fuel_change > 0:
            print(" IMPACT: Transport & cement prices expected to RISE")
            print(" RECOMMENDATION: BUY building materials NOW before increase")
    print("="*55 + "\n")

def main():
    print("Starting Fuel Intelligence ETL...")
    fuel_raw = extract_fuel_prices()
    fx_rate = extract_fx_rate()
    print(f"[EXTRACT] {len(fuel_raw)} stations | FX: ₦{fx_rate}/$")

    df = transform_and_join(fuel_raw, fx_rate)
    load_warehouse(df)
    generate_correlation_analysis()

if __name__ == "__main__":
    main()