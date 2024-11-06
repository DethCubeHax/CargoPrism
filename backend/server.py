from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from flight_service import update_flights_database
from datetime import datetime, timedelta
import pandas as pd

app = FastAPI()

# Add CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # More permissive - allows all origins
    allow_credentials=False,  # Changed to False since we're using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/overview")
def overview():
    df = update_flights_database()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # Resampling and calculating weekly frequency
        cx_weekly_counts = df[df['airline'] == 'CPA'].resample('W').size()
        all_weekly_counts = df.resample('W').size()
        
        # Preparing data for JSON serialization
        return {
            "dates": cx_weekly_counts.index.strftime('%Y-%m-%d').tolist(),  # Format dates as strings
            "CX_weekly_fq": cx_weekly_counts.tolist(),
            "ALL_weekly_fq": all_weekly_counts.tolist()
        }
    
