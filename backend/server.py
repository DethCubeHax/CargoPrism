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
        
        # Filter for last month only
        last_month = df['date'].max() - timedelta(days=30)
        df_month = df[df['date'] >= last_month]
        
        # Filter for CX flights only
        cx_df = df_month[df_month['airline'] == 'CPA']
        
        # Calculate metrics
        total_cx_flights = len(cx_df)
        
        # Calculate on-time performance
        ontime_flights = len(cx_df[cx_df['status'] != 'Cancelled'])
        ontime_percentage = (ontime_flights / total_cx_flights * 100) if total_cx_flights > 0 else 0
        
        # Calculate active routes (unique origin-destination pairs)
        active_routes = len(cx_df[['origin', 'destination']].drop_duplicates())
        
        # Calculate cancellation rate
        cancelled_flights = len(cx_df[cx_df['status'] == 'Cancelled'])
        cancellation_rate = (cancelled_flights / total_cx_flights * 100) if total_cx_flights > 0 else 0
        
        # Add these metrics to a dictionary
        metrics = {
            "total_flights": total_cx_flights,
            "ontime_performance": round(ontime_percentage, 1),
            "active_routes": active_routes,
            "cancellation_rate": round(cancellation_rate, 1)
        }
        
        # Set index for existing calculations
        df.set_index('date', inplace=True)
        
        # Resampling and calculating weekly frequency
        cx_weekly_counts = df[df['airline'] == 'CPA'].resample('W').size()
        all_weekly_counts = df.resample('W').size()

        # weekly perfomance: cod (cancelled or delayed) flights
        condition_cx_cod = (df['airline'] == 'CPA') & (df['status'].isin(['Cancelled', 'Delayed']))
        cx_weekly_cod_flights = df[condition_cx_cod].resample('W').size()
        cx_cod_percentage = ((cx_weekly_cod_flights / cx_weekly_counts.replace(0, pd.NA)) * 100).fillna(0)

        weekly_cod_flights = df[df['status'].isin(['Cancelled', 'Delayed'])].resample('W').size()
        all_cod_percentage = ((weekly_cod_flights/all_weekly_counts.replace(0, pd.NA))*100).fillna(0)

        # weekly top 10
        weekly_top_10 = df['airline'].resample('W').apply(
            lambda x: ", ".join(f"{idx}({v})" for idx, v in x.value_counts().head(10).items())
        )
        df_split = weekly_top_10.str.split(", ", expand=True)
        column_names = [f"No.{i}" for i in range(1, df_split.shape[1] + 1)]
        df_split.columns = column_names
        weekly_top_10 = df_split
        weekly_top_10.index = weekly_top_10.index.strftime('%Y-%m-%d')

        # Return all data including new metrics
        return {
            "metrics": metrics,
            "dates": cx_weekly_counts.index.strftime('%Y-%m-%d').tolist(),
            "CX_weekly_fq": cx_weekly_counts.tolist(),
            "ALL_weekly_fq": all_weekly_counts.tolist(),
            "CX_weekly_cod_percentage": cx_cod_percentage.tolist(),
            "ALL_weekly_cod_percentage": all_cod_percentage.tolist(),
            "weekly_top_10": weekly_top_10.to_json(orient='split')
        }