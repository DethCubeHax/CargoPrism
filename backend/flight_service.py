from datetime import datetime, timedelta
import pandas as pd
import os
from data_utils import get_airport_data, get_hk_flights

def update_flights_database(filename='hk_flights_database_historical.csv', max_empty_days=7):
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