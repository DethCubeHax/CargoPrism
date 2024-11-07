import requests
from datetime import datetime, timedelta
import json
import time

def collect_flight_data():
    # Calculate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    current_date = start_date
    
    all_data = []
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Get arrivals
        arrival_url = f'https://www.hongkongairport.com/flightinfo-rest/rest/flights/past?date={date_str}&lang=en&cargo=true&arrival=true'
        print(f"Fetching arrivals for {date_str}")
        response = requests.get(arrival_url)
        if response.status_code == 200:
            all_data.append({
                'date': date_str,
                'type': 'arrival',
                'data': response.json()
            })
        
        
        # Get departures
        departure_url = f'https://www.hongkongairport.com/flightinfo-rest/rest/flights/past?date={date_str}&lang=en&cargo=true&arrival=false'
        print(f"Fetching departures for {date_str}")
        response = requests.get(departure_url)
        if response.status_code == 200:
            all_data.append({
                'date': date_str,
                'type': 'departure',
                'data': response.json()
            })
        
        current_date += timedelta(days=1)
    
    # Save to file
    with open('hk_flights_raw.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
        
@app.get("/market-metrics")
def market_metrics():
    df = update_flights_database()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        
        # Get current month and last month
        latest_date = df['date'].max()
        current_month_start = latest_date - timedelta(days=30)
        last_month_start = current_month_start - timedelta(days=30)
        
        # Filter dataframes for current and last month
        current_month_df = df[(df['date'] >= current_month_start) & (df['date'] <= latest_date)]
        last_month_df = df[(df['date'] >= last_month_start) & (df['date'] < current_month_start)]
        
        # Market Share Calculation
        def calculate_market_share(df):
            non_cancelled_flights = df[df['status'] != 'Cancelled']
            cx_flights = non_cancelled_flights[non_cancelled_flights['airline'] == 'CPA']
            return (len(cx_flights) / len(non_cancelled_flights) * 100) if len(non_cancelled_flights) > 0 else 0
        
        current_market_share = calculate_market_share(current_month_df)
        last_market_share = calculate_market_share(last_month_df)
        market_share_change = current_market_share - last_market_share
        
        # Routes Served Calculation
        def count_unique_routes(df):
            cx_routes = df[df['airline'] == 'CPA'][['origin', 'destination']].drop_duplicates()
            return len(cx_routes)
        
        current_routes = count_unique_routes(current_month_df)
        last_routes = count_unique_routes(last_month_df)
        routes_change = current_routes - last_routes
        
        # Competitor Count Calculation
        def count_competitors(df):
            return df[df['airline'] != 'CPA']['airline'].nunique()
        
        current_competitors = count_competitors(current_month_df)
        last_competitors = count_competitors(last_month_df)
        competitors_change = current_competitors - last_competitors
        
        # Market Growth Calculation (based on total flights)
        current_total_flights = len(current_month_df[current_month_df['status'] != 'Cancelled'])
        last_total_flights = len(last_month_df[last_month_df['status'] != 'Cancelled'])
        market_growth = ((current_total_flights - last_total_flights) / last_total_flights * 100) if last_total_flights > 0 else 0
        
        return {
            "market_share": {
                "value": round(current_market_share, 1),
                "change": round(market_share_change, 1)
            },
            "routes_served": {
                "value": current_routes,
                "change": routes_change
            },
            "competitor_count": {
                "value": current_competitors,
                "change": competitors_change
            },
            "market_growth": {
                "value": round(market_growth, 1)
            }
        }

if __name__ == "__main__":
    collect_flight_data()