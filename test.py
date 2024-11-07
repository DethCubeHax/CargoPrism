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

if __name__ == "__main__":
    collect_flight_data()