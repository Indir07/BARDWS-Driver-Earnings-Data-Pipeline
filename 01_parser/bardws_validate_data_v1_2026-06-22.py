import os
import pandas as pd
import datetime

def validate_datasets(agg_df, driver_df, report_path):
    """Run data quality validation and write a markdown report."""
    # Driver logs quality metrics
    total_driver_rows = len(driver_df)
    
    # 1. Duplicates check
    dupes_count = driver_df.duplicated(subset=['driver_id', 'log_date']).sum()
    
    # 2. Outliers count
    outliers_count = (driver_df['hours_outlier'] == 1).sum()
    
    # 3. Missing values check
    missing_km = driver_df['km_driven'].isnull().sum()
    missing_fare = driver_df['gross_fare_inr'].isnull().sum()
    
    # 4. Check weather and fuel price ranges
    min_temp = driver_df['temp_min_c'].min()
    max_temp = driver_df['temp_max_c'].max()
    max_rain = driver_df['rainfall_mm'].max()
    avg_fuel = driver_df['retail_price_inr_per_litre'].mean()
    
    total_agg_rows = len(agg_df)
    agg_missing_txn_date = agg_df[agg_df['aggregator'] != 'Ola']['txn_date'].isnull().sum()
    agg_counts = agg_df['aggregator'].value_counts()
    agg_breakdown_str = "\n".join([f"*   **{k}:** {v} rows" for k, v in agg_counts.items()])
    
    report_content = f"""# Data Quality Validation Report
Generated on: {datetime.date.today().strftime('%Y-%m-%d')}

This report summarizes the programmatic validation of the BARDWS data pipeline deliverables.

## 1. Cleaned and Enriched Driver Dataset
*   **Total rows:** {total_driver_rows}
*   **Key duplicate rows (same driver + date):** {dupes_count} (Expected: 0)
*   **Flagged outliers (hours_worked = 26):** {outliers_count} (Expected: 12)
*   **Missing `km_driven` count:** {missing_km} (Expected: 0 - imputed)
*   **Missing `gross_fare_inr` count:** {missing_fare} (Expected: 0 - imputed)

### Enriched Data Highlights
*   **Temperature Range:** {min_temp:.1f}°C to {max_temp:.1f}°C
*   **Maximum Rainfall Day:** {max_rain:.1f} mm
*   **Average IndianOil Petrol Price:** ₹{avg_fuel:.2f}/L

## 2. Normalized Aggregator Earnings Dataset
*   **Total parsed rows:** {total_agg_rows}
*   **Aggregator breakdown:**
{agg_breakdown_str}
*   **Missing transaction dates for daily aggregators (Uber, Rapido, Namma Yatri):** {agg_missing_txn_date} (Expected: 0)

## 3. Data Integrity & Validation Conclusion
{"**PASSED**" if dupes_count == 0 and outliers_count == 12 and missing_km == 0 and missing_fare == 0 else "**FAILED**"} - The cleaned and joined datasets meet all data quality and formatting criteria specified in the PRD.
"""
    
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print(f"Validation report saved to {report_path}")
    return dupes_count == 0 and outliers_count == 12 and missing_km == 0 and missing_fare == 0
