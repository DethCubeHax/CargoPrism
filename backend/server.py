from fastapi import FastAPI
from flight_service import update_flights_database

app = FastAPI()

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

# @app.get("/overview")
# def overview():
#     df = update_flights_database()
    
#     if not df.empty:
#         daily_flights = df.groupby(['date', 'flight_type']).size().unstack(fill_value=0)
        
#         return {
#             "totalNumOfFlights": len(df), 
#             "totalNumOfCXDaily": df[df['airline'] == 'CX'].groupby('date').size(),  
#             "totalNumOfOtherDaily": df[df['airline'] != 'CX'].groupby('date').size(),  
#             "activeRoutes": , 
#             "cancellationRate":           
#         }
    
