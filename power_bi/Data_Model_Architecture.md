# Power BI Data Model Architecture & Schema Design
**Project:** E-Commerce Retail Sales Performance Analytics  
**Architecture:** Enterprise Tabular Star Schema  
**Related Files:** [`DAX_Measures.dax`](file:///c:/Users/karti/OneDrive/Desktop/Retail%20Sales%20Performance%20Dashboard/power_bi/DAX_Measures.dax), [`Dashboard_Design_Guide.md`](file:///c:/Users/karti/OneDrive/Desktop/Retail%20Sales%20Performance%20Dashboard/power_bi/Dashboard_Design_Guide.md)

---

## 1. Star Schema Architecture Diagram

```
                     ┌────────────────────────┐
                     │        dim_date        │
                     │────────────────────────│
                     │ * Date_Key (PK)        │
                     │   Full_Date            │
                     │   Year, Quarter, Month │
                     │   Year_Month, Day_Name │
                     └───────────┬────────────┘
                                 │ 1
                                 │ (Active: Order_Date)
                                 │ (Inactive: Ship_Date)
                                 ▼ *
┌───────────────────────┐   ┌────────────────────────┐   ┌────────────────────────┐
│     dim_customers     │   │       fact_sales       │   │      dim_products      │
│───────────────────────│   │────────────────────────│   │────────────────────────│
│ * Customer_ID (PK)    │1  │ * Transaction_ID (PK)  │  1│ * Product_ID (PK)      │
│   Customer_Name       ├──►│   Order_ID             │◄──┤   Product_Name         │
│   Customer_Email      │*  │   Order_Date (FK)      │  *│   Category             │
│   Segment             │   │   Ship_Date (FK)       │   │   Sub_Category         │
│   Primary_Region      │   │   Customer_ID (FK)     │   │   Standard_Cost        │
│   State, City, Postal │   │   Product_ID (FK)      │   │   Standard_Price       │
└───────────────────────┘   │   Region_ID (FK)       │   └────────────────────────┘
                            │   Sales_Channel        │
                            │   Ship_Mode            │
                            │   Payment_Method       │
                            │   Order_Status         │
                            │   Quantity             │
                            │   Gross_Revenue        │
                            │   Discount_Rate/Amount │
                            │   Net_Revenue          │
                            │   Shipping_Cost        │
                            │   Total_Cost           │
                            │   Profit, Margin %     │
                            │   Delivery_Days        │
                            └───────────┬────────────┘
                                        │ *
                                        │ 
                                        ▼ 1
                             ┌───────────────────────┐
                             │      dim_regions      │
                             │───────────────────────│
                             │ * Region_ID (PK)      │
                             │   Region              │
                             │   Market_Tier         │
                             │   Regional_Manager    │
                             └───────────────────────┘
                                        │
                                        ▼ 
                             ┌───────────────────────┐
                             │      dim_returns      │
                             │───────────────────────│
                             │ * Return_ID (PK)      │
                             │   Transaction_ID (FK) │
                             │   Return_Date         │
                             │   Return_Reason       │
                             │   Refund_Amount       │
                             └───────────────────────┘
```

---

## 2. Model Relationship Specifications

| From Table (Dimension) | Primary Key (PK) | To Table (Fact) | Foreign Key (FK) | Cardinality | Filter Direction | Relationship State |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| `dim_date` | `Full_Date` | `fact_sales` | `Order_Date` | $1 : \text{Many}$ | Single (`dim_date` $\rightarrow$ `fact_sales`) | **Active** (Primary) |
| `dim_date` | `Full_Date` | `fact_sales` | `Ship_Date` | $1 : \text{Many}$ | Single (`dim_date` $\rightarrow$ `fact_sales`) | **Inactive** (Invoked via `USERELATIONSHIP`) |
| `dim_products` | `Product_ID` | `fact_sales` | `Product_ID` | $1 : \text{Many}$ | Single (`dim_products` $\rightarrow$ `fact_sales`) | **Active** |
| `dim_customers`| `Customer_ID`| `fact_sales` | `Customer_ID`| $1 : \text{Many}$ | Single (`dim_customers` $\rightarrow$ `fact_sales`) | **Active** |
| `dim_regions`  | `Region_ID`  | `fact_sales` | `Region_ID`  | $1 : \text{Many}$ | Single (`dim_regions` $\rightarrow$ `fact_sales`) | **Active** |
| `fact_sales`   | `Transaction_ID` | `dim_returns` | `Transaction_ID` | $1 : 1$ / $1 : \text{Many}$ | Single (`fact_sales` $\rightarrow$ `dim_returns`) | **Active** |

---

## 3. Advanced Modeling Best Practices Implemented

### A. Single-Direction Cross-Filtering
- All dimensional relationships are set to **Single** direction filtering from Dimension to Fact.
- Bidirectional cross-filtering is deliberately avoided to prevent ambiguous filter paths, circular dependencies, and performance degradation across millions of rows.

### B. Inactive Relationships for Role-Playing Dimensions
- `fact_sales` has two date foreign keys: `Order_Date` and `Ship_Date`.
- The active relationship drives all revenue and order analytics on `Order_Date`.
- Analysis based on shipment dates utilizes DAX `USERELATIONSHIP`:
  ```dax
  Shipped Revenue = 
  CALCULATE(
      [Total Net Revenue],
      USERELATIONSHIP(fact_sales[Ship_Date], dim_date[Full_Date])
  )
  ```

### C. Sort-By Column Configuration
To ensure correct chronological ordering across visual charts and slicers:
- `dim_date[Month_Name]` is explicitly sorted by `dim_date[Month]`.
- `dim_date[Month_Short]` is sorted by `dim_date[Month]`.
- `dim_date[Day_Name]` is sorted by `dim_date[Day_Of_Week]`.
- `dim_date[Year_Quarter]` is sorted by `dim_date[Year_Quarter]` (or surrogate key).

### D. Hiding Foreign Keys and Surrogate Keys
- All numeric FK fields (`Customer_ID`, `Product_ID`, `Region_ID`) in `fact_sales` are hidden in the Power BI Report View (`IsHidden = True`) to prevent end-users from aggregating non-additive keys, ensuring that all reporting uses the proper dimension attributes.

---

## 4. DAX Calendar Table Generator (Alternative to Power Query)

If an analyst prefers creating the Calendar dimension directly within Power BI via DAX:

```dax
Dim_Date_DAX = 
VAR MinDate = MIN(fact_sales[Order_Date])
VAR MaxDate = MAX(fact_sales[Order_Date])
RETURN
ADDCOLUMNS(
    CALENDAR(MinDate, MaxDate),
    "Date_Key", YEAR([Date]) * 10000 + MONTH([Date]) * 100 + DAY([Date]),
    "Year", YEAR([Date]),
    "Quarter", "Q" & FORMAT([Date], "Q"),
    "Year_Quarter", YEAR([Date]) & "-Q" & FORMAT([Date], "Q"),
    "Month", MONTH([Date]),
    "Month_Name", FORMAT([Date], "MMMM"),
    "Month_Short", FORMAT([Date], "MMM"),
    "Year_Month", FORMAT([Date], "YYYY-MM"),
    "Day_Of_Month", DAY([Date]),
    "Day_Of_Week", WEEKDAY([Date], 2),
    "Day_Name", FORMAT([Date], "dddd"),
    "Is_Weekend", IF(WEEKDAY([Date], 2) >= 6, 1, 0)
)
```
