# Data Quality Validation Report
Generated on: 2026-07-01

This report summarizes the programmatic validation of the BARDWS data pipeline deliverables.

## 1. Driver Logs Quality Metrics (Before vs. After Cleaning)

| Metric | Raw (Before ETL) | Cleaned (After ETL) | Expected Target | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Duplicate Rows (driver+date)** | 80 | 0 | 0 | PASSED |
| **Missing `km_driven` count** | 1971 (1.5%) | 0 | 0 (imputed) | PASSED |
| **Missing `gross_fare_inr` count** | 788 (0.6%) | 0 | 0 (imputed) | PASSED |
| **Flagged Outliers (hours_worked = 26)** | — | 12 | 12 | PASSED |

*   **Total Cleaned Rows:** 131373

### Enriched Data Highlights
*   **Temperature Range:** 10.7°C to 34.3°C
*   **Maximum Rainfall Day:** 38.8 mm
*   **Average IndianOil Petrol Price:** ₹82.31/L

## 2. Normalized Aggregator Earnings Dataset
*   **Total parsed rows:** 265
*   **Aggregator breakdown:**
*   **Uber:** 86 rows
*   **Rapido:** 83 rows
*   **Namma Yatri:** 81 rows
*   **Ola:** 15 rows
*   **Missing transaction dates for daily aggregators (Uber, Rapido, Namma Yatri):** 0 (Expected: 0)

## 3. Data Integrity & Validation Conclusion
**PASSED** - The cleaned and joined datasets meet all data quality and formatting criteria specified in the PRD.
