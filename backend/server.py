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
        ontime_flights = len(cx_df[cx_df['status'] != 'Delayed'])
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

        # weekly top 5
        top_5 = df['airline'].resample('W').apply(lambda x: x.value_counts().head(5).to_dict().keys())
        top_5 = top_5.reset_index()
        top_5.columns = ['week', 'top_airlines']
        top_5 = top_5.explode('top_airlines')

        partial_table = df[['airline','status']]
        partial_table = partial_table.reset_index()
        partial_table['date'] = pd.to_datetime(partial_table['date'])
        partial_table['week'] = partial_table['date'] + pd.to_timedelta(6 - partial_table['date'].dt.weekday, unit='d')

        filtered_df = pd.merge(partial_table, top_5, how='inner', left_on=['week', 'airline'], right_on=['week', 'top_airlines'])
        filtered_df.drop(columns=['top_airlines'], inplace=True)

        filtered_df['week'] = pd.to_datetime(filtered_df['week'])
        filtered_df.set_index('week', inplace=True)
        weekly_top_5 = filtered_df['airline'].resample('W').apply(
            lambda x: {idx: v for idx, v in x.value_counts().head(5).items()}
        )

        filtered_df = filtered_df[filtered_df['status'].isin(['Cancelled', 'Delayed'])]

        # Resample and format the output
        weekly_top_5_cod = filtered_df['airline'].resample('W').apply(
            lambda x: {idx: v for idx, v in x.value_counts().head(5).items()}
        )

        # Convert dictionaries to Series
        weekly_top_5 = pd.Series(weekly_top_5)
        weekly_top_5_cod = pd.Series(weekly_top_5_cod)

        # Calculate ratios
        ratios = {}

        for week, airlines in weekly_top_5.items():
            week_ratios = []
            cod_airlines = weekly_top_5_cod.get(week, {})
            
            # Calculate ratios and convert to formatted string, rounding to integer
            for airline, count in airlines.items():
                if airline in cod_airlines:
                    ratio = round((cod_airlines[airline] / count) * 100)
                else:
                    ratio = 0  # Integer representation for consistency

                week_ratios.append(f"{airline}({ratio}%)")
            
            # Join all airline ratios into a single string for each week
            ratios[week] = ', '.join(week_ratios)

        # Create a Pandas Series from the ratios dictionary
        top5_ratios_series = pd.Series(ratios)
        # Split the series into a DataFrame
        df_split = top5_ratios_series.str.split(", ", expand=True)

        # Generate column names based on the number of splits
        column_names = [f"No.{i}" for i in range(1, df_split.shape[1] + 1)]
        df_split.columns = column_names
        weekly_top_5 = df_split
        # Format the index to be date strings
        weekly_top_5.index = weekly_top_5.index.strftime('%Y-%m-%d')


        # Preparing data for JSON serialization
        return {
            "metrics": metrics,
            "dates": cx_weekly_counts.index.strftime('%Y-%m-%d').tolist(),
            "CX_weekly_fq": cx_weekly_counts.tolist(),
            "ALL_weekly_fq": all_weekly_counts.tolist(),
            "CX_weekly_cod_percentage": cx_cod_percentage.tolist(),
            "ALL_weekly_cod_percentage": all_cod_percentage.tolist(),
            # Weekly Top 10 Table
            "weekly_top_10": weekly_top_10.to_json(orient='split'),
            # Weekly Top 5 Table
            "weekly_top_5": weekly_top_5.to_json(orient='split')

        }
        
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