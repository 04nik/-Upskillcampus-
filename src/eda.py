import os
import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for professional-looking plots
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.style.use('seaborn-v0_8-whitegrid')

# Define holiday list for 2015, 2016, and 2017
HOLIDAYS = {
    # 2015
    "2015-11-11", # Diwali
    "2015-12-25", # Christmas
    # 2016
    "2016-01-01", # New Year
    "2016-01-26", # Republic Day
    "2016-03-24", # Holi
    "2016-04-14", # Ambedkar Jayanti
    "2016-04-15", # Good Friday
    "2016-05-01", # May Day / Labor Day
    "2016-07-06", # Eid-ul-Fitr
    "2016-08-15", # Independence Day
    "2016-09-05", # Ganesh Chaturthi
    "2016-10-02", # Gandhi Jayanti
    "2016-10-11", # Dussehra
    "2016-10-30", # Diwali
    "2016-11-14", # Guru Nanak Jayanti
    "2016-12-25", # Christmas
    # 2017
    "2017-01-01", # New Year
    "2017-01-26", # Republic Day
    "2017-03-13", # Holi
    "2017-04-14", # Good Friday
    "2017-05-01", # Labor Day
    "2017-06-26", # Eid-ul-Fitr
    "2017-08-15", # Independence Day
    "2017-09-30", # Dussehra
    "2017-10-19", # Diwali
    "2017-11-04", # Guru Nanak Jayanti
    "2017-12-25"  # Christmas
}

def run_eda():
    print("Starting Exploratory Data Analysis...")
    
    # Load dataset
    train_path = os.path.join("data", "train.csv")
    if not os.path.exists(train_path):
        raise FileNotFoundError(f"Dataset not found at {train_path}. Run download_data.py first.")
        
    df = pd.read_csv(train_path)
    print(f"Dataset loaded successfully. Shape: {df.shape}")
    
    # Convert DateTime
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df['Date'] = df['DateTime'].dt.date
    df['Hour'] = df['DateTime'].dt.hour
    df['DayOfWeek'] = df['DateTime'].dt.dayofweek # Monday=0, Sunday=6
    df['Month'] = df['DateTime'].dt.month
    df['Year'] = df['DateTime'].dt.year
    df['DayName'] = df['DateTime'].dt.day_name()
    
    # Add Holiday column
    df['IsHoliday'] = df['Date'].apply(lambda d: 1 if str(d) in HOLIDAYS else 0)
    
    print("\n--- Basic Statistics per Junction ---")
    junction_stats = df.groupby('Junction')['Vehicles'].agg(['count', 'min', 'max', 'mean', 'median', 'std'])
    print(junction_stats)
    
    # Create plots directory
    os.makedirs("plots", exist_ok=True)
    
    # Plot 1: Traffic Trend Over Time (Daily Average)
    plt.figure(figsize=(14, 7))
    daily_traffic = df.groupby(['Date', 'Junction'])['Vehicles'].mean().reset_index()
    for junction in sorted(df['Junction'].unique()):
        j_data = daily_traffic[daily_traffic['Junction'] == junction]
        plt.plot(j_data['Date'], j_data['Vehicles'], label=f'Junction {junction}', alpha=0.8, linewidth=1.5)
    
    plt.title('Daily Average Traffic Flow Over Time (2015 - 2017)', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Average Number of Vehicles / Hour', fontsize=12)
    plt.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "1_traffic_trend.png"), dpi=300)
    plt.close()
    print("Saved plots/1_traffic_trend.png")
    
    # Plot 2: Diurnal (Hourly) Traffic Profile
    plt.figure(figsize=(12, 6))
    hourly_traffic = df.groupby(['Hour', 'Junction'])['Vehicles'].mean().reset_index()
    sns.lineplot(data=hourly_traffic, x='Hour', y='Vehicles', hue='Junction', palette='tab10', marker='o', linewidth=2)
    plt.title('Hourly Traffic Profile (Diurnal Pattern)', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('Hour of the Day (24h format)', fontsize=12)
    plt.ylabel('Average Number of Vehicles', fontsize=12)
    plt.xticks(range(0, 24))
    plt.legend(title='Junction', frameon=True, fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "2_hourly_pattern.png"), dpi=300)
    plt.close()
    print("Saved plots/2_hourly_pattern.png")
    
    # Plot 3: Weekly Traffic Profile (Day of Week)
    plt.figure(figsize=(12, 6))
    weekly_traffic = df.groupby(['DayOfWeek', 'DayName', 'Junction'])['Vehicles'].mean().reset_index()
    weekly_traffic = weekly_traffic.sort_values('DayOfWeek')
    sns.lineplot(data=weekly_traffic, x='DayName', y='Vehicles', hue='Junction', palette='tab10', marker='s', linewidth=2)
    plt.title('Weekly Traffic Profile (Weekday vs Weekend)', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('Day of the Week', fontsize=12)
    plt.ylabel('Average Number of Vehicles', fontsize=12)
    plt.legend(title='Junction', frameon=True, fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "3_weekly_pattern.png"), dpi=300)
    plt.close()
    print("Saved plots/3_weekly_pattern.png")
    
    # Plot 4: Monthly Traffic Profile (Seasonality)
    plt.figure(figsize=(12, 6))
    monthly_traffic = df.groupby(['Month', 'Junction'])['Vehicles'].mean().reset_index()
    sns.barplot(data=monthly_traffic, x='Month', y='Vehicles', hue='Junction', palette='tab10')
    plt.title('Monthly Traffic Volume Distribution', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('Month (1 = Jan, 12 = Dec)', fontsize=12)
    plt.ylabel('Average Number of Vehicles', fontsize=12)
    plt.legend(title='Junction', frameon=True, fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "4_monthly_pattern.png"), dpi=300)
    plt.close()
    print("Saved plots/4_monthly_pattern.png")
    
    # Plot 5: Holiday vs. Normal Days Traffic
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='Junction', y='Vehicles', hue='IsHoliday', palette={0: '#3498db', 1: '#e74c3c'})
    plt.title('Traffic Volume Comparison: Normal Days vs. Holidays', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('Junction', fontsize=12)
    plt.ylabel('Vehicles / Hour', fontsize=12)
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles, ['Normal Day', 'Holiday'], title='Day Type', frameon=True, fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "5_holiday_impact.png"), dpi=300)
    plt.close()
    print("Saved plots/5_holiday_impact.png")
    
    print("\nEDA completed successfully! Check the generated plots in the 'plots/' directory.")

if __name__ == "__main__":
    run_eda()
