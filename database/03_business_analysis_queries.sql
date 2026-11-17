-- ============================================================================
-- 03_business_analysis_queries.sql
-- Retail Sales Performance - Advanced Business Intelligence & Analytics Queries
-- Demonstrates: CTEs, Window Functions (LAG, LEAD, DENSE_RANK, NTILE),
-- Aggregations, Rolling Metrics, Cohort Retention, and RFM Segmentation.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: EXECUTIVE KPI SUMMARY ACROSS ALL TIME
-- Business Question: What are the primary company-wide financial and operational KPIs?
-- ----------------------------------------------------------------------------
SELECT 
    COUNT(DISTINCT Order_ID)                            AS Total_Orders,
    COUNT(DISTINCT Customer_ID)                         AS Total_Unique_Customers,
    SUM(Quantity)                                       AS Total_Units_Sold,
    ROUND(SUM(Gross_Revenue), 2)                        AS Gross_Revenue,
    ROUND(SUM(Discount_Amount), 2)                      AS Total_Discounts_Given,
    ROUND(SUM(Net_Revenue), 2)                          AS Total_Net_Revenue,
    ROUND(SUM(Total_Cost), 2)                           AS Total_COGS_And_Shipping,
    ROUND(SUM(Profit), 2)                               AS Total_Net_Profit,
    ROUND((SUM(Profit) / SUM(Net_Revenue)) * 100, 2)    AS Overall_Profit_Margin_Pct,
    ROUND(SUM(Net_Revenue) / COUNT(DISTINCT Order_ID), 2) AS Average_Order_Value_AOV,
    ROUND((SUM(Is_Returned) * 1.0 / COUNT(*)) * 100, 2) AS Overall_Return_Rate_Pct
FROM fact_sales;


-- ----------------------------------------------------------------------------
-- QUERY 2: YEAR-OVER-YEAR (YoY) REVENUE, PROFIT & ORDER GROWTH
-- Business Question: How has top-line revenue and bottom-line profit grown YoY?
-- ----------------------------------------------------------------------------
WITH Annual_Sales AS (
    SELECT 
        d.Year,
        ROUND(SUM(s.Net_Revenue), 2)  AS Net_Revenue,
        ROUND(SUM(s.Profit), 2)       AS Net_Profit,
        COUNT(DISTINCT s.Order_ID)    AS Total_Orders,
        SUM(s.Quantity)               AS Units_Sold
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
    ) AS YoY_Revenue_Growth_Pct,
    
    Net_Profit,
    LAG(Net_Profit, 1) OVER (ORDER BY Year) AS Prior_Year_Profit,
    ROUND(
        ((Net_Profit - LAG(Net_Profit, 1) OVER (ORDER BY Year)) / 
        LAG(Net_Profit, 1) OVER (ORDER BY Year)) * 100, 2
    ) AS YoY_Profit_Growth_Pct,

    Total_Orders,
    ROUND(
        ((Total_Orders - LAG(Total_Orders, 1) OVER (ORDER BY Year)) * 1.0 / 
        LAG(Total_Orders, 1) OVER (ORDER BY Year)) * 100, 2
    ) AS YoY_Order_Growth_Pct
FROM Annual_Sales
ORDER BY Year ASC;


-- ----------------------------------------------------------------------------
-- QUERY 3: MONTH-OVER-MONTH (MoM) GROWTH & 3-MONTH ROLLING REVENUE
-- Business Question: What is the monthly trajectory and smoothed 3-month moving average?
-- ----------------------------------------------------------------------------
WITH Monthly_Sales AS (
    SELECT 
        d.Year,
        d.Month,
        d.Year_Month,
        ROUND(SUM(s.Net_Revenue), 2) AS Monthly_Revenue,
        ROUND(SUM(s.Profit), 2)      AS Monthly_Profit
    FROM fact_sales s
    JOIN dim_date d ON s.Order_Date = d.Full_Date
    GROUP BY d.Year, d.Month, d.Year_Month
)
SELECT 
    Year_Month,
    Monthly_Revenue,
    LAG(Monthly_Revenue, 1) OVER (ORDER BY Year_Month) AS Prior_Month_Revenue,
    ROUND(
        ((Monthly_Revenue - LAG(Monthly_Revenue, 1) OVER (ORDER BY Year_Month)) /
        LAG(Monthly_Revenue, 1) OVER (ORDER BY Year_Month)) * 100, 2
    ) AS MoM_Revenue_Growth_Pct,
    ROUND(
        AVG(Monthly_Revenue) OVER (
            ORDER BY Year_Month 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 2
    ) AS Rolling_3Month_Avg_Revenue,
    Monthly_Profit,
    ROUND((Monthly_Profit / Monthly_Revenue) * 100, 2) AS Monthly_Margin_Pct
FROM Monthly_Sales
ORDER BY Year_Month ASC;


-- ----------------------------------------------------------------------------
-- QUERY 4: TOP 10 PRODUCTS BY REVENUE AND PROFIT MARGIN
-- Business Question: Which specific SKUs drive the bulk of enterprise cash flow?
-- ----------------------------------------------------------------------------
WITH Product_Financials AS (
    SELECT 
        p.Product_ID,
        p.Product_Name,
        p.Category,
        p.Sub_Category,
        COUNT(DISTINCT s.Order_ID)        AS Total_Orders,
        SUM(s.Quantity)                   AS Total_Units_Sold,
        ROUND(SUM(s.Net_Revenue), 2)      AS Total_Revenue,
        ROUND(SUM(s.Profit), 2)           AS Total_Profit,
        ROUND((SUM(s.Profit) / SUM(s.Net_Revenue)) * 100, 2) AS Profit_Margin_Pct
    FROM fact_sales s
    JOIN dim_products p ON s.Product_ID = p.Product_ID
    GROUP BY p.Product_ID, p.Product_Name, p.Category, p.Sub_Category
)
SELECT 
    DENSE_RANK() OVER (ORDER BY Total_Revenue DESC) AS Revenue_Rank,
    Product_Name,
    Category,
    Sub_Category,
    Total_Orders,
    Total_Units_Sold,
    Total_Revenue,
    Total_Profit,
    Profit_Margin_Pct
FROM Product_Financials
ORDER BY Total_Revenue DESC
LIMIT 10;


-- ----------------------------------------------------------------------------
-- QUERY 5: CATEGORY & SUB-CATEGORY PROFITABILITY MATRIX
-- Business Question: Which categories generate the healthiest margins vs volume?
-- ----------------------------------------------------------------------------
SELECT 
    p.Category,
    p.Sub_Category,
    COUNT(DISTINCT s.Order_ID)                             AS Total_Orders,
    SUM(s.Quantity)                                        AS Total_Units_Sold,
    ROUND(SUM(s.Net_Revenue), 2)                           AS Net_Revenue,
    ROUND(SUM(s.Profit), 2)                                AS Net_Profit,
    ROUND((SUM(s.Profit) / SUM(s.Net_Revenue)) * 100, 2)   AS Profit_Margin_Pct,
    ROUND(
        (SUM(s.Net_Revenue) * 100.0) / 
        (SELECT SUM(Net_Revenue) FROM fact_sales), 2
    ) AS Share_Of_Total_Revenue_Pct
FROM fact_sales s
JOIN dim_products p ON s.Product_ID = p.Product_ID
GROUP BY p.Category, p.Sub_Category
ORDER BY p.Category ASC, Net_Revenue DESC;


-- ----------------------------------------------------------------------------
-- QUERY 6: REGIONAL REVENUE, PROFIT & REGIONAL MANAGER PERFORMANCE
-- Business Question: How do regions stack up in revenue contribution and margin?
-- ----------------------------------------------------------------------------
SELECT 
    r.Region_ID,
    r.Region,
    r.Market_Tier,
    r.Regional_Manager,
    COUNT(DISTINCT s.Customer_ID)                          AS Active_Customers,
    COUNT(DISTINCT s.Order_ID)                             AS Total_Orders,
    ROUND(SUM(s.Net_Revenue), 2)                           AS Total_Revenue,
    ROUND(SUM(s.Profit), 2)                                AS Total_Profit,
    ROUND((SUM(s.Profit) / SUM(s.Net_Revenue)) * 100, 2)   AS Profit_Margin_Pct,
    ROUND(SUM(s.Net_Revenue) / COUNT(DISTINCT s.Order_ID), 2) AS Regional_AOV
FROM fact_sales s
JOIN dim_regions r ON s.Region_ID = r.Region_ID
GROUP BY r.Region_ID, r.Region, r.Market_Tier, r.Regional_Manager
ORDER BY Total_Revenue DESC;


-- ----------------------------------------------------------------------------
-- QUERY 7: CUSTOMER SEGMENTATION FINANCIAL PERFORMANCE
-- Business Question: What is the revenue, AOV, and profitability by customer segment?
-- ----------------------------------------------------------------------------
SELECT 
    c.Segment,
    COUNT(DISTINCT c.Customer_ID)                           AS Customer_Count,
    COUNT(DISTINCT s.Order_ID)                              AS Total_Orders,
    ROUND(COUNT(DISTINCT s.Order_ID) * 1.0 / COUNT(DISTINCT c.Customer_ID), 1) AS Orders_Per_Customer,
    SUM(s.Quantity)                                         AS Total_Units_Purchased,
    ROUND(SUM(s.Net_Revenue), 2)                            AS Total_Revenue,
    ROUND(SUM(s.Profit), 2)                                 AS Total_Profit,
    ROUND((SUM(s.Profit) / SUM(s.Net_Revenue)) * 100, 2)    AS Margin_Pct,
    ROUND(SUM(s.Net_Revenue) / COUNT(DISTINCT s.Order_ID), 2) AS Segment_AOV
FROM fact_sales s
JOIN dim_customers c ON s.Customer_ID = c.Customer_ID
GROUP BY c.Segment
ORDER BY Total_Revenue DESC;


-- ----------------------------------------------------------------------------
-- QUERY 8: CUSTOMER RFM (RECENCY, FREQUENCY, MONETARY) SEGMENTATION
-- Business Question: How can we segment customers into Champions, Loyal, At-Risk?
-- ----------------------------------------------------------------------------
WITH Customer_Aggregates AS (
    SELECT 
        Customer_ID,
        -- Recency: Days since last transaction (relative to latest dataset date: 2025-12-31)
        CAST(JULIANDAY('2025-12-31') - JULIANDAY(MAX(Order_Date)) AS INTEGER) AS Recency_Days,
        -- Frequency: Count of distinct orders
        COUNT(DISTINCT Order_ID) AS Frequency,
        -- Monetary: Total spend
        ROUND(SUM(Net_Revenue), 2) AS Monetary
    FROM fact_sales
    GROUP BY Customer_ID
),
RFM_Scores AS (
    SELECT 
        Customer_ID,
        Recency_Days,
        Frequency,
        Monetary,
        NTILE(4) OVER (ORDER BY Recency_Days DESC) AS R_Score,  -- 4 = Most recent
        NTILE(4) OVER (ORDER BY Frequency ASC)     AS F_Score,  -- 4 = Most frequent
        NTILE(4) OVER (ORDER BY Monetary ASC)      AS M_Score   -- 4 = Highest spend
    FROM Customer_Aggregates
)
SELECT 
    Customer_ID,
    Recency_Days,
    Frequency,
    Monetary,
    R_Score,
    F_Score,
    M_Score,
    CASE 
        WHEN R_Score >= 3 AND F_Score >= 3 AND M_Score >= 3 THEN 'Champions / High Value'
        WHEN R_Score >= 3 AND F_Score >= 2 THEN 'Loyal Active Customers'
        WHEN R_Score <= 2 AND F_Score >= 3 THEN 'At Risk / Churning Champions'
        WHEN R_Score <= 2 AND F_Score <= 2 AND M_Score <= 2 THEN 'Hibernating / Dormant'
        ELSE 'Promising / Potential Growth'
    END AS RFM_Customer_Segment
FROM RFM_Scores
ORDER BY Monetary DESC
LIMIT 20;


-- ----------------------------------------------------------------------------
-- QUERY 9: REPEAT PURCHASING TIER & CUSTOMER LIFETIME SPEND
-- Business Question: What proportion of revenue is driven by core vs VIP buyers?
-- ----------------------------------------------------------------------------
WITH Customer_Order_Counts AS (
    SELECT 
        Customer_ID,
        COUNT(DISTINCT Order_ID) AS Total_Customer_Orders,
        ROUND(SUM(Net_Revenue), 2) AS Total_Customer_Spend
    FROM fact_sales
    GROUP BY Customer_ID
)
SELECT 
    CASE 
        WHEN Total_Customer_Orders <= 15 THEN 'Occasional Buyers (<= 15 Orders)'
        WHEN Total_Customer_Orders BETWEEN 16 AND 22 THEN 'Core Regulars (16-22 Orders)'
        ELSE 'Super VIP Loyalists (23+ Orders)'
    END AS Buyer_Tier,
    COUNT(Customer_ID)                           AS Customer_Count,
    ROUND(SUM(Total_Customer_Spend), 2)          AS Total_Revenue_Generated,
    ROUND(
        (SUM(Total_Customer_Spend) * 100.0) / 
        (SELECT SUM(Net_Revenue) FROM fact_sales), 2
    ) AS Share_Of_Total_Revenue_Pct,
    ROUND(AVG(Total_Customer_Spend), 2)          AS Avg_Revenue_Per_Customer
FROM Customer_Order_Counts
GROUP BY Buyer_Tier
ORDER BY Total_Revenue_Generated DESC;


-- ----------------------------------------------------------------------------
-- QUERY 10: SHIPPING PERFORMANCE & ON-TIME DELIVERY SLA BY SHIPPING MODE
-- Business Question: Does shipping mode impact delivery time and profitability?
-- ----------------------------------------------------------------------------
SELECT 
    Ship_Mode,
    COUNT(DISTINCT Order_ID)                              AS Order_Count,
    ROUND(AVG(Delivery_Days), 1)                          AS Avg_Delivery_Days,
    MIN(Delivery_Days)                                    AS Fastest_Delivery_Days,
    MAX(Delivery_Days)                                    AS Longest_Delivery_Days,
    ROUND(SUM(Shipping_Cost), 2)                          AS Total_Shipping_Costs,
    ROUND(AVG(Shipping_Cost), 2)                          AS Avg_Shipping_Cost_Per_Item,
    ROUND(SUM(Net_Revenue), 2)                            AS Total_Revenue,
    ROUND(SUM(Profit), 2)                                 AS Total_Profit,
    ROUND((SUM(Profit) / SUM(Net_Revenue)) * 100, 2)      AS Margin_Pct
FROM fact_sales
GROUP BY Ship_Mode
ORDER BY Order_Count DESC;


-- ----------------------------------------------------------------------------
-- QUERY 11: PRODUCT RETURN RATE & LOST REVENUE BY CATEGORY
-- Business Question: Where are returns concentrated, and what is the return impact?
-- ----------------------------------------------------------------------------
SELECT 
    p.Category,
    COUNT(*)                                              AS Total_Items_Sold,
    SUM(s.Is_Returned)                                    AS Total_Items_Returned,
    ROUND((SUM(s.Is_Returned) * 100.0 / COUNT(*)), 2)     AS Return_Rate_Pct,
    ROUND(SUM(CASE WHEN s.Is_Returned = 1 THEN s.Net_Revenue ELSE 0 END), 2) AS Gross_Returned_Value,
    ROUND(SUM(COALESCE(r.Refund_Amount, 0)), 2)           AS Total_Refunded_Amount,
    ROUND(SUM(COALESCE(r.Restocking_Fee, 0)), 2)          AS Restocking_Fees_Recouped
FROM fact_sales s
JOIN dim_products p ON s.Product_ID = p.Product_ID
LEFT JOIN dim_returns r ON s.Transaction_ID = r.Transaction_ID
GROUP BY p.Category
ORDER BY Return_Rate_Pct DESC;


-- ----------------------------------------------------------------------------
-- QUERY 12: DISCOUNT IMPACT ON MARGINS (PRICE ELASTICITY CHECK)
-- Business Question: Are steep discounts eroding profitability without gaining volume?
-- ----------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN Discount_Rate = 0.00 THEN '0% Full Price'
        WHEN Discount_Rate <= 0.05 THEN '1% - 5% Low Discount'
        WHEN Discount_Rate <= 0.15 THEN '6% - 15% Medium Discount'
        ELSE '16%+ Heavy Promo Discount'
    END AS Discount_Band,
    COUNT(*)                                              AS Transaction_Volume,
    SUM(Quantity)                                         AS Total_Units_Sold,
    ROUND(SUM(Net_Revenue), 2)                            AS Total_Net_Revenue,
    ROUND(SUM(Discount_Amount), 2)                        AS Total_Discount_Given,
    ROUND(SUM(Profit), 2)                                 AS Total_Profit,
    ROUND((SUM(Profit) / SUM(Net_Revenue)) * 100, 2)      AS Realized_Margin_Pct
FROM fact_sales
GROUP BY Discount_Band
ORDER BY Total_Net_Revenue DESC;


-- ----------------------------------------------------------------------------
-- QUERY 13: SALES CHANNEL PERFORMANCE & PROFITABILITY
-- Business Question: Which acquisition channels (Online, App, Amazon) yield highest profits?
-- ----------------------------------------------------------------------------
SELECT 
    Sales_Channel,
    COUNT(DISTINCT Order_ID)                              AS Orders,
    SUM(Quantity)                                         AS Units,
    ROUND(SUM(Net_Revenue), 2)                            AS Net_Revenue,
    ROUND(SUM(Profit), 2)                                 AS Net_Profit,
    ROUND((SUM(Profit) / SUM(Net_Revenue)) * 100, 2)      AS Margin_Pct,
    ROUND(SUM(Net_Revenue) / COUNT(DISTINCT Order_ID), 2) AS Channel_AOV,
    ROUND(
        (SUM(Net_Revenue) * 100.0) / 
        (SELECT SUM(Net_Revenue) FROM fact_sales), 2
    ) AS Channel_Revenue_Share_Pct
FROM fact_sales
GROUP BY Sales_Channel
ORDER BY Net_Revenue DESC;


-- ----------------------------------------------------------------------------
-- QUERY 14: PARETO 80/20 ANALYSIS (CUMULATIVE REVENUE SHARE)
-- Business Question: Do top 20% of products generate 80% of revenue?
-- ----------------------------------------------------------------------------
WITH Product_Revenue AS (
    SELECT 
        p.Product_Name,
        p.Category,
        ROUND(SUM(s.Net_Revenue), 2) AS Product_Revenue
    FROM fact_sales s
    JOIN dim_products p ON s.Product_ID = p.Product_ID
    GROUP BY p.Product_Name, p.Category
),
Cumulative_Revenue AS (
    SELECT 
        Product_Name,
        Category,
        Product_Revenue,
        SUM(Product_Revenue) OVER (ORDER BY Product_Revenue DESC) AS Running_Total_Revenue,
        SUM(Product_Revenue) OVER () AS Overall_Company_Revenue
    FROM Product_Revenue
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY Product_Revenue DESC) AS SKU_Rank,
    Product_Name,
    Category,
    Product_Revenue,
    ROUND(Running_Total_Revenue, 2) AS Running_Total_Revenue,
    ROUND((Running_Total_Revenue / Overall_Company_Revenue) * 100, 2) AS Cumulative_Revenue_Pct
FROM Cumulative_Revenue
ORDER BY Product_Revenue DESC;


-- ----------------------------------------------------------------------------
-- QUERY 15: QUARTERLY COHORT ACQUISITION & RETENTION
-- Business Question: How do customer cohorts spend across consecutive quarters?
-- ----------------------------------------------------------------------------
WITH Customer_First_Quarter AS (
    SELECT 
        Customer_ID,
        MIN(SUBSTR(Order_Date, 1, 7)) AS First_Order_Month,
        d.Year_Quarter AS Acquisition_Cohort
    FROM fact_sales s
    JOIN dim_date d ON s.Order_Date = d.Full_Date
    GROUP BY Customer_ID
),
Cohort_Performance AS (
    SELECT 
        cfq.Acquisition_Cohort,
        COUNT(DISTINCT s.Customer_ID) AS Cohort_Size,
        COUNT(DISTINCT s.Order_ID)    AS Lifetime_Orders,
        ROUND(SUM(s.Net_Revenue), 2)  AS Cohort_Lifetime_Revenue,
        ROUND(SUM(s.Profit), 2)       AS Cohort_Lifetime_Profit,
        ROUND(SUM(s.Net_Revenue) / COUNT(DISTINCT s.Customer_ID), 2) AS Revenue_Per_Acquired_Customer
    FROM Customer_First_Quarter cfq
    JOIN fact_sales s ON cfq.Customer_ID = s.Customer_ID
    GROUP BY cfq.Acquisition_Cohort
)
SELECT * 
FROM Cohort_Performance
ORDER BY Acquisition_Cohort ASC;
