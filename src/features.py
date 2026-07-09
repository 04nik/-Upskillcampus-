import os
import pandas as pd
import numpy as np

# Use the same holiday set for consistency
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

def extract_base_features(df):
    """
    Extracts basic datetime features and holiday indicators.
    """
    df = df.copy()
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df['Date'] = df['DateTime'].dt.date
    df['Hour'] = df['DateTime'].dt.hour
    df['DayOfWeek'] = df['DateTime'].dt.dayofweek
    df['Day'] = df['DateTime'].dt.day
    df['Month'] = df['DateTime'].dt.month
    df['Year'] = df['DateTime'].dt.year
    df['DayOfYear'] = df['DateTime'].dt.dayofyear
    df['IsWeekend'] = df['DayOfWeek'].apply(lambda x: 1 if x in (5, 6) else 0)
    df['IsHoliday'] = df['Date'].apply(lambda d: 1 if str(d) in HOLIDAYS else 0)
    return df

def generate_features(train_df, test_df):
    """
    Performs feature engineering by extracting calendar variables and mapping
    historical traffic profiles (target encodings) from the training set.
    """
    print("Extracting base features...")
    train = extract_base_features(train_df)
    test = extract_base_features(test_df)
    
    print("Computing historical traffic profiles (target encodings)...")
    
    # 1. Junction + Hour mean
    jh_mean = train.groupby(['Junction', 'Hour'])['Vehicles'].mean().rename('jh_mean').reset_index()
    
    # 2. Junction + DayOfWeek mean
    jdow_mean = train.groupby(['Junction', 'DayOfWeek'])['Vehicles'].mean().rename('jdow_mean').reset_index()
    
    # 3. Junction + Hour + DayOfWeek mean (captures weekly rush-hour cycles)
    jhdow_mean = train.groupby(['Junction', 'Hour', 'DayOfWeek'])['Vehicles'].mean().rename('jhdow_mean').reset_index()
    
    # 4. Junction + Hour + IsHoliday mean (captures how holiday traffic shifts by hour)
    jhhol_mean = train.groupby(['Junction', 'Hour', 'IsHoliday'])['Vehicles'].mean().rename('jhhol_mean').reset_index()
    
    # Map encodings to Train
    train = train.merge(jh_mean, on=['Junction', 'Hour'], how='left')
    train = train.merge(jdow_mean, on=['Junction', 'DayOfWeek'], how='left')
    train = train.merge(jhdow_mean, on=['Junction', 'Hour', 'DayOfWeek'], how='left')
    train = train.merge(jhhol_mean, on=['Junction', 'Hour', 'IsHoliday'], how='left')
    
    # Map encodings to Test
    test = test.merge(jh_mean, on=['Junction', 'Hour'], how='left')
    test = test.merge(jdow_mean, on=['Junction', 'DayOfWeek'], how='left')
    test = test.merge(jhdow_mean, on=['Junction', 'Hour', 'DayOfWeek'], how='left')
    test = test.merge(jhhol_mean, on=['Junction', 'Hour', 'IsHoliday'], how='left')
    
    # Fill any missing values in test set profiles with simple junction averages
    j_mean = train.groupby('Junction')['Vehicles'].mean().rename('j_mean').reset_index()
    
    train = train.merge(j_mean, on='Junction', how='left')
    test = test.merge(j_mean, on='Junction', how='left')
    
    for col in ['jh_mean', 'jdow_mean', 'jhdow_mean', 'jhhol_mean']:
        train[col] = train[col].fillna(train['j_mean'])
        test[col] = test[col].fillna(test['j_mean'])
        
    # Drop intermediate columns
    cols_to_drop = ['Date', 'j_mean']
    train = train.drop(columns=cols_to_drop)
    test = test.drop(columns=cols_to_drop)
    
    return train, test

if __name__ == "__main__":
    # Test feature generation with mock data if run directly
    print("Features script ready.")
