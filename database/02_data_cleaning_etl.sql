-- ============================================================================
-- 02_data_cleaning_etl.sql
-- Retail Sales Performance - SQL Cleaning, Transformation & Star Schema ETL
-- Demonstrates: Deduplication, Date Parsing, String Standardization,
-- Type Casting, Feature Engineering, and Data Quality Assurance (DQA).
-- ============================================================================

-- ----------------------------------------------------------------------------
-- STEP 1: INSPECT RAW STAGING DATA FOR QUALITY ANOMALIES
-- ----------------------------------------------------------------------------
-- Check for null values, duplicates, and anomalous formats in staging
SELECT 
    COUNT(*) AS total_raw_records,
    COUNT(DISTINCT Txn_ID) AS unique_txns,
    SUM(CASE WHEN Cust_ID IS NULL OR Cust_ID = '' THEN 1 ELSE 0 END) AS missing_cust_ids,
    SUM(CASE WHEN Prod_ID IS NULL OR Prod_ID = '' THEN 1 ELSE 0 END) AS missing_prod_ids,
    SUM(CASE WHEN Quantity <= 0 THEN 1 ELSE 0 END) AS invalid_quantities,
    SUM(CASE WHEN Unit_Price <= 0 THEN 1 ELSE 0 END) AS invalid_prices
FROM raw_retail_sales;

-- ----------------------------------------------------------------------------
-- STEP 2: CTE PIPELINE FOR DEDUPLICATION AND CLEANING
-- ----------------------------------------------------------------------------
WITH Deduplicated_Staging AS (
    -- Remove any duplicate transaction rows using window function
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY Txn_ID 
               ORDER BY Order_Date DESC
           ) AS dedupe_rank
    FROM raw_retail_sales
),
Standardized_Staging AS (
    SELECT 
        -- Key Identifiers
        TRIM(Txn_ID) AS Transaction_ID,
        TRIM(Order_ID) AS Order_ID,
        TRIM(Cust_ID) AS Customer_ID,
        TRIM(Prod_ID) AS Product_ID,
        
        -- Standardize Customer Attributes (Trim trailing spaces & Initcap/Proper Case)
        TRIM(Cust_Name) AS Customer_Name,
        CASE 
            WHEN LOWER(TRIM(Cust_Segment)) = 'consumer' THEN 'Consumer'
            WHEN LOWER(TRIM(Cust_Segment)) = 'corporate' THEN 'Corporate'
            WHEN LOWER(TRIM(Cust_Segment)) = 'home office' THEN 'Home Office'
            WHEN LOWER(TRIM(Cust_Segment)) = 'small business' THEN 'Small Business'
            ELSE 'Consumer'
        END AS Segment,
        
        -- Geographic Attributes
        TRIM(Country) AS Country,
        TRIM(State) AS State,
        TRIM(City) AS City,
        TRIM(Postal_Code) AS Postal_Code,
        TRIM(Region) AS Region,
        CASE 
            WHEN TRIM(Region) = 'West' THEN 'REG-W'
            WHEN TRIM(Region) = 'East' THEN 'REG-E'
            WHEN TRIM(Region) = 'Central' THEN 'REG-C'
            WHEN TRIM(Region) = 'South' THEN 'REG-S'
            ELSE 'REG-UNK'
        END AS Region_ID,

        -- Standardize Product Attributes
        TRIM(Prod_Name) AS Product_Name,
        TRIM(Category) AS Category,
        TRIM(Sub_Category) AS Sub_Category,

        -- Standardize Multi-Format Dates
        -- Handles ISO (YYYY-MM-DD), US (MM/DD/YYYY), and European (DD-MM-YYYY)
        CASE 
            WHEN Order_Date LIKE '____-__-__' THEN Order_Date
            WHEN Order_Date LIKE '__/__/____' THEN 
                SUBSTR(Order_Date, 7, 4) || '-' || SUBSTR(Order_Date, 1, 2) || '-' || SUBSTR(Order_Date, 4, 2)
            WHEN Order_Date LIKE '__-__-____' THEN 
                SUBSTR(Order_Date, 7, 4) || '-' || SUBSTR(Order_Date, 4, 2) || '-' || SUBSTR(Order_Date, 1, 2)
            ELSE Order_Date
        END AS Clean_Order_Date,

        CASE 
            WHEN Ship_Date IS NULL OR Ship_Date = '' THEN NULL
            WHEN Ship_Date LIKE '____-__-__' THEN Ship_Date
            WHEN Ship_Date LIKE '__/__/____' THEN 
                SUBSTR(Ship_Date, 7, 4) || '-' || SUBSTR(Ship_Date, 1, 2) || '-' || SUBSTR(Ship_Date, 4, 2)
            ELSE Ship_Date
        END AS Clean_Ship_Date,

        -- Clean Discount (Convert percentages e.g., '15%' -> 0.15, '0.1' -> 0.10)
        CASE 
            WHEN Discount LIKE '%#%' ESCAPE '#' THEN 0.00
            WHEN Discount LIKE '%%' AND Discount LIKE '%!%%' ESCAPE '!' THEN 
                CAST(REPLACE(Discount, '%', '') AS NUMERIC) / 100.0
            ELSE 
                COALESCE(CAST(Discount AS NUMERIC), 0.00)
        END AS Clean_Discount_Rate,

        -- Numeric Metrics & Types
        CAST(Quantity AS INTEGER) AS Quantity,
        CAST(Unit_Cost AS NUMERIC(10, 2)) AS Unit_Cost,
        CAST(Unit_Price AS NUMERIC(10, 2)) AS Unit_Price,
        CAST(Shipping_Fee AS NUMERIC(10, 2)) AS Shipping_Cost,

        -- Operational Metadata
        TRIM(Channel) AS Sales_Channel,
        TRIM(Ship_Mode) AS Ship_Mode,
        TRIM(Payment_Type) AS Payment_Method,
        TRIM(Order_Status) AS Order_Status,
        TRIM(Return_Reason) AS Return_Reason,
        CASE WHEN TRIM(Order_Status) = 'Returned' THEN 1 ELSE 0 END AS Is_Returned
    FROM Deduplicated_Staging
    WHERE dedupe_rank = 1
),
Calculated_Financials AS (
    SELECT 
        *,
        -- Gross Revenue = Quantity * Unit Price
        ROUND(Quantity * Unit_Price, 2) AS Gross_Revenue,
        
        -- Discount Amount = Gross Revenue * Discount Rate
        ROUND((Quantity * Unit_Price) * Clean_Discount_Rate, 2) AS Discount_Amount,
        
        -- Net Revenue = Gross Revenue - Discount Amount
        ROUND((Quantity * Unit_Price) - ((Quantity * Unit_Price) * Clean_Discount_Rate), 2) AS Net_Revenue,
        
        -- Total Cost = (Quantity * Unit Cost) + Shipping Fee
        ROUND((Quantity * Unit_Cost) + Shipping_Cost, 2) AS Total_Cost
    FROM Standardized_Staging
),
Final_Enriched_Sales AS (
    SELECT 
        *,
        -- Profit = Net Revenue - Total Cost
        ROUND(Net_Revenue - Total_Cost, 2) AS Profit,
        
        -- Profit Margin % = Profit / Net Revenue (Safe division)
        ROUND(CASE 
            WHEN Net_Revenue > 0 THEN (Net_Revenue - Total_Cost) / Net_Revenue 
            ELSE 0.0000 
        END, 4) AS Profit_Margin_Pct,

        -- Shipping Delivery SLA (Days elapsed between Order and Delivery)
        CAST(
            JULIANDAY(Clean_Ship_Date) - JULIANDAY(Clean_Order_Date) 
            AS INTEGER
        ) AS Delivery_Days
    FROM Calculated_Financials
)
SELECT * FROM Final_Enriched_Sales LIMIT 10;

-- ----------------------------------------------------------------------------
-- STEP 3: AUTOMATED DATA QUALITY AUDIT (SANITY CHECKS)
-- ----------------------------------------------------------------------------
-- 1. Check for negative revenues or prices
SELECT 'Assert No Negative Revenue' AS Test_Name,
       COUNT(*) AS Failure_Count
FROM fact_sales
WHERE Net_Revenue < 0 OR Unit_Price < 0;

-- 2. Check for orphan records (Foreign Key integrity)
SELECT 'Assert Zero Orphan Customers' AS Test_Name,
       COUNT(*) AS Failure_Count
FROM fact_sales s
LEFT JOIN dim_customers c ON s.Customer_ID = c.Customer_ID
WHERE c.Customer_ID IS NULL;

-- 3. Check for valid margin percentages (-100% to 100%)
SELECT 'Assert Reasonable Margin %' AS Test_Name,
       COUNT(*) AS Failure_Count
FROM fact_sales
WHERE Profit_Margin_Pct < -1.0 OR Profit_Margin_Pct > 1.0;

-- 4. Verify Shipping SLA logic
SELECT 'Assert Valid Shipping Duration' AS Test_Name,
       COUNT(*) AS Failure_Count
FROM fact_sales
WHERE Delivery_Days < 0;
