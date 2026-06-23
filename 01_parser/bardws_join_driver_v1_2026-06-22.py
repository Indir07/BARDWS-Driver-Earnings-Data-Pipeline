import pandas as pd

def join_data(driver_df, weather_df, fuel_df):
    """Enrich driver logs with weather and IndianOil Petrol prices."""
    # Ensure dates are in YYYY-MM-DD string format
    driver_df['log_date'] = pd.to_datetime(driver_df['log_date']).dt.strftime('%Y-%m-%d')
    weather_df['date'] = pd.to_datetime(weather_df['date']).dt.strftime('%Y-%m-%d')
    fuel_df['date'] = pd.to_datetime(fuel_df['date']).dt.strftime('%Y-%m-%d')
    
    # Filter fuel price for IndianOil Petrol in Bengaluru
    fuel_filtered = fuel_df[
        (fuel_df['oil_company'] == 'IndianOil') & 
        (fuel_df['fuel_type'] == 'Petrol')
    ].copy()
    
    fuel_subset = fuel_filtered[['date', 'retail_price_inr_per_litre']].copy()
    fuel_subset = fuel_subset.drop_duplicates(subset=['date'])
    
    # Weather subset columns
    weather_subset = weather_df[['date', 'rainfall_mm', 'temp_max_c', 'temp_min_c', 'humidity_pct']].copy()
    weather_subset = weather_subset.drop_duplicates(subset=['date'])
    
    # Perform joins
    merged = driver_df.merge(weather_subset, left_on='log_date', right_on='date', how='left')
    merged = merged.drop(columns=['date'])
    
    merged = merged.merge(fuel_subset, left_on='log_date', right_on='date', how='left')
    merged = merged.drop(columns=['date'])
    
    # Return sorted by driver_id and log_date
    return merged.sort_values(by=['driver_id', 'log_date']).reset_index(drop=True)
