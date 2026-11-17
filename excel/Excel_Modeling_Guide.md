# Microsoft Excel & Power Query Data Modeling Guide
**Project:** E-Commerce Retail Sales Performance Analytics  
**Files:** [`retail_sales_master_model.xlsx`](file:///c:/Users/karti/OneDrive/Desktop/Retail%20Sales%20Performance%20Dashboard/excel/retail_sales_master_model.xlsx), [`power_query_etl_scripts.m`](file:///c:/Users/karti/OneDrive/Desktop/Retail%20Sales%20Performance%20Dashboard/excel/power_query_etl_scripts.m)

---

## 1. Overview of Excel Implementation

This project implements an enterprise-grade reporting framework within **Microsoft Excel** using both modern **Power Query (M ETL)** and **Power Pivot (Data Model)** capabilities. The master workbook provides a dual-layer architecture:
1. **Raw / Ingestion Layer:** Power Query imports raw, dirty transactional logs (`retail_sales_raw.csv`), sanitizes data anomalies, and loads structured tables.
2. **Analytical Presentation Layer:** An Executive KPI Dashboard featuring dynamic summary tables, KPI metrics, and category/regional breakdowns.

---

## 2. Power Query (M) ETL Pipeline Breakdown

The ETL process in [`power_query_etl_scripts.m`](file:///c:/Users/karti/OneDrive/Desktop/Retail%20Sales%20Performance%20Dashboard/excel/power_query_etl_scripts.m) is divided into 5 modular queries:

```
[Raw CSV File] 
      │
      ▼
[Staging_Raw_Sales] ── (Trimming, Multi-format Date Parsing, Discount Standardizing)
      │
      ├───► [Fact_Sales]     (Transaction metrics: Revenue, Costs, Profit, Margin)
      ├───► [Dim_Product]    (Deduplicated SKUs, Categories, Unit Costs & Prices)
      ├───► [Dim_Customer]   (Deduplicated Customer Profiles, Segments, Geography)
      └───► [Dim_Date]       (Dynamic Calendar Generator: Year, Quarter, Month, Weekday)
```

### Key Applied ETL Steps:
1. **Multi-Format Date Parsing:**
   Handles ISO (`YYYY-MM-DD`), US (`MM/DD/YYYY`), and UK/European (`DD-MM-YYYY`) dates safely without throwing errors:
   ```powerquery
   try Date.FromText(rawDate, "en-US") 
   otherwise try Date.FromText(rawDate, "en-GB")
   otherwise Date.FromText(rawDate)
   ```
2. **Discount Column Normalization:**
   Converts mixed percentage strings (e.g., `"15%"`) and decimals (`0.15`) into clean floats (`0.15`):
   ```powerquery
   if Text.EndsWith(d, "%") then Number.FromText(Text.TrimEnd(d, "%")) / 100.0 else Number.FromText(d)
   ```
3. **Financial Feature Engineering:**
   - $\text{Gross Revenue} = \text{Quantity} \times \text{Unit Price}$
   - $\text{Discount Amount} = \text{Gross Revenue} \times \text{Discount Rate}$
   - $\text{Net Revenue} = \text{Gross Revenue} - \text{Discount Amount}$
   - $\text{Total Cost} = (\text{Quantity} \times \text{Unit Cost}) + \text{Shipping Fee}$
   - $\text{Profit} = \text{Net Revenue} - \text{Total Cost}$
   - $\text{Profit Margin \%} = \frac{\text{Profit}}{\text{Net Revenue}}$

---

## 3. Master Excel Workbook Architecture (`retail_sales_master_model.xlsx`)

The workbook contains seven sheets:

| Sheet Name | Type | Contents & Purpose |
| :--- | :--- | :--- |
| **Executive Dashboard** | Presentation | High-level KPI cards, Category breakdown table, Regional distribution table, conditional formatting. |
| **Fact_Sales** | Data Table | Cleaned transaction lines ($20,886$ records) with order dates, quantities, net revenues, profits, and delivery days. |
| **Dim_Products** | Dimension | Product catalog ($47$ SKUs across Technology, Furniture, Office Supplies, Home & Kitchen, Apparel). |
| **Dim_Customers** | Dimension | $750$ unique customer profiles with segment, primary region, state, city, and account creation dates. |
| **Dim_Regions** | Dimension | Regional lookup ($4$ US regions, market tiers, regional directors). |
| **Dim_Date** | Dimension | Calendar dimension ($1,096$ days from 2023-01-01 to 2025-12-31). |
| **Dim_Returns** | Fact/Audit | $1,371$ return audit logs with return dates, reasons, and refund amounts. |

---

## 4. Key Formulas & Analytical Techniques in Excel

### A. Dynamic Array & Lookup Formulas
- **XLOOKUP for Dimensional Joining:**
  ```excel
  =XLOOKUP([@Product_ID], Dim_Products[Product_ID], Dim_Products[Category], "Unknown")
  ```
- **Dynamic Unique Filter for Slicing:**
  ```excel
  =SORT(UNIQUE(Fact_Sales[Sales_Channel]))
  ```
- **Conditional Financial Aggregations:**
  - Net Revenue by Category:
    ```excel
    =SUMIFS(Fact_Sales[Net_Revenue], Fact_Sales[Product_ID], Dim_Products[Product_ID])
    ```
  - Weighted Average Order Value (AOV):
    ```excel
    =SUM(Fact_Sales[Net_Revenue]) / DISTINCTCOUNT(Fact_Sales[Order_ID])
    ```

### B. Excel Number Formatting & Presentation
- **Currency:** `$#,##0.00`
- **Percentage:** `0.0%`
- **Large KPI Format:** `$#,##0,,\M` (Displaying millions e.g. `$15.3M`)
- **KPI Card Design:** Clean cards with subtle gray borders (`#D9D9D9`), navy headers (`#1F4E79`), and accent trend indicators.

---

## 5. How to Load and Refresh in Excel / Power Pivot
1. Open Excel $\rightarrow$ **Data Tab** $\rightarrow$ **Get Data** $\rightarrow$ **From Other Sources** $\rightarrow$ **Blank Query**.
2. Open the **Advanced Editor** and paste the M-code from [`power_query_etl_scripts.m`](file:///c:/Users/karti/OneDrive/Desktop/Retail%20Sales%20Performance%20Dashboard/excel/power_query_etl_scripts.m).
3. Click **Close & Load To...** $\rightarrow$ Select **Add this data to the Data Model**.
4. In the Power Pivot window, drag `Customer_ID`, `Product_ID`, and `Region_ID` to establish $1:\text{Many}$ relationships with `Fact_Sales`.
