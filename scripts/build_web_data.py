"""
build_web_data.py
Generates the comprehensive, reactive data payload for web_dashboard/dashboard_data.js
Pre-computes exact metrics for Year (ALL, 2023, 2024, 2025) and outputs 250 sample transactions.
"""

import os
import sqlite3
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, "database", "retail_sales.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

years = ["ALL", "2023", "2024", "2025"]
categories = ["ALL", "Technology", "Furniture", "Home & Kitchen", "Apparel & Footwear", "Office Supplies"]
regions = ["ALL", "West", "East", "Central", "South"]

stats_by_year = {}

for yr in years:
    where_s_clause = "" if yr == "ALL" else f"WHERE s.Order_Date LIKE '{yr}%'"

    # KPIs
    cur.execute(f"""
        SELECT 
            ROUND(SUM(s.Net_Revenue), 2) as tot_rev,
            ROUND(SUM(s.Profit), 2) as tot_profit,
            ROUND((SUM(s.Profit) / SUM(s.Net_Revenue)) * 100, 2) as margin_pct,
            COUNT(DISTINCT s.Order_ID) as orders,
            SUM(s.Quantity) as units,
            ROUND(SUM(s.Net_Revenue) / COUNT(DISTINCT s.Order_ID), 2) as aov,
            ROUND((SUM(s.Is_Returned) * 100.0 / COUNT(*)), 2) as return_pct
        FROM fact_sales s
        {where_s_clause}
    """)
    row = cur.fetchone()
    kpis = {
        "total_revenue": row[0],
        "total_profit": row[1],
        "profit_margin_pct": row[2],
        "total_orders": row[3],
        "units_sold": row[4],
        "avg_order_value": row[5],
        "return_rate_pct": row[6]
    }

    # Monthly Trend
    cur.execute(f"""
        SELECT SUBSTR(s.Order_Date, 1, 7) as Year_Month,
               ROUND(SUM(s.Net_Revenue), 2) as Revenue,
               ROUND(SUM(s.Profit), 2) as Profit,
               COUNT(DISTINCT s.Order_ID) as Orders
        FROM fact_sales s
        {where_s_clause}
        GROUP BY SUBSTR(s.Order_Date, 1, 7)
        ORDER BY Year_Month ASC
    """)
    cols = ["Year_Month", "Revenue", "Profit", "Orders"]
    monthly = [dict(zip(cols, r)) for r in cur.fetchall()]

    # Category Breakdown
    cur.execute(f"""
        SELECT p.Category,
               ROUND(SUM(s.Net_Revenue), 2) as Revenue,
               ROUND(SUM(s.Profit), 2) as Profit,
               COUNT(DISTINCT s.Order_ID) as Orders,
               SUM(s.Quantity) as Units,
               ROUND((SUM(s.Profit) / SUM(s.Net_Revenue)) * 100, 2) as Margin_Pct
        FROM fact_sales s
        JOIN dim_products p ON s.Product_ID = p.Product_ID
        {where_s_clause}
        GROUP BY p.Category
        ORDER BY Revenue DESC
    """)
    cols = ["Category", "Revenue", "Profit", "Orders", "Units", "Margin_Pct"]
    cats = [dict(zip(cols, r)) for r in cur.fetchall()]

    # Regional Performance
    cur.execute(f"""
        SELECT r.Region,
               ROUND(SUM(s.Net_Revenue), 2) as Revenue,
               ROUND(SUM(s.Profit), 2) as Profit,
               COUNT(DISTINCT s.Order_ID) as Orders,
               ROUND((SUM(s.Profit) / SUM(s.Net_Revenue)) * 100, 2) as Margin_Pct
        FROM fact_sales s
        JOIN dim_regions r ON s.Region_ID = r.Region_ID
        {where_s_clause}
        GROUP BY r.Region
        ORDER BY Revenue DESC
    """)
    cols = ["Region", "Revenue", "Profit", "Orders", "Margin_Pct"]
    regs = [dict(zip(cols, r)) for r in cur.fetchall()]

    # Top 10 Products
    cur.execute(f"""
        SELECT p.Product_Name, p.Category,
               ROUND(SUM(s.Net_Revenue), 2) as Revenue,
               ROUND(SUM(s.Profit), 2) as Profit,
               SUM(s.Quantity) as Units_Sold
        FROM fact_sales s
        JOIN dim_products p ON s.Product_ID = p.Product_ID
        {where_s_clause}
        GROUP BY p.Product_ID, p.Product_Name, p.Category
        ORDER BY Revenue DESC
        LIMIT 10
    """)
    cols = ["Product_Name", "Category", "Revenue", "Profit", "Units_Sold"]
    top_prods = [dict(zip(cols, r)) for r in cur.fetchall()]

    stats_by_year[yr] = {
        "kpis": kpis,
        "monthly_trend": monthly,
        "category_breakdown": cats,
        "regional_performance": regs,
        "top_products": top_prods
    }

# Also fetch 250 sample transactions for the data table
cur.execute("""
    SELECT s.Transaction_ID, s.Order_ID, s.Order_Date, c.Customer_Name, c.Segment, 
           r.Region, p.Product_Name, p.Category, s.Quantity, s.Net_Revenue, s.Profit, s.Order_Status
    FROM fact_sales s
    JOIN dim_customers c ON s.Customer_ID = c.Customer_ID
    JOIN dim_regions r ON s.Region_ID = r.Region_ID
    JOIN dim_products p ON s.Product_ID = p.Product_ID
    ORDER BY s.Order_Date DESC
    LIMIT 250
""")
cols = ["txn_id", "order_id", "order_date", "customer_name", "segment", "region", "product_name", "category", "quantity", "net_revenue", "profit", "status"]
txns = [dict(zip(cols, r)) for r in cur.fetchall()]

final_payload = {
    "by_year": stats_by_year,
    "transactions": txns
}

out_js = os.path.join(base_dir, "web_dashboard", "dashboard_data.js")
with open(out_js, "w", encoding="utf-8") as f:
    f.write("const DASHBOARD_DATA = " + json.dumps(final_payload, indent=2) + ";")

out_json = os.path.join(base_dir, "web_dashboard", "dashboard_data.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(final_payload, f, indent=2)

print(f"Generated rich interactive dataset in {out_js} and {out_json}")
conn.close()
