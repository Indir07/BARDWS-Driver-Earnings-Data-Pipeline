# Data Quality Validation Report
Generated on: 2026-06-22

This report summarizes the programmatic validation of the BARDWS data pipeline deliverables.

## 1. Cleaned and Enriched Driver Dataset
*   **Total rows:** 131373
*   **Key duplicate rows (same driver + date):** 0 (Expected: 0)
*   **Flagged outliers (hours_worked = 26):** 12 (Expected: 12)
*   **Missing `km_driven` count:** 0 (Expected: 0 - imputed)
*   **Missing `gross_fare_inr` count:** 0 (Expected: 0 - imputed)

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
