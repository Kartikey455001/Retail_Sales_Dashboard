-- ============================================================================
-- 01_schema_ddl.sql
-- Retail Sales Performance Data Warehouse - Star Schema DDL
-- Database: Compatible with SQLite, PostgreSQL, MySQL, and Microsoft SQL Server
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. STAGING TABLE (Raw Ingestion Layer)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_retail_sales;

CREATE TABLE stg_retail_sales (
    Txn_ID          VARCHAR(50),
    Order_ID        VARCHAR(50),
    Order_Date      VARCHAR(50),
    Ship_Date       VARCHAR(50),
    Cust_ID         VARCHAR(50),
    Cust_Name       VARCHAR(150),
    Cust_Segment    VARCHAR(50),
    Country         VARCHAR(50),
    State           VARCHAR(100),
    City            VARCHAR(100),
    Postal_Code     VARCHAR(20),
    Region          VARCHAR(50),
    Prod_ID         VARCHAR(50),
    Prod_Name       VARCHAR(200),
    Category        VARCHAR(100),
    Sub_Category    VARCHAR(100),
    Unit_Cost       NUMERIC(10, 2),
    Unit_Price      NUMERIC(10, 2),
    Quantity        INTEGER,
    Discount        VARCHAR(20),
    Shipping_Fee    NUMERIC(10, 2),
    Channel         VARCHAR(50),
    Ship_Mode       VARCHAR(50),
    Payment_Type    VARCHAR(50),
    Order_Status    VARCHAR(50),
    Return_Reason   VARCHAR(100)
);

-- ----------------------------------------------------------------------------
-- 2. DIMENSION TABLES (Star Schema)
-- ----------------------------------------------------------------------------

-- Dim_Date: Conformed Date Dimension for Time Intelligence
DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_date (
    Date_Key        INTEGER PRIMARY KEY,      -- Format: YYYYMMDD
    Full_Date       DATE NOT NULL UNIQUE,     -- Format: YYYY-MM-DD
    Year            INTEGER NOT NULL,
    Quarter         VARCHAR(2) NOT NULL,      -- Q1, Q2, Q3, Q4
    Year_Quarter    VARCHAR(10) NOT NULL,     -- 2024-Q1
    Month           INTEGER NOT NULL,         -- 1 - 12
    Month_Name      VARCHAR(20) NOT NULL,     -- January, February...
    Month_Short     VARCHAR(3) NOT NULL,      -- Jan, Feb...
    Year_Month      VARCHAR(7) NOT NULL,      -- 2024-01
    Day_Of_Month    INTEGER NOT NULL,
    Day_Of_Week     INTEGER NOT NULL,         -- 1 (Mon) - 7 (Sun)
    Day_Name        VARCHAR(15) NOT NULL,     -- Monday, Tuesday...
    Day_Short       VARCHAR(3) NOT NULL,      -- Mon, Tue...
    Is_Weekend      INTEGER NOT NULL,         -- 1 = Weekend, 0 = Weekday
    Fiscal_Year     INTEGER NOT NULL,
    Fiscal_Quarter  VARCHAR(5) NOT NULL
);

-- Dim_Customers: Customer Profiles & Geographic Hierarchy
DROP TABLE IF EXISTS dim_customers;

CREATE TABLE dim_customers (
    Customer_ID     VARCHAR(50) PRIMARY KEY,
    Customer_Name   VARCHAR(150) NOT NULL,
    Customer_Email  VARCHAR(150),
    Segment         VARCHAR(50) NOT NULL,     -- Consumer, Corporate, Home Office, Small Business
    Primary_Region  VARCHAR(50),
    State           VARCHAR(100),
    City            VARCHAR(100),
    Postal_Code     VARCHAR(20),
    Account_Created DATE
);

-- Dim_Products: Product Catalog Hierarchy
DROP TABLE IF EXISTS dim_products;

CREATE TABLE dim_products (
    Product_ID      VARCHAR(50) PRIMARY KEY,
    Product_Name    VARCHAR(200) NOT NULL,
    Category        VARCHAR(100) NOT NULL,    -- Technology, Furniture, Office Supplies, etc.
    Sub_Category    VARCHAR(100) NOT NULL,
    Standard_Cost   NUMERIC(10, 2) NOT NULL,
    Standard_Price  NUMERIC(10, 2) NOT NULL
);

-- Dim_Regions: Regional Management & Territories
DROP TABLE IF EXISTS dim_regions;

CREATE TABLE dim_regions (
    Region_ID        VARCHAR(20) PRIMARY KEY,
    Region           VARCHAR(50) NOT NULL UNIQUE,
    Market_Tier      VARCHAR(20),
    Regional_Manager VARCHAR(100)
);

-- Dim_Returns: Product Return Audit & Restocking Logistics
DROP TABLE IF EXISTS dim_returns;

CREATE TABLE dim_returns (
    Return_ID        VARCHAR(50) PRIMARY KEY,
    Transaction_ID   VARCHAR(50) NOT NULL,
    Order_ID         VARCHAR(50) NOT NULL,
    Return_Date      DATE NOT NULL,
    Return_Reason    VARCHAR(100),
    Refund_Amount    NUMERIC(10, 2) NOT NULL,
    Restocking_Fee   NUMERIC(10, 2) DEFAULT 0.00
);

-- ----------------------------------------------------------------------------
-- 3. FACT TABLE (Sales Transactions)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS fact_sales;

CREATE TABLE fact_sales (
    Transaction_ID      VARCHAR(50) PRIMARY KEY,
    Order_ID            VARCHAR(50) NOT NULL,
    Order_Date          DATE NOT NULL,
    Ship_Date           DATE,
    Customer_ID         VARCHAR(50) NOT NULL,
    Product_ID          VARCHAR(50) NOT NULL,
    Region_ID           VARCHAR(20) NOT NULL,
    Sales_Channel       VARCHAR(50) NOT NULL,
    Ship_Mode           VARCHAR(50) NOT NULL,
    Payment_Method      VARCHAR(50) NOT NULL,
    Order_Status        VARCHAR(50) NOT NULL,
    Quantity            INTEGER NOT NULL CHECK(Quantity > 0),
    Unit_Cost           NUMERIC(10, 2) NOT NULL CHECK(Unit_Cost >= 0),
    Unit_Price          NUMERIC(10, 2) NOT NULL CHECK(Unit_Price >= 0),
    Gross_Revenue       NUMERIC(12, 2) NOT NULL,
    Discount_Rate       NUMERIC(5, 4) DEFAULT 0.0000,
    Discount_Amount     NUMERIC(10, 2) DEFAULT 0.00,
    Net_Revenue         NUMERIC(12, 2) NOT NULL,
    Shipping_Cost       NUMERIC(10, 2) DEFAULT 0.00,
    Total_Cost          NUMERIC(12, 2) NOT NULL,
    Profit              NUMERIC(12, 2) NOT NULL,
    Profit_Margin_Pct   NUMERIC(6, 4) NOT NULL,
    Is_Returned         INTEGER NOT NULL DEFAULT 0,
    Delivery_Days       INTEGER,
    
    -- Foreign Key Integrity
    FOREIGN KEY (Customer_ID) REFERENCES dim_customers(Customer_ID),
    FOREIGN KEY (Product_ID)  REFERENCES dim_products(Product_ID),
    FOREIGN KEY (Region_ID)   REFERENCES dim_regions(Region_ID)
);

-- ----------------------------------------------------------------------------
-- 4. PERFORMANCE OPTIMIZATION INDEXES
-- ----------------------------------------------------------------------------
CREATE INDEX idx_fact_sales_order_date ON fact_sales(Order_Date);
CREATE INDEX idx_fact_sales_customer   ON fact_sales(Customer_ID);
CREATE INDEX idx_fact_sales_product    ON fact_sales(Product_ID);
CREATE INDEX idx_fact_sales_region     ON fact_sales(Region_ID);
CREATE INDEX idx_fact_sales_status     ON fact_sales(Order_Status);
CREATE INDEX idx_fact_sales_channel    ON fact_sales(Sales_Channel);
