import pandas as pd
import numpy as np

def compute_driver_medians(df):
    """Compute median speed and median fare per ride for each driver."""
    # Speed: km_driven / hours_worked on active days
    df_active = df[(df['km_driven'] > 0) & (df['hours_worked'] > 0)].copy()
    df_active['km_per_hour'] = df_active['km_driven'] / df_active['hours_worked']
    driver_median_speed = df_active.groupby('driver_id')['km_per_hour'].median()
    global_median_speed = df_active['km_per_hour'].median()
    
    # Fare per ride: gross_fare_inr / rides_completed on active days
    df_fare = df[(df['gross_fare_inr'] > 0) & (df['rides_completed'] > 0)].copy()
    df_fare['fare_per_ride'] = df_fare['gross_fare_inr'] / df_fare['rides_completed']
    driver_median_fare = df_fare.groupby('driver_id')['fare_per_ride'].median()
    global_median_fare = df_fare['fare_per_ride'].median()
    
    return driver_median_speed, global_median_speed, driver_median_fare, global_median_fare

def impute_missing_values(df, driver_median_speed, global_median_speed, driver_median_fare, global_median_fare):
    """Impute missing km_driven and gross_fare_inr according to documented rules."""
    # Impute km_driven
    null_km = df['km_driven'].isnull()
    speeds = df['driver_id'].map(driver_median_speed).fillna(global_median_speed)
    df.loc[null_km, 'km_driven'] = df.loc[null_km, 'hours_worked'] * speeds
    
    # Set to 0 if it's a sick day or hours_worked is 0
    df.loc[df['sick_day'] == 1, 'km_driven'] = 0.0
    df.loc[df['hours_worked'] == 0, 'km_driven'] = 0.0
    
    # Impute gross_fare_inr
    null_fare = df['gross_fare_inr'].isnull()
    fares = df['driver_id'].map(driver_median_fare).fillna(global_median_fare)
    df.loc[null_fare, 'gross_fare_inr'] = df.loc[null_fare, 'rides_completed'] * fares
    
    # Set to 0 if it's a sick day or hours_worked is 0
    df.loc[df['sick_day'] == 1, 'gross_fare_inr'] = 0.0
    df.loc[df['hours_worked'] == 0, 'gross_fare_inr'] = 0.0
    
    return df

def tidy_driver_logs(df):
    """Tidy the driver logs: drop duplicates, flag outliers, impute missing values."""
    # 1. Remove 80 fully duplicated rows
    df_clean = df.drop_duplicates(keep='first').copy()
    
    # 2. Flag 12 outlier rows (hours_worked == 26)
    df_clean['hours_outlier'] = (df_clean['hours_worked'] == 26).astype(int)
    
    # 3. Impute missing values
    driver_median_speed, global_median_speed, driver_median_fare, global_median_fare = compute_driver_medians(df_clean)
    df_clean = impute_missing_values(
        df_clean, driver_median_speed, global_median_speed, 
        driver_median_fare, global_median_fare
    )
    
    # Round decimal fields to 2 decimal places
    df_clean['km_driven'] = df_clean['km_driven'].round(2)
    df_clean['gross_fare_inr'] = df_clean['gross_fare_inr'].round(2)
    
    return df_clean
