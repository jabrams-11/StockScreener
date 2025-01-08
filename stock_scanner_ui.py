import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd


st.set_page_config(page_title="Stock Scanner", layout="wide")

def fetch_stock_data():
    url = "https://scanner.tradingview.com/america/scan?label-product=screener-stock"
    
    headers = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9,fr;q=0.8",
        "content-type": "application/json",
        "origin": "https://www.tradingview.com",
        "referer": "https://www.tradingview.com/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/131.0.0.0 Safari/537.36",
    }

    payload = {
        "columns": [
            "name", "description", "close", "change", "volume",
            "relative_volume_10d_calc", "market_cap_basic", 
            "sector", "exchange"
        ],
        "filter": [
            {"left": "close", "operation": "in_range", "right": [1, 30]},
            {"left": "change", "operation": "greater", "right": 10},
            {"left": "relative_volume_10d_calc", "operation": "greater", "right": 5},
            {"left": "float_shares_outstanding_current", "operation": "in_range", "right": [0, 10000000]},
            {"left": "volume", "operation": "greater", "right": 10000000}
        ],
        "markets": ["america"],
        "range": [0, 100],
        "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def process_stock_data(data):
    stocks = []
    for item in data['data']:
        stock = {
            'Symbol': item['d'][0],
            'Company': item['d'][1],
            'Price': f"${item['d'][2]:.2f}",
            'Change %': f"{item['d'][3]:.2f}%",
            'Volume': f"{item['d'][4]:,}",
            'Relative Volume': f"{item['d'][5]:.2f}x",
            'Market Cap': f"${item['d'][6]:,}",
            'Sector': item['d'][7],
            'Exchange': item['d'][8]
        }
        stocks.append(stock)
    return pd.DataFrame(stocks)

st.title("🚀 High Volume Stock Scanner")


col1, col2 = st.columns([2, 1])
with col1:
    if st.button("🔄 Refresh Data", type="primary"):
        st.session_state['refresh_trigger'] = not st.session_state.get('refresh_trigger', False)
with col2:
    st.markdown(f"*Last updated: {datetime.now().strftime('%I:%M:%S %p')}*")


st.divider()


st.subheader("📊 Scanning Criteria")
criteria_cols = st.columns(5)
with criteria_cols[0]:
    st.metric("Price Range", "$1 - $30")
with criteria_cols[1]:
    st.metric("Min Price Change", "+10%")
with criteria_cols[2]:
    st.metric("Min Rel. Volume", "5x")
with criteria_cols[3]:
    st.metric("Max Float", "10M shares")
with criteria_cols[4]:
    st.metric("Min Volume", "10M shares")


st.divider()


try:
    data = fetch_stock_data()
    df = process_stock_data(data)
    
    if len(df) == 0:
        st.info("🔍 No stocks currently meet the criteria")
    else:
        st.subheader(f"📈 Found {len(df)} Matching Stocks")
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            height=400 if len(df) > 5 else None
        )

except Exception as e:
    st.error(f"❌ Error fetching data: {str(e)}")
