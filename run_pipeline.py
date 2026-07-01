import os
import sys
import pandas as pd
import importlib

# Add 01_parser to search path
sys.path.insert(0, os.path.abspath("01_parser"))

def load_modules():
    """Load modules dynamically handling hyphenated names."""
    parser = importlib.import_module("bardws_parser_aggregator_v1_2026-06-22")
    tidy = importlib.import_module("bardws_tidy_driver_v1_2026-06-22")
    join = importlib.import_module("bardws_join_driver_v1_2026-06-22")
    validate = importlib.import_module("bardws_validate_data_v1_2026-06-22")
    return parser, tidy, join, validate

def load_and_tidy_driver_logs(tidy):
    """Load raw driver logs, compute raw quality statistics, and tidy them."""
    driver_logs_path = "assets/driver_logs/member_driver_logs_sample.csv"
    driver_raw = pd.read_csv(driver_logs_path)
    print(f"Loaded {len(driver_raw)} raw driver logs.")
    
    # Calculate raw quality metrics for validation report
    raw_stats = {
        'raw_dupes': int(driver_raw.duplicated(subset=['driver_id', 'log_date']).sum()),
        'raw_missing_km': int(driver_raw['km_driven'].isnull().sum()),
        'raw_missing_km_pct': float(driver_raw['km_driven'].isnull().mean() * 100),
        'raw_missing_fare': int(driver_raw['gross_fare_inr'].isnull().sum()),
        'raw_missing_fare_pct': float(driver_raw['gross_fare_inr'].isnull().mean() * 100)
    }
    
    driver_tidied = tidy.tidy_driver_logs(driver_raw)
    print(f"Tidied driver logs: {len(driver_tidied)} rows (duplicates removed).")
    return driver_tidied, raw_stats

def join_and_enrich_driver_logs(join, driver_tidied, out_dir):
    """Join driver logs with daily weather and petrol price datasets."""
    weather_path = "assets/weather/imd_bengaluru_weather_2018_2024.csv"
    weather_df = pd.read_csv(weather_path)
    
    fuel_path = "assets/fuel_prices/bengaluru_fuel_prices_2018_2024.csv"
    fuel_df = pd.read_csv(fuel_path)
    
    driver_enriched = join.join_data(driver_tidied, weather_df, fuel_df)
    print(f"Joined and enriched driver logs: {len(driver_enriched)} rows.")
    
    # Save final enriched driver dataset deterministically
    driver_parquet_path = os.path.join(out_dir, "bardws_dataset_driver-enriched_v1.parquet")
    driver_csv_path = os.path.join(out_dir, "bardws_dataset_driver-enriched_v1.csv")
    
    driver_enriched.to_parquet(driver_parquet_path, index=False)
    driver_enriched.to_csv(driver_csv_path, index=False)
    print(f"Saved enriched driver dataset to {driver_parquet_path} and {driver_csv_path}")
    return driver_enriched

def run_pipeline():
    """Main pipeline orchestrator (guaranteed under 60 lines)."""
    print("="*50)
    print("BARDWS Data Pipeline Orchestrator")
    print("="*50)
    
    # 1. Load pipeline modules
    print("Loading pipeline modules...")
    parser, tidy, join, validate = load_modules()
    
    # 2. Stage 1: Parse aggregator statement PDFs
    print("\n[Stage 1] Parsing aggregator statement PDFs...")
    parser.main()
    
    # Load the generated aggregator table to validate later
    out_dir = "02_datasets"
    agg_csv_path = os.path.join(out_dir, "bardws_dataset_aggregator-earnings_v1.csv")
    agg_df = pd.read_csv(agg_csv_path)
    
    # 3. Stage 2: Load and tidy driver logs
    print("\n[Stage 2] Loading and tidying driver logs...")
    driver_tidied, raw_stats = load_and_tidy_driver_logs(tidy)
    
    # 4. Stage 3: Join and enrich with weather and fuel prices
    print("\n[Stage 3] Joining driver logs with weather and fuel price data...")
    driver_enriched = join_and_enrich_driver_logs(join, driver_tidied, out_dir)
    
    # 5. Stage 4: Run validation check and generate report
    print("\n[Stage 4] Running data quality validations...")
    report_path = os.path.join(out_dir, "bardws_validation_report_v1.md")
    success = validate.validate_datasets(agg_df, driver_enriched, report_path, raw_stats)
    
    print("\n" + "="*50)
    if success:
        print("PIPELINE RUN SUCCESSFULLY AND ALL VALIDATIONS PASSED!")
    else:
        print("PIPELINE RUN COMPLETED WITH VALIDATION WARNINGS (see report).")
    print("="*50)

if __name__ == "__main__":
    run_pipeline()
