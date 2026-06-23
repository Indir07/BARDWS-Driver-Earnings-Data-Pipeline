import os
import re
import datetime
import pypdf
import pandas as pd

# Global configuration
LOG_FILE = "parse_failures.log"

def log_failure(filename, reason):
    """Log a parsing failure to a log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] File: {filename} | Reason: {reason}\n")

def clean_num(val):
    """Clean a string value to parse it as float/int."""
    val_clean = val.replace(',', '').replace('₹', '').replace('Rs.', '').strip()
    if val_clean.startswith('+'):
        val_clean = val_clean[1:].strip()
    elif val_clean.startswith('-'):
        val_clean = '-' + val_clean[1:].strip()
    return val_clean

def parse_val(val, target_type):
    """Parse string to target_type (int or float)."""
    clean_str = clean_num(val)
    if target_type == int:
        return int(clean_str)
    return float(clean_str)

def get_month_range(month_name, year):
    """Get the start and end dates for a given month and year."""
    month_map = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    month = month_map.get(month_name.lower().strip())
    if not month:
        return None, None
    year = int(year)
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year}-12-31"
    else:
        end_date = (datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    return start_date, end_date

def extract_dates(text, agg_type):
    """Extract statement_period_start and statement_period_end from text."""
    if agg_type == "Namma Yatri":
        match = re.search(r'\b(September|December|October)\s+(\d{4})\b', text)
        if match:
            return get_month_range(match.group(1), match.group(2))
    elif agg_type == "Ola":
        match = re.search(r'Month:\s*([A-Za-z]+)\s+(\d{4})', text)
        if match:
            return get_month_range(match.group(1), match.group(2))
    elif agg_type == "Rapido":
        match = re.search(r'Period:\s*([A-Za-z]+)\s+(\d{4})', text)
        if match:
            return get_month_range(match.group(1), match.group(2))
    elif agg_type == "Uber":
        match = re.search(r'Statement period:\s*([\d-]+)\s+to\s+([\d-]+)', text)
        if match:
            start_dt = datetime.datetime.strptime(match.group(1), "%d-%m-%Y").strftime("%Y-%m-%d")
            end_dt = datetime.datetime.strptime(match.group(2), "%d-%m-%Y").strftime("%Y-%m-%d")
            return start_dt, end_dt
    return None, None

def parse_ny_rows(lines, filename, start_date, end_date):
    """Parse Namma Yatri data rows."""
    rows = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if re.match(r'^\d{2}/\d{2}/\d{4}$', line):
            if i + 5 < len(lines):
                try:
                    txn_date = datetime.datetime.strptime(line, "%d/%m/%Y").strftime("%Y-%m-%d")
                    trips = parse_val(lines[i+1], int)
                    rider_pay = parse_val(lines[i+2], float)
                    sub = parse_val(lines[i+3], float)
                    gst = parse_val(lines[i+4], float)
                    net = parse_val(lines[i+5], float)
                    rows.append({
                        'aggregator': 'Namma Yatri',
                        'statement_period_start': start_date,
                        'statement_period_end': end_date,
                        'txn_date': txn_date,
                        'trips': trips,
                        'rider_payment_inr': rider_pay,
                        'platform_fee_inr': round(sub + gst, 2),
                        'net_earnings_inr': net
                    })
                except Exception as e:
                    log_failure(filename, f"Failed parsing Namma Yatri row at line {i}: {e}")
                i += 6
                continue
        i += 1
    return rows

def parse_ola_rows(lines, filename, start_date, end_date):
    """Parse Ola data rows."""
    rows = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if re.match(r'^(Week \d|W\d-\d{2}/\d{4})$', line):
            if i + 5 < len(lines):
                try:
                    trips = parse_val(lines[i+1], int)
                    earnings = parse_val(lines[i+2], float)
                    comm = parse_val(lines[i+3], float)
                    incentive = parse_val(lines[i+4], float)
                    payout = parse_val(lines[i+5], float)
                    rows.append({
                        'aggregator': 'Ola',
                        'statement_period_start': start_date,
                        'statement_period_end': end_date,
                        'txn_date': None,
                        'trips': trips,
                        'rider_payment_inr': earnings,
                        'platform_fee_inr': comm,
                        'net_earnings_inr': payout
                    })
                except Exception as e:
                    log_failure(filename, f"Failed parsing Ola row at line {i}: {e}")
                i += 6
                continue
        i += 1
    return rows

def parse_rapido_rows(lines, filename, start_date, end_date, has_tips):
    """Parse Rapido data rows."""
    rows = []
    i = 0
    year = datetime.datetime.strptime(start_date, "%Y-%m-%d").year
    stride = 6 if has_tips else 5
    while i < len(lines):
        line = lines[i].strip()
        if re.match(r'^\d{2} [A-Za-z]{3}$', line):
            if i + stride - 1 < len(lines):
                try:
                    day_str = line
                    parts = day_str.split()
                    day = int(parts[0])
                    month_name = parts[1][:3]
                    dt = datetime.datetime.strptime(f"{day} {month_name} {year}", "%d %b %Y")
                    txn_date = dt.strftime('%Y-%m-%d')
                    
                    orders = parse_val(lines[i+1], int)
                    cust_paid = parse_val(lines[i+2], float)
                    rapido_fee = parse_val(lines[i+3], float)
                    
                    if has_tips:
                        tips = parse_val(lines[i+4], float)
                        earning = parse_val(lines[i+5], float)
                    else:
                        earning = parse_val(lines[i+4], float)
                    
                    rows.append({
                        'aggregator': 'Rapido',
                        'statement_period_start': start_date,
                        'statement_period_end': end_date,
                        'txn_date': txn_date,
                        'trips': orders,
                        'rider_payment_inr': cust_paid,
                        'platform_fee_inr': rapido_fee,
                        'net_earnings_inr': earning
                    })
                except Exception as e:
                    log_failure(filename, f"Failed parsing Rapido row at line {i}: {e}")
                i += stride
                continue
        i += 1
    return rows

def parse_uber_rows(lines, filename, start_date, end_date, has_booking_fee):
    """Parse Uber data rows."""
    rows = []
    i = 0
    stride = 6 if has_booking_fee else 5
    while i < len(lines):
        line = lines[i].strip()
        if re.match(r'^(\d{2}-\d{2}-\d{4}|\d{4}-\d{2}-\d{2})$', line):
            if i + stride - 1 < len(lines):
                try:
                    if '-' in line:
                        parts = line.split('-')
                        if len(parts[0]) == 4:
                            txn_date = line
                        else:
                            txn_date = datetime.datetime.strptime(line, "%d-%m-%Y").strftime("%Y-%m-%d")
                    else:
                        raise ValueError(f"Unknown date format: {line}")
                    
                    trips = parse_val(lines[i+1], int)
                    rider_pay = parse_val(lines[i+2], float)
                    service_fee = parse_val(lines[i+3], float)
                    
                    if has_booking_fee:
                        booking_fee = parse_val(lines[i+4], float)
                        net = parse_val(lines[i+5], float)
                        platform_fee = round(service_fee + booking_fee, 2)
                    else:
                        net = parse_val(lines[i+4], float)
                        platform_fee = service_fee
                    
                    rows.append({
                        'aggregator': 'Uber',
                        'statement_period_start': start_date,
                        'statement_period_end': end_date,
                        'txn_date': txn_date,
                        'trips': trips,
                        'rider_payment_inr': rider_pay,
                        'platform_fee_inr': platform_fee,
                        'net_earnings_inr': net
                      })
                except Exception as e:
                    log_failure(filename, f"Failed parsing Uber row at line {i}: {e}")
                i += stride
                continue
        i += 1
    return rows

def parse_pdf(file_path):
    """Determine the aggregator and parse the file."""
    filename = os.path.basename(file_path)
    reader = pypdf.PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    agg_type = None
    if "Namma Yatri" in text:
        agg_type = "Namma Yatri"
    elif "OLA" in text:
        agg_type = "Ola"
    elif "rapido" in text:
        agg_type = "Rapido"
    elif "Uber" in text:
        agg_type = "Uber"
    
    if not agg_type:
        log_failure(filename, "Could not determine aggregator type from PDF text")
        return []
    
    start_date, end_date = extract_dates(text, agg_type)
    if not start_date or not end_date:
        log_failure(filename, f"Could not extract statement period dates for {agg_type}")
        return []
    
    if agg_type == "Namma Yatri":
        return parse_ny_rows(lines, filename, start_date, end_date)
    elif agg_type == "Ola":
        return parse_ola_rows(lines, filename, start_date, end_date)
    elif agg_type == "Rapido":
        has_tips = "Tips (₹)" in text
        return parse_rapido_rows(lines, filename, start_date, end_date, has_tips)
    elif agg_type == "Uber":
        has_bf = "Booking fee (₹)" in text
        return parse_uber_rows(lines, filename, start_date, end_date, has_bf)
    return []

def main():
    """Main runner for aggregator PDF parser."""
    pdf_dir = "aggregator_pdfs"
    if not os.path.exists(pdf_dir) and os.path.exists(os.path.join("assets", pdf_dir)):
        pdf_dir = os.path.join("assets", pdf_dir)
    
    if not os.path.exists(pdf_dir):
        print(f"Error: Directory {pdf_dir} not found.")
        return
    
    all_rows = []
    for f in sorted(os.listdir(pdf_dir)):
        if f.endswith(".pdf"):
            file_path = os.path.join(pdf_dir, f)
            print(f"Parsing {file_path}...")
            rows = parse_pdf(file_path)
            all_rows.extend(rows)
            print(f"Extracted {len(rows)} rows.")
    
    if not all_rows:
        print("No rows parsed!")
        return
    
    df = pd.DataFrame(all_rows)
    
    # Ensure directories exist
    out_dir = "02_datasets"
    os.makedirs(out_dir, exist_ok=True)
    
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    parquet_path = os.path.join(out_dir, f"bardws_dataset_aggregator-earnings_v1_{today_str}.parquet")
    csv_path = os.path.join(out_dir, f"bardws_dataset_aggregator-earnings_v1_{today_str}.csv")
    
    df.to_parquet(parquet_path, index=False)
    df.to_csv(csv_path, index=False)
    print(f"Saved {len(df)} rows to {parquet_path} and {csv_path}")

if __name__ == "__main__":
    main()
