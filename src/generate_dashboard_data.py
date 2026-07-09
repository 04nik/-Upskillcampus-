import os
import pandas as pd
import numpy as np
import json

# Same holiday set
HOLIDAYS = {
    # 2015
    "2015-11-11", "2015-12-25",
    # 2016
    "2016-01-01", "2016-01-26", "2016-03-24", "2016-04-14", "2016-04-15",
    "2016-05-01", "2016-07-06", "2016-08-15", "2016-09-05", "2016-10-02",
    "2016-10-11", "2016-10-30", "2016-11-14", "2016-12-25",
    # 2017
    "2017-01-01", "2017-01-26", "2017-03-13", "2017-04-14", "2017-05-01",
    "2017-06-26", "2017-08-15", "2017-09-30", "2017-10-19", "2017-11-04",
    "2017-12-25"
}

def generate_dashboard_js():
    print("Generating dashboard data JS file...")
    
    # Load required data
    train = pd.read_csv(os.path.join("data", "train.csv"))
    forecast = pd.read_csv(os.path.join("data", "forecast_results.csv"))
    performance = pd.read_csv(os.path.join("data", "model_performance.csv"))
    
    # Preprocess Datetimes
    train['DateTime'] = pd.to_datetime(train['DateTime'])
    train['Date'] = train['DateTime'].dt.date
    train['Hour'] = train['DateTime'].dt.hour
    train['DayOfWeek'] = train['DateTime'].dt.dayofweek
    train['DayName'] = train['DateTime'].dt.day_name()
    train['Month'] = train['DateTime'].dt.month
    train['IsHoliday'] = train['Date'].apply(lambda d: 1 if str(d) in HOLIDAYS else 0)
    
    forecast['DateTime'] = pd.to_datetime(forecast['DateTime'])
    forecast['Date'] = forecast['DateTime'].dt.date
    forecast['Hour'] = forecast['DateTime'].dt.hour
    forecast['DayOfWeek'] = forecast['DateTime'].dt.dayofweek
    forecast['DayName'] = forecast['DateTime'].dt.day_name()
    forecast['IsHoliday'] = forecast['Date'].apply(lambda d: 1 if str(d) in HOLIDAYS else 0)
    
    # 1. Model Stats
    model_stats = performance.to_dict(orient='records')
    
    # 2. Historical Daily Averages (last 6 months: Jan 1, 2017 to June 30, 2017 for readability)
    hist_daily_df = train[train['DateTime'] >= '2017-01-01'].groupby(['Date', 'Junction'])['Vehicles'].mean().reset_index()
    hist_daily_df['Date'] = hist_daily_df['Date'].astype(str)
    
    historical_daily = {}
    for j in sorted(train['Junction'].unique()):
        j_data = hist_daily_df[hist_daily_df['Junction'] == j]
        historical_daily[int(j)] = {
            'dates': j_data['Date'].tolist(),
            'vehicles': [round(x, 1) for x in j_data['Vehicles'].tolist()]
        }
        
    # 3. Hourly Profile (Diurnal Pattern)
    hourly_df = train.groupby(['Junction', 'Hour'])['Vehicles'].mean().reset_index()
    hourly_profile = {}
    for j in sorted(train['Junction'].unique()):
        j_data = hourly_df[hourly_df['Junction'] == j]
        hourly_profile[int(j)] = [round(x, 1) for x in j_data['Vehicles'].tolist()]
        
    # 4. Weekly Profile (Weekday vs Weekend)
    weekly_df = train.groupby(['Junction', 'DayOfWeek'])['Vehicles'].mean().reset_index()
    weekly_profile = {}
    for j in sorted(train['Junction'].unique()):
        j_data = weekly_df[weekly_df['Junction'] == j].sort_values('DayOfWeek')
        weekly_profile[int(j)] = [round(x, 1) for x in j_data['Vehicles'].tolist()]
        
    # 5. Holiday vs Normal Hourly Profile
    hol_df = train.groupby(['Junction', 'IsHoliday', 'Hour'])['Vehicles'].mean().reset_index()
    holiday_profile = {}
    for j in sorted(train['Junction'].unique()):
        j_normal = hol_df[(hol_df['Junction'] == j) & (hol_df['IsHoliday'] == 0)].sort_values('Hour')
        j_holiday = hol_df[(hol_df['Junction'] == j) & (hol_df['IsHoliday'] == 1)].sort_values('Hour')
        
        holiday_profile[int(j)] = {
            'normal': [round(x, 1) for x in j_normal['Vehicles'].tolist()],
            'holiday': [round(x, 1) for x in j_holiday['Vehicles'].tolist()]
        }
        
    # 6. Future Hourly Forecast (First 7 days of test set: July 1 to July 7, 2017)
    forecast_hourly_subset = forecast[forecast['DateTime'] < '2017-07-08'].copy()
    forecast_hourly_subset['DateTimeStr'] = forecast_hourly_subset['DateTime'].dt.strftime('%Y-%m-%d %H:%M')
    
    hourly_forecast = {}
    for j in sorted(train['Junction'].unique()):
        j_data = forecast_hourly_subset[forecast_hourly_subset['Junction'] == j].sort_values('DateTime')
        hourly_forecast[int(j)] = {
            'timestamps': j_data['DateTimeStr'].tolist(),
            'vehicles': j_data['Vehicles'].tolist()
        }
        
    # 7. Future Daily Forecast (entire 4-month test set: July 1 to Oct 31, 2017)
    forecast_daily_df = forecast.groupby(['Date', 'Junction'])['Vehicles'].mean().reset_index()
    forecast_daily_df['Date'] = forecast_daily_df['Date'].astype(str)
    
    daily_forecast = {}
    for j in sorted(train['Junction'].unique()):
        j_data = forecast_daily_df[forecast_daily_df['Junction'] == j].sort_values('Date')
        daily_forecast[int(j)] = {
            'dates': j_data['Date'].tolist(),
            'vehicles': [round(x, 1) for x in j_data['Vehicles'].tolist()]
        }
        
    # Combine everything into a single dictionary
    data_dict = {
        'modelStats': model_stats,
        'historicalDaily': historical_daily,
        'hourlyProfile': hourly_profile,
        'weeklyProfile': weekly_profile,
        'holidayProfile': holiday_profile,
        'hourlyForecast': hourly_forecast,
        'dailyForecast': daily_forecast
    }
    
    # Save as JavaScript file
    os.makedirs("dashboard", exist_ok=True)
    out_path = os.path.join("dashboard", "data.js")
    with open(out_path, "w") as f:
        f.write("/* Automatically generated traffic forecasting data */\n")
        f.write("const trafficData = ")
        json.dump(data_dict, f, indent=2)
        f.write(";\n")
        
    print(f"Successfully generated {out_path}")

if __name__ == "__main__":
    generate_dashboard_js()
