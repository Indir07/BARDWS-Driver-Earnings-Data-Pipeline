import os
import sys
import datetime
import pandas as pd
import importlib

# Add 01_parser to search path
sys.path.insert(0, os.path.abspath("01_parser"))

def run_pipeline():
    print("="*50)
    print("BARDWS Data Pipeline Orchestrator")
    print("="*50)
    
    # 1. Dynamically import pipeline modules (handling hyphenated names)
    print("Loading pipeline modules...")
    parser = importlib.import_module("bardws_parser_aggregator_v1_2026-06-22")
    tidy = importlib.import_module("bardws_tidy_driver_v1_2026-06-22")
    join = importlib.import_module("bardws_join_driver_v1_2026-06-22")
    validate = importlib.import_module("bardws_validate_data_v1_2026-06-22")
    
    # 2. Stage 1: Parse aggregator statement PDFs
    print("\n[Stage 1] Parsing aggregator statement PDFs...")
    parser.main()
    
    # Load the generated aggregator table to validate later
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    out_dir = "02_datasets"
    agg_csv_path = os.path.join(out_dir, f"bardws_dataset_aggregator-earnings_v1_{today_str}.csv")
    agg_df = pd.read_csv(agg_csv_path)
    
    # 3. Stage 2: Tidy driver logs
    print("\n[Stage 2] Loading and tidying driver logs...")
    driver_logs_path = "driver_logs/member_driver_logs_sample.csv"
    if not os.path.exists(driver_logs_path):
        driver_logs_path = os.path.join("assets", driver_logs_path)
    
    driver_raw = pd.read_csv(driver_logs_path)
    print(f"Loaded {len(driver_raw)} raw driver logs.")
    driver_tidied = tidy.tidy_driver_logs(driver_raw)
    print(f"Tidied driver logs: {len(driver_tidied)} rows (duplicates removed).")
    
    # 4. Stage 3: Join and enrich with weather and fuel prices
    print("\n[Stage 3] Joining driver logs with weather and fuel price data...")
    weather_path = "weather/imd_bengaluru_weather_2018_2024.csv"
    if not os.path.exists(weather_path):
        weather_path = os.path.join("assets", weather_path)
    weather_df = pd.read_csv(weather_path)
    
    fuel_path = "fuel_prices/bengaluru_fuel_prices_2018_2024.csv"
    if not os.path.exists(fuel_path):
        fuel_path = os.path.join("assets", fuel_path)
    fuel_df = pd.read_csv(fuel_path)
    
    driver_enriched = join.join_data(driver_tidied, weather_df, fuel_df)
    print(f"Joined and enriched driver logs: {len(driver_enriched)} rows.")
    
    # Save final enriched driver dataset
    driver_parquet_path = os.path.join(out_dir, f"bardws_dataset_driver-enriched_v1_{today_str}.parquet")
    driver_csv_path = os.path.join(out_dir, f"bardws_dataset_driver-enriched_v1_{today_str}.csv")
    
    driver_enriched.to_parquet(driver_parquet_path, index=False)
    driver_enriched.to_csv(driver_csv_path, index=False)
    print(f"Saved enriched driver dataset to {driver_parquet_path} and {driver_csv_path}")
    
    # 5. Stage 4: Run validation check and generate report
    print("\n[Stage 4] Running data quality validations...")
    report_path = os.path.join(out_dir, f"bardws_validation_report_v1_{today_str}.md")
    success = validate.validate_datasets(agg_df, driver_enriched, report_path)
    
    print("\n" + "="*50)
    if success:
        print("PIPELINE RUN SUCCESSFULLY AND ALL VALIDATIONS PASSED!")
    else:
        print("PIPELINE RUN COMPLETED WITH VALIDATION WARNINGS (see report).")
    print("="*50)

if __name__ == "__main__":
    run_pipeline()
