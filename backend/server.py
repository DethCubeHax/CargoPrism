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
def overview(origin: str = None, destination: str = None):
    df = update_flights_database()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        
        # Get CX flights for station lists
        cx_df = df[df['airline'] == 'CPA']
        
        # Get station lists based on filters
        if origin:
            # If origin is selected, get only destinations that CX flies to from this origin
            possible_destinations = sorted(cx_df[cx_df['origin'] == origin]['destination'].unique().tolist())
            possible_origins = [origin]
        elif destination:
            # If destination is selected, get only origins that CX flies from to this destination
            possible_origins = sorted(cx_df[cx_df['destination'] == destination]['origin'].unique().tolist())
            possible_destinations = [destination]
        else:
            # If no filters, get all CX origins and destinations
            possible_origins = sorted(cx_df['origin'].unique().tolist())
            possible_destinations = sorted(cx_df['destination'].unique().tolist())
        
        # Filter for last month only
        last_month = df['date'].max() - timedelta(days=30)
        df_month = df[df['date'] >= last_month]
        
        # Apply route filters if provided
        if origin:
            df_month = df_month[df_month['origin'] == origin]
        if destination:
            df_month = df_month[df_month['destination'] == destination]
        
        # Filter for CX flights only for metrics
        cx_df_month = df_month[df_month['airline'] == 'CPA']
        
        # Calculate metrics with filtered data
        total_cx_flights = len(cx_df_month)
        
        if total_cx_flights > 0:
            ontime_flights = len(cx_df_month[cx_df_month['status'] != 'Delayed'])
            ontime_percentage = (ontime_flights / total_cx_flights * 100)
            
            active_routes = len(cx_df_month[['origin', 'destination']].drop_duplicates())
            
            cancelled_flights = len(cx_df_month[cx_df_month['status'] == 'Cancelled'])
            cancellation_rate = (cancelled_flights / total_cx_flights * 100)
        else:
            ontime_percentage = 0
            active_routes = 0
            cancellation_rate = 0
        
        metrics = {
            "total_flights": total_cx_flights,
            "ontime_performance": round(ontime_percentage, 1),
            "active_routes": active_routes,
            "cancellation_rate": round(cancellation_rate, 1)
        }
        
        # Set index for existing calculations
        df_month.set_index('date', inplace=True)
        
        # Resampling and calculating weekly frequency
        cx_weekly_counts = df_month[df_month['airline'] == 'CPA'].resample('W').size()
        all_weekly_counts = df_month.resample('W').size()

        # weekly performance: cod (cancelled or delayed) flights
        condition_cx_cod = (df_month['airline'] == 'CPA') & (df_month['status'].isin(['Cancelled', 'Delayed']))
        cx_weekly_cod_flights = df_month[condition_cx_cod].resample('W').size()
        cx_cod_percentage = ((cx_weekly_cod_flights / cx_weekly_counts.replace(0, pd.NA)) * 100).fillna(0)

        weekly_cod_flights = df_month[df_month['status'].isin(['Cancelled', 'Delayed'])].resample('W').size()
        all_cod_percentage = ((weekly_cod_flights/all_weekly_counts.replace(0, pd.NA))*100).fillna(0)

        # weekly top 10
        weekly_top_10 = df_month['airline'].resample('W').apply(
            lambda x: ", ".join(f"{idx}({v})" for idx, v in x.value_counts().head(10).items())
        )
        df_split = weekly_top_10.str.split(", ", expand=True)
        column_names = [f"No.{i}" for i in range(1, df_split.shape[1] + 1)]
        df_split.columns = column_names
        weekly_top_10 = df_split
        weekly_top_10.index = weekly_top_10.index.strftime('%Y-%m-%d')

        # weekly top 5
        top_5 = df_month['airline'].resample('W').apply(lambda x: x.value_counts().head(5).to_dict().keys())
        top_5 = top_5.reset_index()
        top_5.columns = ['week', 'top_airlines']
        top_5 = top_5.explode('top_airlines')

        partial_table = df_month[['airline','status']]
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
            
            for airline, count in airlines.items():
                if airline in cod_airlines:
                    ratio = round((cod_airlines[airline] / count) * 100)
                else:
                    ratio = 0

                week_ratios.append(f"{airline}({ratio}%)")
            
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

        return {
            "metrics": metrics,
            "dates": cx_weekly_counts.index.strftime('%Y-%m-%d').tolist(),
            "CX_weekly_fq": cx_weekly_counts.tolist(),
            "ALL_weekly_fq": all_weekly_counts.tolist(),
            "CX_weekly_cod_percentage": cx_cod_percentage.tolist(),
            "ALL_weekly_cod_percentage": all_cod_percentage.tolist(),
            "weekly_top_10": weekly_top_10.to_json(orient='split'),
            "weekly_top_5": weekly_top_5.to_json(orient='split'),
            "stations": {
                "origins": possible_origins,
                "destinations": possible_destinations
            }
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
        
@app.get("/performance")
def performance():
    df = update_flights_database()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        
        # Get current month and last month
        latest_date = df['date'].max()
        current_month_start = latest_date - timedelta(days=30)
        last_month_start = current_month_start - timedelta(days=30)
        
        # Filter for current and last month
        current_df = df[df['date'] >= current_month_start]
        last_month_df = df[(df['date'] >= last_month_start) & (df['date'] < current_month_start)]
        
        # Filter for CX flights
        current_cx = current_df[current_df['airline'] == 'CPA']
        last_month_cx = last_month_df[last_month_df['airline'] == 'CPA']
        
        # Average Daily Flights
        current_daily_avg = len(current_cx) / 30
        last_daily_avg = len(last_month_cx) / 30
        daily_flights_change = ((current_daily_avg - last_daily_avg) / last_daily_avg * 100) if last_daily_avg > 0 else 0
        
        # On-time Performance (flights that are not delayed)
        current_ontime = len(current_cx[current_cx['status'] != 'Delayed'])
        current_ontime_rate = (current_ontime / len(current_cx) * 100) if len(current_cx) > 0 else 0
        
        last_ontime = len(last_month_cx[last_month_cx['status'] != 'Delayed'])
        last_ontime_rate = (last_ontime / len(last_month_cx) * 100) if len(last_month_cx) > 0 else 0
        ontime_change = current_ontime_rate - last_ontime_rate
        
        # Average Delay Time (assuming 60 min for delayed flights)
        delay_minutes = 60
        current_delayed_flights = len(current_cx[current_cx['status'] == 'Delayed'])
        last_delayed_flights = len(last_month_cx[last_month_cx['status'] == 'Delayed'])
        
        current_avg_delay = (current_delayed_flights * delay_minutes) / len(current_cx) if len(current_cx) > 0 else 0
        last_avg_delay = (last_delayed_flights * delay_minutes) / len(last_month_cx) if len(last_month_cx) > 0 else 0
        delay_change = current_avg_delay - last_avg_delay
        
        # Completion Factor (non-cancelled flights)
        current_completed = len(current_cx[current_cx['status'] != 'Cancelled'])
        current_completion = (current_completed / len(current_cx) * 100) if len(current_cx) > 0 else 0
        
        last_completed = len(last_month_cx[last_month_cx['status'] != 'Cancelled'])
        last_completion = (last_completed / len(last_month_cx) * 100) if len(last_month_cx) > 0 else 0
        completion_change = current_completion - last_completion

        # Schedule Changes Analysis - Tracking Cancellations and Resumptions
        competitor_df = df[df['airline'] != 'CPA'].copy()
        competitor_df = competitor_df[competitor_df['date'] >= current_month_start]  # Limit to last month
        schedule_changes = []
        
        # Group by flight number and find cancelled flights
        for flight_no in competitor_df['flight_no'].unique():
            flight_data = competitor_df[competitor_df['flight_no'] == flight_no].sort_values('date')
            
            # Find cancellations and next scheduled flight
            for idx, row in flight_data.iterrows():
                if row['status'] == 'Cancelled':
                    # Look for the next scheduled occurrence of this flight
                    next_flights = flight_data[flight_data['date'] > row['date']]
                    if not next_flights.empty:
                        next_scheduled = next_flights.iloc[0]
                        schedule_changes.append({
                            "date": row['date'].strftime('%Y-%m-%d'),
                            "flight_no": flight_no,
                            "airline": row['airline'],
                            "original_status": "Cancelled",
                            "new_status": f"Resumed on {next_scheduled['date'].strftime('%Y-%m-%d')}"
                        })
        
        # Sort schedule changes by date
        schedule_changes.sort(key=lambda x: x['date'], reverse=True)
        
        # Prepare the data for return
        if schedule_changes:
            schedule_data = [
                [
                    change['date'],
                    change['flight_no'],
                    change['airline'],
                    change['original_status'],
                    change['new_status']
                ] for change in schedule_changes
            ]
        else:
            schedule_data = ["None"]

        return {
            "metrics": {
                "daily_flights": {
                    "value": round(current_daily_avg, 1),
                    "change": round(daily_flights_change, 1)
                },
                "ontime_performance": {
                    "value": round(current_ontime_rate, 1),
                    "change": round(ontime_change, 1)
                },
                "avg_delay": {
                    "value": round(current_avg_delay, 1),
                    "change": round(delay_change, 1)
                },
                "completion_factor": {
                    "value": round(current_completion, 1),
                    "change": round(completion_change, 1)
                }
            },
            "schedule_changes": {
                "columns": ["Date", "Flight No", "Airline", "Original Status", "New Status"],
                "data": schedule_data
            }
        }