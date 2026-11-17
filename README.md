# Retail Sales Performance Dashboard
### Power BI | SQL | Microsoft Excel | DAX | Star Schema Data Modeling

![Power BI](https://img.shields.io/badge/Power_BI-Desktop-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![SQL](https://img.shields.io/badge/SQL-ETL_%26_Analytics-CC292B?style=for-the-badge&logo=sqlite&logoColor=white)
![Excel](https://img.shields.io/badge/MS_Excel-Power_Query_%26_Pivot-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)
![DAX](https://img.shields.io/badge/DAX-Time_Intelligence-0078D4?style=for-the-badge&logo=microsoft&logoColor=white)
![Python](https://img.shields.io/badge/Python-Data_Engineering-3776AB?style=for-the-badge&logo=python&logoColor=white)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Kartikey455001%2FRetail__Sales__Dashboard-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Kartikey455001/Retail_Sales_Dashboard)

---

## 📌 Project Overview

This end-to-end Business Intelligence project provides an enterprise-grade performance analytics suite for an e-commerce retail organization spanning **3 full fiscal years (2023 – 2025)**. 

The project encompasses the complete data analytics lifecycle:
1. **Data Ingestion & Cleaning:** Extracted raw transactional logs with anomalies (inconsistent date formats, unnormalized strings, missing values, discount formatting), and engineered a robust **SQL & Power Query (M) ETL pipeline** to clean, deduplicate, and standardize the data.
2. **Dimensional Data Modeling:** Designed an optimized **Star Schema** data warehouse comprising 1 Fact table (`fact_sales`) and 5 Dimension tables (`dim_products`, `dim_customers`, `dim_regions`, `dim_date`, and `dim_returns`).
3. **Advanced DAX Measures:** Authored **35+ production DAX calculations** spanning core financial KPIs, time intelligence (YoY, MoM, YTD, SPLY, 3-month rolling averages), customer intelligence, and dynamic measure switching.
4. **Interactive Dashboard Design:** Structured a multi-page Power BI dashboard architecture and built a companion **interactive web application** (`web_dashboard/index.html`) and an **Excel analytical workbook** (`excel/retail_sales_master_model.xlsx`) for instant executive reporting.

---

## 🎯 Executive Scorecard Highlights (2023 - 2025)

| Metric | Result | YoY Trend / Status | Description |
| :--- | :---: | :---: | :--- |
| **Total Net Revenue** | **\$15,334,377.74** | **▲ +16.9% YoY** | Net sales after promotions & discounts across 3 fiscal years |
| **Total Net Profit** | **\$5,997,927.49** | **▲ +17.2% YoY** | Bottom-line gross profit after COGS and shipping logistics |
| **Profit Margin %** | **39.11%** | **Target: 35.0%** | Maintained disciplined margin stability across all 36 months |
| **Total Orders** | **14,904** | **▲ +16.2% YoY** | 20,886 line items fulfilled across retail & corporate accounts |
| **Units Sold** | **32,894** | 2.21 units/order | Physical items delivered across 47 distinct SKUs |
| **Average Order Value (AOV)** | **\$1,028.88** | **▲ +$12.40 YoY** | Driven by strong corporate computing and furniture orders |
| **Overall Return Rate %** | **6.56%** | 1,371 Returns | Footwear & Apparel showed highest returns (13.2%) |

---

## 🏗️ System Architecture & Workflow

```
┌────────────────────────────────────────────────────────────────────────┐
│                        RAW DATA SOURCES                                │
│  • Transaction Logs (retail_sales_raw.csv - 20k+ rows)                 │
│  • Quirks: Mixed date formats, percentage strings, unnormalized text   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        DATA CLEANING & ETL                             │
│  • SQL ETL Pipeline: 02_data_cleaning_etl.sql (CTEs, Window Dedupe)    │
│  • Power Query M Script: power_query_etl_scripts.m                     │
│  • Feature Engineering: Net Revenue, COGS, Profit, Delivery SLAs       │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      STAR SCHEMA DATA WAREHOUSE                        │
│  • Fact_Sales (Transactions, Quantities, Revenues, Costs, Margins)     │
│  • Dim_Products (47 SKUs, Categories, Sub-Categories, Unit Pricing)    │
│  • Dim_Customers (750 Accounts, Segments, Geographic Profiles)         │
│  • Dim_Date (1,096 Days, Calendars, Quarters, Months, Fiscal Periods)  │
│  • Dim_Regions (West, East, Central, South, Regional Leadership)       │
│  • Dim_Returns (1,371 Audited Returns, Root Causes, Restocking Fees)   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
        ┌──────────────────────────┴──────────────────────────┐
        ▼                                                     ▼
┌──────────────────────────────────┐        ┌──────────────────────────────────┐
│         POWER BI & DAX           │        │         MS EXCEL & WEB           │
│ • 35+ DAX Measures               │        │ • retail_sales_master_model.xlsx │
│ • Time Intelligence (YoY, SPLY)  │        │ • Executive KPI Summary Dashboard│
│ • Category & Regional Reporting  │        │ • Interactive Live Web Dashboard │
│ • Drill-Through & Tooltips       │        │   (web_dashboard/index.html)     │
└──────────────────────────────────┘        └──────────────────────────────────┘
```

---

## 🗂️ Project Repository Structure

```
Retail Sales Performance Dashboard/
│
├── README.md                              <- Flagship project documentation & resume guide
│
├── data/
│   ├── raw/
│   │   └── retail_sales_raw.csv           <- Raw transactional data with realistic quirks
│   └── cleaned/
│       ├── fact_sales.csv                 <- Transformed transactional fact table
│       ├── dim_products.csv               <- Product dimension table (47 SKUs)
│       ├── dim_customers.csv              <- Customer dimension table (750 accounts)
│       ├── dim_regions.csv                <- Regional management dimension
│       ├── dim_date.csv                   <- Conformed date calendar dimension
│       └── dim_returns.csv                <- Audited product returns & refund fees
│
├── database/
│   ├── retail_sales.db                    <- Pre-loaded SQLite database (Zero setup required)
│   ├── 01_schema_ddl.sql                  <- Star Schema DDL, constraints & indexes
│   ├── 02_data_cleaning_etl.sql           <- SQL ETL script (deduplication, date parsing, DQA)
│   └── 03_business_analysis_queries.sql   <- 15 analytical SQL queries (CTEs, Window functions)
│
├── excel/
│   ├── retail_sales_master_model.xlsx     <- Styled Master Excel model with KPI summary tabs
│   ├── power_query_etl_scripts.m          <- Production M-code for Excel/Power BI Power Query
│   └── Excel_Modeling_Guide.md            <- Detailed documentation on Excel formulas & Pivot model
│
├── power_bi/
│   ├── DAX_Measures.dax                   <- 35+ production-grade DAX measures with folders
│   ├── Data_Model_Architecture.md         <- Star Schema specs, cardinality, and relationships
│   └── Dashboard_Design_Guide.md          <- Canvas layout, color palette, cards, and visual setup
│
├── web_dashboard/
│   ├── index.html                         <- Live interactive standalone dashboard (Browser ready)
│   ├── dashboard_data.js                  <- Embedded data payload (No CORS restrictions)
│   └── dashboard_data.json                <- Raw JSON aggregation payload
│
├── reports/
│   └── Executive_Business_Report.md       <- 10-page caliber executive business intelligence report
│
└── scripts/
    └── generate_data.py                   <- Deterministic data generation & modeling engine
```

---

## 💻 SQL ETL & Business Queries Showcase

### 1. Data Cleaning & Multi-Format Date Parsing (SQL ETL)
In [`database/02_data_cleaning_etl.sql`](file:///c:/Users/karti/OneDrive/Desktop/Retail%20Sales%20Performance%20Dashboard/database/02_data_cleaning_etl.sql), the script normalizes dates across US (`MM/DD/YYYY`), ISO (`YYYY-MM-DD`), and UK (`DD-MM-YYYY`) formats while deduplicating rows:
```sql
WITH Deduplicated_Staging AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY Txn_ID 
               ORDER BY Order_Date DESC
           ) AS dedupe_rank
    FROM raw_retail_sales
)
SELECT 
    TRIM(Txn_ID) AS Transaction_ID,
    TRIM(Order_ID) AS Order_ID,
    CASE 
        WHEN Order_Date LIKE '____-__-__' THEN Order_Date
        WHEN Order_Date LIKE '__/__/____' THEN 
            SUBSTR(Order_Date, 7, 4) || '-' || SUBSTR(Order_Date, 1, 2) || '-' || SUBSTR(Order_Date, 4, 2)
        WHEN Order_Date LIKE '__-__-____' THEN 
            SUBSTR(Order_Date, 7, 4) || '-' || SUBSTR(Order_Date, 4, 2) || '-' || SUBSTR(Order_Date, 1, 2)
        ELSE Order_Date
    END AS Clean_Order_Date,
    ROUND((Quantity * Unit_Price) - ((Quantity * Unit_Price) * Clean_Discount_Rate), 2) AS Net_Revenue,
    ROUND(Net_Revenue - Total_Cost, 2) AS Profit
FROM Deduplicated_Staging
WHERE dedupe_rank = 1;
```

### 2. Year-over-Year (YoY) Growth with Window Functions (`LAG`)
```sql
WITH Annual_Sales AS (
    SELECT 
        d.Year,
        ROUND(SUM(s.Net_Revenue), 2) AS Net_Revenue,
        ROUND(SUM(s.Profit), 2)      AS Net_Profit
    FROM fact_sales s
    JOIN dim_date d ON s.Order_Date = d.Full_Date
    GROUP BY d.Year
)
SELECT 
    Year,
    Net_Revenue,
    LAG(Net_Revenue, 1) OVER (ORDER BY Year) AS Prior_Year_Revenue,
    ROUND(
        ((Net_Revenue - LAG(Net_Revenue, 1) OVER (ORDER BY Year)) / 
        LAG(Net_Revenue, 1) OVER (ORDER BY Year)) * 100, 2
    ) AS YoY_Revenue_Growth_Pct
FROM Annual_Sales;
```

### 3. Customer RFM Segmentation via Window Quantiles (`NTILE`)
In Query 8 of [`database/03_business_analysis_queries.sql`](file:///c:/Users/karti/OneDrive/Desktop/Retail%20Sales%20Performance%20Dashboard/database/03_business_analysis_queries.sql), customers are segmented into Champions, Loyal Regulars, and Churn Risks based on Recency, Frequency, and Monetary scores.

---

## ⚡ Power BI DAX Measures Library Showcase

All measures in [`power_bi/DAX_Measures.dax`](file:///c:/Users/karti/OneDrive/Desktop/Retail%20Sales%20Performance%20Dashboard/power_bi/DAX_Measures.dax) are organized into structured display folders:

### 1. Core Financial Measures
```dax
-- Total Net Revenue
Total Net Revenue = 
SUM(fact_sales[Net_Revenue])

-- Total Net Profit
Total Profit = 
[Total Net Revenue] - [Total Cost]

-- Profit Margin %
Profit Margin % = 
DIVIDE([Total Profit], [Total Net Revenue], 0)

-- Average Order Value (AOV)
Average Order Value = 
DIVIDE([Total Net Revenue], [Total Orders], 0)
```

### 2. Time Intelligence (YoY & SPLY)
```dax
-- Same Period Last Year (SPLY)
Revenue PY = 
CALCULATE(
    [Total Net Revenue],
    SAMEPERIODLASTYEAR(dim_date[Full_Date])
)

-- YoY Revenue Growth %
YoY Revenue Growth % = 
DIVIDE([Total Net Revenue] - [Revenue PY], [Revenue PY], 0)

-- 3-Month Rolling Average Revenue
Rolling 3-Month Revenue = 
AVERAGEX(
    DATESINPERIOD(
        dim_date[Full_Date],
        LASTDATE(dim_date[Full_Date]),
        -3,
        MONTH
    ),
    [Total Net Revenue]
)
```

### 3. Ranking & Top N Dynamic Filters
```dax
-- Dynamic Product Revenue Ranking
Product Revenue Rank = 
IF(
    ISINSCOPE(dim_products[Product_Name]),
    RANKX(
        ALLSELECTED(dim_products[Product_Name]),
        [Total Net Revenue],
        ,
        DESC,
        DENSE
    ),
    BLANK()
)
```

---

## 📊 Interactive Dashboard Walkthrough

### 1. Standalone Live Web Dashboard (`web_dashboard/index.html`)
- **Direct Browser Execution:** Open [`web_dashboard/index.html`](file:///c:/Users/karti/OneDrive/Desktop/Retail%20Sales%20Performance%20Dashboard/web_dashboard/index.html) in Chrome, Edge, or Safari without needing a local web server.
- **Interactive Slicers:** Filter instantly by Year (All, 2025, 2024, 2023), Category, and Region.
- **Dynamic Visuals:** Includes 36-month trend combo charts, donut category share, top 10 best-selling SKUs, regional margin bars, and a live searchable transaction log with status badges.
- **Theme Support:** Features built-in Light and Dark mode toggling.

### 2. Master Microsoft Excel Workbook (`excel/retail_sales_master_model.xlsx`)
- **Executive Dashboard Sheet:** KPI Scorecards formatted in corporate navy and subtle borders.
- **Pivot Summaries:** Pre-configured Category Breakdown and Regional Distribution tables.
- **Data Model Sheets:** Complete `Fact_Sales`, `Dim_Products`, `Dim_Customers`, `Dim_Regions`, `Dim_Date`, and `Dim_Returns` sheets formatted as official Excel Tables.

---

## 💡 Key Business Insights & Strategic Recommendations

Detailed in [`reports/Executive_Business_Report.md`](file:///c:/Users/karti/OneDrive/Desktop/Retail%20Sales%20Performance%20Dashboard/reports/Executive_Business_Report.md):

1. **Technology is the Primary Growth Engine (47.1% Share | \$7.22M):** High-ticket laptops and audio gear dominate sales. Recommendation: bundle high-margin accessories (`TEC-ACC-001` Logitech mouse, docks) to increase cart margin by +1.8%.
2. **Apparel Return Rate Anomaly (13.2% vs 6.6% Benchmark):** Sizing discrepancies account for 32% of returns. Recommendation: Implement AI virtual sizing guides to cut return rates to <8%, recovering **\$75,000 annually** in reverse logistics costs.
3. **Heavy Freight Surcharges in Furniture (33.55% Margin):** Bulky standing desks and chairs suffer higher freight costs. Recommendation: Renegotiate regional LTL carrier contracts in West and Central regions to recapture **+2.4% in gross margin**.
4. **Core Account Dominance:** 89% of enterprise revenue is generated by repeat buyers (Core Regulars + Super VIP Loyalists). Recommendation: Deploy automated VIP concierge retention programs for accounts inactive for >120 days.

---

## 🚀 How to Run and Explore the Project

### 1. View the Interactive Dashboard Immediately
Double-click [`web_dashboard/index.html`](file:///c:/Users/karti/OneDrive/Desktop/Retail%20Sales%20Performance%20Dashboard/web_dashboard/index.html) to interact with the full dashboard in your web browser.

### 2. Inspect and Query the SQLite Database
Run analytical SQL queries directly using SQLite or Python:
```powershell
python -c "import sqlite3; conn = sqlite3.connect('database/retail_sales.db'); print('Total Rows in Fact_Sales:', conn.execute('SELECT COUNT(*) FROM fact_sales').fetchone()[0])"
```

### 3. Open the Excel Master Model
Open [`excel/retail_sales_master_model.xlsx`](file:///c:/Users/karti/OneDrive/Desktop/Retail%20Sales%20Performance%20Dashboard/excel/retail_sales_master_model.xlsx) in Microsoft Excel to explore the Executive Dashboard, formulas, and dimensional tables.

### 4. Build or Customize in Power BI Desktop
1. Open **Power BI Desktop**.
2. Select **Get Data** $\rightarrow$ **Text/CSV** and select the files in `data/cleaned/`.
3. In Model View, verify relationships as outlined in [`power_bi/Data_Model_Architecture.md`](file:///c:/Users/karti/OneDrive/Desktop/Retail%20Sales%20Performance%20Dashboard/power_bi/Data_Model_Architecture.md).
4. Create a new measure table `_Measures` and paste the formulas from [`power_bi/DAX_Measures.dax`](file:///c:/Users/karti/OneDrive/Desktop/Retail%20Sales%20Performance%20Dashboard/power_bi/DAX_Measures.dax).
5. Assemble visual pages following [`power_bi/Dashboard_Design_Guide.md`](file:///c:/Users/karti/OneDrive/Desktop/Retail%20Sales%20Performance%20Dashboard/power_bi/Dashboard_Design_Guide.md).

---

## 💼 Resume Bullet Points & Interview Talking Points

### Resume Bullet Points
- **Retail Sales Performance Dashboard | Power BI, SQL, MS Excel, DAX**
  - Engineered an end-to-end analytics pipeline extracting, transforming, and cleaning 20,000+ e-commerce transaction records using SQL CTEs and Power Query (M).
  - Modeled a high-performance Star Schema data warehouse with 1 Fact and 5 Dimension tables, optimizing filter propagation and active/inactive date relationships.
  - Developed 35+ DAX measures (Time Intelligence, YoY/MoM growth, RFM segmentation, dynamic SWITCH metrics) tracking \$15.33M in net revenue and 39.1% profit margin.
  - Designed an interactive multi-page Power BI dashboard and companion web application delivering real-time executive visibility into sales channels, product profitability, and regional delivery SLAs.
  - Authored a comprehensive C-suite business report uncovering high return rates in apparel (13.2%) and proposed carrier contract renegotiations projected to save \$174K annually.

### Key Interview Talking Points
- **Q: How did you handle data quality issues in the raw dataset?**  
  *A:* "I constructed a multi-stage SQL and Power Query ETL pipeline that used `ROW_NUMBER()` window functions to eliminate duplicate transactions, regex/substring parsing to standardize mixed date formats (`MM/DD/YYYY` and `YYYY-MM-DD`), and dynamic conditional logic to parse dirty discount strings like `'15%'` into clean decimals."
- **Q: How did you approach the data model in Power BI?**  
  *A:* "I implemented a strict Star Schema architecture with single-direction cross-filtering to optimize query performance and eliminate circular dependencies. For role-playing date relationships between `Order_Date` and `Ship_Date`, I kept `Order_Date` active and used DAX `USERELATIONSHIP` for ship date analysis."
- **Q: What was the most impactful business insight you uncovered?**  
  *A:* "While Technology accounted for 47% of revenue, our RFM analysis revealed that 89% of revenue came from repeat buyers, and Apparel suffered from a 13.2% return rate driven by sizing issues. I formulated a 5-point strategic plan including AI virtual sizing and LTL freight optimization for furniture that recovers ~\$174K in margin."
