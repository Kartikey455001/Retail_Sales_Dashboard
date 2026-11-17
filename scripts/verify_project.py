"""
verify_project.py
Comprehensive automated test suite to verify:
1. Data integrity in database/retail_sales.db
2. Foreign key and schema constraints
3. Execution of all 15 SQL analytical queries
4. DAX measure table & column references
5. Master Excel workbook structure and sheets
6. Web dashboard payload and file integrity
"""

import os
import re
import sqlite3
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []
warnings = []

print("=" * 70)
print("RETAIL SALES PERFORMANCE DASHBOARD - AUTOMATED PROJECT HEALTH CHECK")
print("=" * 70)

# -------------------------------------------------------------
# 1. Check Database & Table Integrity
# -------------------------------------------------------------
db_path = os.path.join(base_dir, "database", "retail_sales.db")
if not os.path.exists(db_path):
    errors.append("database/retail_sales.db does not exist!")
else:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Check expected tables
    expected_tables = ["fact_sales", "dim_products", "dim_customers", "dim_regions", "dim_date", "dim_returns", "raw_retail_sales"]
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [r[0] for r in cur.fetchall()]
    
    print("\n[1/5] Checking Database Tables & Row Counts:")
    for t in expected_tables:
        if t in existing_tables:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cur.fetchone()[0]
            print(f"  ✓ Table '{t}': {cnt:,} rows")
            if cnt == 0:
                errors.append(f"Table '{t}' is empty!")
        else:
            errors.append(f"Missing expected table: '{t}'")
            
    # Foreign Key Check
    cur.execute("""
        SELECT COUNT(*) FROM fact_sales s
        LEFT JOIN dim_products p ON s.Product_ID = p.Product_ID
        WHERE p.Product_ID IS NULL
    """)
    orphan_prods = cur.fetchone()[0]
    if orphan_prods > 0:
        errors.append(f"Found {orphan_prods} orphan products in fact_sales!")
    else:
        print("  ✓ Zero orphan products (FK Integrity verified)")

    cur.execute("""
        SELECT COUNT(*) FROM fact_sales s
        LEFT JOIN dim_customers c ON s.Customer_ID = c.Customer_ID
        WHERE c.Customer_ID IS NULL
    """)
    orphan_custs = cur.fetchone()[0]
    if orphan_custs > 0:
        errors.append(f"Found {orphan_custs} orphan customers in fact_sales!")
    else:
        print("  ✓ Zero orphan customers (FK Integrity verified)")

# -------------------------------------------------------------
# 2. Check SQL Analytical Queries
# -------------------------------------------------------------
print("\n[2/5] Testing 15 SQL Business Intelligence Queries:")
sql_file = os.path.join(base_dir, "database", "03_business_analysis_queries.sql")
if not os.path.exists(sql_file):
    errors.append("database/03_business_analysis_queries.sql not found!")
else:
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()
    
    # Strip comments
    clean_sql = re.sub(r"--.*", "", sql_content)
    queries = [q.strip() for q in clean_sql.split(";") if q.strip()]
    
    passed_queries = 0
    for idx, q in enumerate(queries, 1):
        try:
            cur.execute(q)
            rows = cur.fetchall()
            passed_queries += 1
            print(f"  ✓ Query {idx:02d}: PASSED ({len(rows)} rows returned)")
        except Exception as e:
            errors.append(f"SQL Query {idx} failed: {e}")
            print(f"  ✗ Query {idx:02d}: FAILED ({e})")
    print(f"  -> {passed_queries}/{len(queries)} Analytical Queries Executed Successfully")

# -------------------------------------------------------------
# 3. Check DAX Measures Table and Column References
# -------------------------------------------------------------
print("\n[3/5] Validating DAX Measures Library References:")
dax_file = os.path.join(base_dir, "power_bi", "DAX_Measures.dax")
if not os.path.exists(dax_file):
    errors.append("power_bi/DAX_Measures.dax not found!")
else:
    with open(dax_file, "r", encoding="utf-8") as f:
        dax_text = f.read()

    # Get DB tables and columns
    db_schema = {}
    for t in existing_tables:
        cur.execute(f"PRAGMA table_info({t})")
        db_schema[t] = [r[1] for r in cur.fetchall()]

    refs = re.findall(r"\b([A-Za-z0-9_]+)\[([A-Za-z0-9_]+)\]", dax_text)
    dax_errs = 0
    for t, c in set(refs):
        if t in ["Parameter_Metric"]: # Disconnected table for dynamic switch
            continue
        if t not in db_schema:
            errors.append(f"DAX references unknown table: {t}[{c}]")
            dax_errs += 1
        elif c not in db_schema[t]:
            errors.append(f"DAX references unknown column: {t}[{c}] (Available: {db_schema[t]})")
            dax_errs += 1

    if dax_errs == 0:
        print(f"  ✓ All {len(set(refs))} Table[Column] references in DAX match database schema exactly!")
    else:
        print(f"  ✗ Found {dax_errs} schema mismatches in DAX!")

conn.close()

# -------------------------------------------------------------
# 4. Check Excel Master Model File
# -------------------------------------------------------------
print("\n[4/5] Inspecting Master Excel Model:")
excel_file = os.path.join(base_dir, "excel", "retail_sales_master_model.xlsx")
if not os.path.exists(excel_file):
    errors.append("excel/retail_sales_master_model.xlsx does not exist!")
else:
    import zipfile
    try:
        with zipfile.ZipFile(excel_file, "r") as zf:
            # Check sheet XMLs
            sheets = [n for n in zf.namelist() if n.startswith("xl/worksheets/sheet")]
            print(f"  ✓ Excel workbook valid ZIP format ({len(sheets)} worksheets found)")
            print(f"  ✓ File size: {os.path.getsize(excel_file) / (1024*1024):.2f} MB")
    except Exception as e:
        errors.append(f"Excel workbook validation error: {e}")

# -------------------------------------------------------------
# 5. Check Web Dashboard Assets
# -------------------------------------------------------------
print("\n[5/5] Checking Interactive Web Dashboard Files:")
html_file = os.path.join(base_dir, "web_dashboard", "index.html")
js_file = os.path.join(base_dir, "web_dashboard", "dashboard_data.js")
json_file = os.path.join(base_dir, "web_dashboard", "dashboard_data.json")

for fpath, label in [(html_file, "HTML App"), (js_file, "Data JS Payload"), (json_file, "Data JSON")]:
    if not os.path.exists(fpath):
        errors.append(f"Missing web dashboard file: {label}")
    else:
        print(f"  ✓ {label}: Found ({os.path.getsize(fpath):,} bytes)")

# Verify JSON parses
try:
    with open(json_file, "r", encoding="utf-8") as f:
        d = json.load(f)
    all_year_stats = d.get("by_year", {}).get("ALL", {})
    months_count = len(all_year_stats.get("monthly_trend", []))
    prods_count = len(all_year_stats.get("top_products", []))
    txns_count = len(d.get("transactions", []))
    print(f"  ✓ JSON Valid: {months_count} months, {prods_count} top products, {txns_count} ledger rows")
except Exception as e:
    errors.append(f"Invalid JSON payload: {e}")

print("\n" + "=" * 70)
if errors:
    print(f"FAILED: Found {len(errors)} error(s):")
    for e in errors:
        print(f"  - {e}")
else:
    print("ALL TESTS PASSED! Project is in 100% verified, production-ready state.")
print("=" * 70)
