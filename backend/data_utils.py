import json
import pandas as pd
from datetime import datetime, timedelta
import requests
import os

def get_airport_data():
    """Load airport data from iata.json"""
    try:
        with open('iata.json', encoding='utf-8') as f:
            airports = json.load(f)
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
                        
                        origin = 'HKG'
                        destination = 'HKG'
                        origin_name = airport_data.get('HKG', 'Hong Kong International Airport')
                        destination_name = airport_data.get('HKG', 'Hong Kong International Airport')
                        
                        if flight_type == 'arrival':
                            if flight['origin']:
                                origin = flight['origin'][0]
                                origin_name = airport_data.get(origin, f'Unknown ({origin})')
                        else:
                            if 'destination' in flight and flight['destination']:
                                destination = flight['destination'][0]
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