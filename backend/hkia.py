from fastapi import FastAPI
import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import json

app = FastAPI()

def get_airport_data():
    """Load airport data from iata.json"""
    try:
        with open('iata.json') as f:
            airports = json.load(f)
            # Convert to dictionary for faster lookups
            return {airport['iata_code']: airport['name'] for airport in airports}
    except FileNotFoundError:
        print("Warning: iata.json not found")
        return {}

def get_hk_flights(date, flight_type='arrival', airport_data=None):
    """
    Get flights data for a specific date and type (arrival/departure)
    """
    if flight_type not in ['arrival', 'departure']:
        raise ValueError("flight_type must be either 'arrival' or 'departure'")
    
    is_arrival = 'true' if flight_type == 'arrival' else 'false'
    api_url = f'https://www.hongkongairport.com/flightinfo-rest/rest/flights/past?date={date}&lang=en&cargo=true&arrival={is_arrival}'
    
    try:
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            rows = []
            
            if not data or not data[0].get('list'):
                return None
            
            for date_entry in data:
                date = date_entry['date']
                for flight in date_entry['list']:
                    flight_time = flight['time']
                    status = flight['status']
                    
                    for f in flight['flight']:
                        flight_no = f['no']
                        airline = f['airline']
                        
                        # Initialize both origin and destination
                        origin = 'HKG'
                        destination = 'HKG'
                        origin_name = airport_data.get('HKG', 'Hong Kong International Airport')
                        destination_name = airport_data.get('HKG', 'Hong Kong International Airport')
                        
                        if flight_type == 'arrival':
                            # For arrivals, update origin
                            if flight['origin']:
                                origin = flight['origin'][0]  # Take first origin
                                origin_name = airport_data.get(origin, f'Unknown ({origin})')
                        else:
                            # For departures, update destination
                            if 'destination' in flight and flight['destination']:
                                destination = flight['destination'][0]  # Take first destination
                                destination_name = airport_data.get(destination, f'Unknown ({destination})')
                        
                        row = {
                            'date': date,
                            'time': flight_time,
                            'flight_no': flight_no,
                            'airline': airline,
                            'origin': origin,
                            'destination': destination,
                            'origin_name': origin_name,
                            'destination_name': destination_name,
                            'status': status,
                            'flight_type': flight_type
                        }
                        rows.append(row)
            
            if rows:
                df = pd.DataFrame(rows)
                df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
                df = df.sort_values('datetime', ascending=True)
                df = df.reset_index(drop=True)
                
                # Order columns
                columns = ['date', 'time', 'flight_no', 'airline', 'origin', 'destination', 
                          'origin_name', 'destination_name', 'status', 'flight_type', 'datetime']
                df = df[columns]
                return df
            return None
        else:
            print(f"Failed to retrieve {flight_type} data for {date}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error retrieving data for {date}: {str(e)}")
        return None

def update_flights_database(filename='hk_flights_database_historical.csv', max_empty_days=7):
    # Load airport data
    airport_data = get_airport_data()
    
    start_date = datetime.now()
    current_date = start_date
    empty_days_count = 0
    
    if os.path.exists(filename):
        existing_df = pd.read_csv(filename)
        existing_df['datetime'] = pd.to_datetime(existing_df['datetime'])
        print(f"Loaded existing database with {len(existing_df)} records")
        
        earliest_date = pd.to_datetime(existing_df['date'].min())
        current_date = earliest_date - timedelta(days=1)
    else:
        existing_df = pd.DataFrame()
        print("Creating new database")
    
    new_data_frames = []
    
    while empty_days_count < max_empty_days:
        if (start_date - current_date).days > 89:
            print("\nReached 89 days limit. Stopping data collection.")
            break
            
        date_str = current_date.strftime('%Y-%m-%d')
        print(f"\nFetching data for {date_str}...")
        
        arrivals_df = get_hk_flights(date_str, 'arrival', airport_data)
        departures_df = get_hk_flights(date_str, 'departure', airport_data)
        
        if arrivals_df is None and departures_df is None:
            empty_days_count += 1
            print(f"No data found for {date_str}. Empty days count: {empty_days_count}")
        else:
            empty_days_count = 0
            if arrivals_df is not None and not arrivals_df.empty:
                new_data_frames.append(arrivals_df)
                print(f"Retrieved {len(arrivals_df)} arrival flights")
            if departures_df is not None and not departures_df.empty:
                new_data_frames.append(departures_df)
                print(f"Retrieved {len(departures_df)} departure flights")
        
        if len(new_data_frames) > 0 and (start_date - current_date).days % 7 == 0:
            print("\nSaving intermediate results...")
            intermediate_df = pd.concat(new_data_frames, ignore_index=True)
            if not existing_df.empty:
                combined_df = pd.concat([existing_df, intermediate_df], ignore_index=True)
            else:
                combined_df = intermediate_df
            
            combined_df = combined_df.drop_duplicates(
                subset=['date', 'time', 'flight_no', 'flight_type'], 
                keep='last'
            )
            combined_df = combined_df.sort_values('datetime', ascending=True)
            combined_df = combined_df.reset_index(drop=True)
            combined_df.to_csv(filename, index=False)
            print(f"Saved {len(combined_df)} records to database")
        
        current_date -= timedelta(days=1)
    
    if new_data_frames:
        new_df = pd.concat(new_data_frames, ignore_index=True)
        
        if not existing_df.empty:
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df = combined_df.drop_duplicates(
                subset=['date', 'time', 'flight_no', 'flight_type'], 
                keep='last'
            )
            combined_df = combined_df.sort_values('datetime', ascending=True)
            combined_df = combined_df.reset_index(drop=True)
        else:
            combined_df = new_df
        
        combined_df.to_csv(filename, index=False)
        print(f"\nDatabase updated. Total records: {len(combined_df)}")
        
        print("\nDate range in database:")
        print(f"Earliest date: {combined_df['date'].min()}")
        print(f"Latest date: {combined_df['date'].max()}")
        
        print("\nFlights by date and type:")
        summary = combined_df.groupby(['date', 'flight_type']).size().unstack(fill_value=0)
        print(summary.tail())
        
        return combined_df
    
    return existing_df

@app.get("/hkia")
def hkia():
    df = update_flights_database()
    
    if not df.empty:
        daily_flights = df.groupby(['date', 'flight_type']).size().unstack(fill_value=0)
        return {
            "totalNumOfFlights": len(df), 
            "numOfUniqueAirlines": df['airline'].nunique(), 
            "dateRange": f"{df['date'].min()} to {df['date'].max()}", 
            "flightsByType": df['flight_type'].value_counts().to_dict(), 
            "mostFreqAirlines": df['airline'].value_counts().head().to_dict(), 
            "avgDailyFlights": daily_flights.mean().to_dict()
        }