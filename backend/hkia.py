from fastapi import FastAPI

import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time

app = FastAPI()

def get_hk_flights(date, flight_type='arrival', max_retries=3):
    """
    Get flights data for a specific date and type (arrival/departure)
    """
    # Validate flight type
    if flight_type not in ['arrival', 'departure']:
        raise ValueError("flight_type must be either 'arrival' or 'departure'")
    
    # Set parameters based on flight type
    is_arrival = 'true' if flight_type == 'arrival' else 'false'
    api_url = f'https://www.hongkongairport.com/flightinfo-rest/rest/flights/past?date={date}&lang=en&cargo=true&arrival={is_arrival}'
    
    for attempt in range(max_retries):
        try:
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.json()
                rows = []
                
                # Check if the response contains actual flight data
                if not data or not data[0].get('list'):
                    return None
                
                for date_entry in data:
                    date = date_entry['date']
                    for flight in date_entry['list']:
                        time = flight['time']
                        status = flight['status']
                        
                        for f in flight['flight']:
                            flight_no = f['no']
                            airline = f['airline']
                            
                            # Handle origins/destinations
                            if flight_type == 'arrival':
                                locations = ', '.join(flight['origin'])
                                location_type = 'origin'
                            else:
                                locations = ', '.join(flight['destination']) if 'destination' in flight else ''
                                location_type = 'destination'
                            
                            row = {
                                'date': date,
                                'time': time,
                                'flight_no': flight_no,
                                'airline': airline,
                                location_type: locations,
                                'status': status,
                                'flight_type': flight_type
                            }
                            rows.append(row)
                
                if rows:
                    df = pd.DataFrame(rows)
                    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
                    df = df.sort_values('datetime', ascending=True)
                    df = df.reset_index(drop=True)
                    
                    # Order columns based on flight type
                    if flight_type == 'arrival':
                        columns = ['date', 'time', 'flight_no', 'airline', 'origin', 'status', 'flight_type', 'datetime']
                    else:
                        columns = ['date', 'time', 'flight_no', 'airline', 'destination', 'status', 'flight_type', 'datetime']
                    
                    df = df[columns]
                    return df
                return None
            else:
                print(f"Failed to retrieve {flight_type} data for {date}. Status code: {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait 2 seconds before retrying
                continue
        except Exception as e:
            print(f"Error retrieving data for {date}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait 2 seconds before retrying
            continue
    
    return None

def update_flights_database(filename='hk_flights_database_historical.csv', max_empty_days=7):
    start_date = datetime.now()
    current_date = start_date
    empty_days_count = 0
    
    # Load existing database if it exists
    if os.path.exists(filename):
        existing_df = pd.read_csv(filename)
        existing_df['datetime'] = pd.to_datetime(existing_df['datetime'])
        print(f"Loaded existing database with {len(existing_df)} records")
        
        # Find the earliest date in the database and start from there
        earliest_date = pd.to_datetime(existing_df['date'].min())
        current_date = earliest_date - timedelta(days=1)
    else:
        existing_df = pd.DataFrame()
        print("Creating new database")
    
    new_data_frames = []
    
    while empty_days_count < max_empty_days:
        date_str = current_date.strftime('%Y-%m-%d')
        print(f"\nFetching data for {date_str}...")
        
        # Get arrivals
        print("Fetching arrivals...")
        arrivals_df = get_hk_flights(date_str, 'arrival')
        
        # Get departures
        print("Fetching departures...")
        departures_df = get_hk_flights(date_str, 'departure')
        
        # Check if we got any data
        if arrivals_df is None and departures_df is None:
            empty_days_count += 1
            print(f"No data found for {date_str}. Empty days count: {empty_days_count}")
        else:
            empty_days_count = 0  # Reset counter if we get data
            if arrivals_df is not None and not arrivals_df.empty:
                new_data_frames.append(arrivals_df)
                print(f"Retrieved {len(arrivals_df)} arrival flights")
            if departures_df is not None and not departures_df.empty:
                new_data_frames.append(departures_df)
                print(f"Retrieved {len(departures_df)} departure flights")
        
        # Save intermediate results every 7 days
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
        
        # Move to previous day
        current_date -= timedelta(days=1)
    
    if new_data_frames:
        # Final save
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
        
        # Save to CSV
        combined_df.to_csv(filename, index=False)
        print(f"\nDatabase updated. Total records: {len(combined_df)}")
        
        # Print summary
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
    # Update database and get current state
    df = update_flights_database()
    
    if not df.empty:
        # print("\nFinal Database Statistics:")
        # print(f"Total number of flights: {len(df)}")
        # print(f"Number of unique airlines: {df['airline'].nunique()}")
        # print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        
        # print("\nFlights by type:")
        # print(df['flight_type'].value_counts())
        
        # print("\nMost frequent airlines:")
        # print(df['airline'].value_counts().head())
        
        # print("\nAverage daily flights:")
        daily_flights = df.groupby(['date', 'flight_type']).size().unstack(fill_value=0)
        # print(daily_flights.mean())
        
        return {"totalNumOfFlights": len(df), "numOfUniqueAirlines": df['airline'].nunique(), "dateRange": f"{df['date'].min()} to {df['date'].max()}", "flightsByType": df['flight_type'].value_counts(), "mostFreqAirlines": df['airline'].value_counts().head(), "avgDailyFlights": daily_flights.mean()}