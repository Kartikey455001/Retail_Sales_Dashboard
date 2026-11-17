/* ============================================================================
   POWER QUERY (M) ETL SCRIPT: E-COMMERCE RETAIL SALES CLEANING & MODELING
   File: power_query_etl_scripts.m
   Tools: MS Excel Power Query / Power BI Desktop Power Query Editor
   Description: Complete M-code pipeline to ingest raw retail sales data,
                clean strings, parse multiple date formats, handle nulls,
                calculate financial metrics, and split into Star Schema dimensions.
   ============================================================================ */

// ----------------------------------------------------------------------------
// QUERY 1: Staging_Raw_Sales
// Ingests raw CSV, standardizes column names, trims strings, and parses dates
// ----------------------------------------------------------------------------
let
    // 1. Ingest raw CSV file
    Source = Csv.Document(
        File.Contents("C:\Users\karti\OneDrive\Desktop\Retail Sales Performance Dashboard\data\raw\retail_sales_raw.csv"),
        [Delimiter=",", Columns=26, Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    
    // 2. Promote first row as headers
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    
    // 3. Trim all text columns to eliminate leading/trailing whitespace
    TrimmedText = Table.TransformColumns(PromotedHeaders, {
        {"Txn_ID", Text.Trim, type text},
        {"Order_ID", Text.Trim, type text},
        {"Cust_ID", Text.Trim, type text},
        {"Cust_Name", Text.Trim, type text},
        {"Cust_Segment", Text.Trim, type text},
        {"Country", Text.Trim, type text},
        {"State", Text.Trim, type text},
        {"City", Text.Trim, type text},
        {"Postal_Code", Text.Trim, type text},
        {"Region", Text.Trim, type text},
        {"Prod_ID", Text.Trim, type text},
        {"Prod_Name", Text.Trim, type text},
        {"Category", Text.Trim, type text},
        {"Sub_Category", Text.Trim, type text},
        {"Channel", Text.Trim, type text},
        {"Ship_Mode", Text.Trim, type text},
        {"Payment_Type", Text.Trim, type text},
        {"Order_Status", Text.Trim, type text},
        {"Return_Reason", Text.Trim, type text}
    }),
    
    // 4. Clean Customer Segment (Proper Case)
    CleanedSegment = Table.TransformColumns(TrimmedText, {
        {"Cust_Segment", Text.Proper, type text}
    }),
    
    // 5. Parse mixed-format Order_Date (YYYY-MM-DD, MM/DD/YYYY, DD-MM-YYYY)
    ParsedOrderDate = Table.AddColumn(CleanedSegment, "Clean_Order_Date", each 
        let
            rawDate = [Order_Date]
        in
            try Date.FromText(rawDate, "en-US") 
            otherwise try Date.FromText(rawDate, "en-GB")
            otherwise Date.FromText(rawDate),
        type date
    ),
    
    // 6. Parse mixed-format Ship_Date (Handling nulls and blanks)
    ParsedShipDate = Table.AddColumn(ParsedOrderDate, "Clean_Ship_Date", each 
        let
            rawDate = [Ship_Date]
        in
            if rawDate = null or rawDate = "" then null 
            else try Date.FromText(rawDate, "en-US") 
                 otherwise try Date.FromText(rawDate, "en-GB")
                 otherwise Date.FromText(rawDate),
        type date
    ),
    
    // 7. Clean and parse Discount column (Handles "15%", "0.15", and blanks)
    ParsedDiscount = Table.AddColumn(ParsedShipDate, "Discount_Rate", each 
        let
            d = [Discount]
        in
            if d = null or d = "" then 0.0
            else if Text.EndsWith(d, "%") then 
                Number.FromText(Text.TrimEnd(d, "%")) / 100.0
            else 
                Number.FromText(d),
        type number
    ),
    
    // 8. Assign Standard Data Types
    TypedTable = Table.TransformColumnTypes(ParsedDiscount, {
        {"Quantity", Int64.Type},
        {"Unit_Cost", Currency.Type},
        {"Unit_Price", Currency.Type},
        {"Shipping_Fee", Currency.Type}
    }),
    
    // 9. Feature Engineering: Financial Calculations
    AddedGrossRevenue = Table.AddColumn(TypedTable, "Gross_Revenue", each 
        [Quantity] * [Unit_Price], Currency.Type
    ),
    AddedDiscountAmount = Table.AddColumn(AddedGrossRevenue, "Discount_Amount", each 
        [Gross_Revenue] * [Discount_Rate], Currency.Type
    ),
    AddedNetRevenue = Table.AddColumn(AddedDiscountAmount, "Net_Revenue", each 
        [Gross_Revenue] - [Discount_Amount], Currency.Type
    ),
    AddedTotalCost = Table.AddColumn(AddedNetRevenue, "Total_Cost", each 
        ([Quantity] * [Unit_Cost]) + [Shipping_Fee], Currency.Type
    ),
    AddedProfit = Table.AddColumn(AddedTotalCost, "Profit", each 
        [Net_Revenue] - [Total_Cost], Currency.Type
    ),
    AddedProfitMargin = Table.AddColumn(AddedProfit, "Profit_Margin_Pct", each 
        if [Net_Revenue] > 0 then [Profit] / [Net_Revenue] else 0.0, Percentage.Type
    ),
    
    // 10. Operational Metrics: Delivery Delay in Days
    AddedDeliveryDays = Table.AddColumn(AddedProfitMargin, "Delivery_Days", each 
        if [Clean_Ship_Date] <> null then 
            Duration.Days([Clean_Ship_Date] - [Clean_Order_Date]) 
        else null, Int64.Type
    ),
    
    // 11. Region Key Mapping
    AddedRegionID = Table.AddColumn(AddedDeliveryDays, "Region_ID", each 
        if [Region] = "West" then "REG-W"
        else if [Region] = "East" then "REG-E"
        else if [Region] = "Central" then "REG-C"
        else if [Region] = "South" then "REG-S"
        else "REG-UNK",
        type text
    )
in
    AddedRegionID;


// ----------------------------------------------------------------------------
// QUERY 2: Fact_Sales (Star Schema Fact Table)
// Selects transactional columns, removes redundant textual dimensions
// ----------------------------------------------------------------------------
let
    Source = Staging_Raw_Sales,
    SelectedColumns = Table.SelectColumns(Source, {
        "Txn_ID", "Order_ID", "Clean_Order_Date", "Clean_Ship_Date",
        "Cust_ID", "Prod_ID", "Region_ID",
        "Channel", "Ship_Mode", "Payment_Type", "Order_Status",
        "Quantity", "Unit_Cost", "Unit_Price",
        "Gross_Revenue", "Discount_Rate", "Discount_Amount", "Net_Revenue",
        "Shipping_Fee", "Total_Cost", "Profit", "Profit_Margin_Pct", "Delivery_Days"
    }),
    RenamedColumns = Table.RenameColumns(SelectedColumns, {
        {"Txn_ID", "Transaction_ID"},
        {"Clean_Order_Date", "Order_Date"},
        {"Clean_Ship_Date", "Ship_Date"},
        {"Cust_ID", "Customer_ID"},
        {"Prod_ID", "Product_ID"},
        {"Channel", "Sales_Channel"},
        {"Payment_Type", "Payment_Method"},
        {"Shipping_Fee", "Shipping_Cost"}
    })
in
    RenamedColumns;


// ----------------------------------------------------------------------------
// QUERY 3: Dim_Product (Product Dimension)
// Deduplicates products, retains hierarchy and standard pricing
// ----------------------------------------------------------------------------
let
    Source = Staging_Raw_Sales,
    SelectedColumns = Table.SelectColumns(Source, {
        "Prod_ID", "Prod_Name", "Category", "Sub_Category", "Unit_Cost", "Unit_Price"
    }),
    Deduplicated = Table.Distinct(SelectedColumns, {"Prod_ID"}),
    RenamedColumns = Table.RenameColumns(Deduplicated, {
        {"Prod_ID", "Product_ID"},
        {"Prod_Name", "Product_Name"},
        {"Unit_Cost", "Standard_Cost"},
        {"Unit_Price", "Standard_Price"}
    })
in
    RenamedColumns;


// ----------------------------------------------------------------------------
// QUERY 4: Dim_Customer (Customer Dimension)
// Deduplicates customers and keeps geographical profile
// ----------------------------------------------------------------------------
let
    Source = Staging_Raw_Sales,
    SelectedColumns = Table.SelectColumns(Source, {
        "Cust_ID", "Cust_Name", "Cust_Segment", "Region", "State", "City", "Postal_Code"
    }),
    Deduplicated = Table.Distinct(SelectedColumns, {"Cust_ID"}),
    RenamedColumns = Table.RenameColumns(Deduplicated, {
        {"Cust_ID", "Customer_ID"},
        {"Cust_Name", "Customer_Name"},
        {"Cust_Segment", "Segment"},
        {"Region", "Primary_Region"}
    })
in
    RenamedColumns;


// ----------------------------------------------------------------------------
// QUERY 5: Dim_Date (Dynamic Calendar Table Generator in M)
// Automatically generates date range based on min/max sales order dates
// ----------------------------------------------------------------------------
let
    StartDate = #date(2023, 1, 1),
    EndDate = #date(2025, 12, 31),
    NumberOfDays = Duration.Days(EndDate - StartDate) + 1,
    DateList = List.Dates(StartDate, NumberOfDays, #duration(1, 0, 0, 0)),
    TableFromList = Table.FromList(DateList, Splitter.SplitByNothing(), {"Full_Date"}, null, ExtraValues.Error),
    TypedDate = Table.TransformColumnTypes(TableFromList, {{"Full_Date", type date}}),
    
    // Add Calendar Attributes
    AddedDateKey = Table.AddColumn(TypedDate, "Date_Key", each 
        Date.Year([Full_Date]) * 10000 + Date.Month([Full_Date]) * 100 + Date.Day([Full_Date]), Int64.Type
    ),
    AddedYear = Table.AddColumn(AddedDateKey, "Year", each Date.Year([Full_Date]), Int64.Type),
    AddedQuarter = Table.AddColumn(AddedYear, "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Full_Date])), type text),
    AddedYearQuarter = Table.AddColumn(AddedQuarter, "Year_Quarter", each Text.From([Year]) & "-" & [Quarter], type text),
    AddedMonth = Table.AddColumn(AddedYearQuarter, "Month", each Date.Month([Full_Date]), Int64.Type),
    AddedMonthName = Table.AddColumn(AddedMonth, "Month_Name", each Date.MonthName([Full_Date]), type text),
    AddedMonthShort = Table.AddColumn(AddedMonthName, "Month_Short", each Text.Start([Month_Name], 3), type text),
    AddedYearMonth = Table.AddColumn(AddedMonthShort, "Year_Month", each Text.From([Year]) & "-" & Text.PadStart(Text.From([Month]), 2, "0"), type text),
    AddedDay = Table.AddColumn(AddedYearMonth, "Day_Of_Month", each Date.Day([Full_Date]), Int64.Type),
    AddedDayOfWeek = Table.AddColumn(AddedDay, "Day_Of_Week", each Date.DayOfWeek([Full_Date], Day.Monday) + 1, Int64.Type),
    AddedDayName = Table.AddColumn(AddedDayOfWeek, "Day_Name", each Date.DayOfWeekName([Full_Date]), type text),
    AddedIsWeekend = Table.AddColumn(AddedDayName, "Is_Weekend", each if [Day_Of_Week] >= 6 then 1 else 0, Int64.Type)
in
    AddedIsWeekend;
