# Power BI Interactive Dashboard Design & Implementation Guide
**Project:** E-Commerce Retail Sales Performance Analytics  
**Display Format:** 16:9 Canvas (1920 x 1080 px or 1280 x 720 px)  
**Theme:** Enterprise Modern Dark Slate / Corporate Blue

---

## 1. Visual Design System & Palette

| Element | Color Hex | Visual Usage |
| :--- | :--- | :--- |
| **Primary Navy** | `#1E293B` | Executive headers, sidebar banner, primary visual accents |
| **Accent Emerald** | `#10B981` | Positive YoY variance, healthy profit margins ($\ge 35\%$), revenue indicators |
| **Accent Amber** | `#F59E0B` | Medium margin warnings, moderate shipping delays |
| **Alert Rose/Red**| `#EF4444` | Negative YoY variance, high return rates, margin deficits |
| **Canvas Background** | `#F8FAFC` | Light neutral background for high contrast & clarity |
| **Card Surface** | `#FFFFFF` | Card containers with `0 1px 3px rgba(0,0,0,0.1)` drop shadow |
| **Body Typography** | `Segoe UI` | Standard Power BI enterprise font (9pt regular, 11pt semibold, 20pt bold) |

---

## 2. Page 1: Executive Overview Dashboard

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  [Logo] RETAIL SALES PERFORMANCE DASHBOARD | Executive Overview    [2023-2025 Slicers] │
├──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬─────────────┤
│ TOTAL REVENUE│ TOTAL PROFIT │ PROFIT MARGIN│ TOTAL ORDERS │     AOV      │ RETURN RATE │
│   $15.33M    │    $6.00M    │    39.1%     │    14,904    │  $1,028.88   │    6.6%     │
│  ▲ +16.9% YoY│  ▲ +17.2% YoY│  ▲ +0.1% YoY │  ▲ +16.2% YoY│   ▲ +0.6% YoY│  ▼ -0.3% YoY│
├──────────────┴──────────────┴──────────────┼──────────────┴──────────────┴─────────────┤
│ [CHART 1: Monthly Revenue & Profit Trend]  │ [CHART 2: Category Revenue Breakdown]     │
│ Line & Clustered Column:                   │ Donut Chart:                              │
│ • Columns: Net Revenue                     │ • Technology ($7.2M, 47%)                 │
│ • Line: Net Profit                         │ • Furniture ($4.1M, 27%)                  │
│ • Dashed Line: 3-Month Rolling Average     │ • Home & Kitchen ($2.3M, 15%)             │
│                                            │ • Apparel & Footwear ($1.1M, 7%)          │
│                                            │ • Office Supplies ($0.6M, 4%)             │
├────────────────────────────────────────────┼───────────────────────────────────────────┤
│ [CHART 3: Regional Sales & Profitability]  │ [CHART 4: Sales Channel Contribution]     │
│ Clustered Bar Chart:                       │ Horizontal 100% Stacked Bar:              │
│ • West Region (Leader: $5.2M, 39.2% margin)│ • Online Store (45%)                      │
│ • East Region ($4.6M, 39.0% margin)        │ • Mobile App (32%)                        │
│ • Central Region ($3.4M, 38.9% margin)     │ • Amazon Storefront (18%)                 │
│ • South Region ($2.1M, 39.4% margin)       │ • Partner Portal (5%)                     │
└────────────────────────────────────────────┴───────────────────────────────────────────┘
```

### Visual Specifications for Page 1:
1. **Top Header & Global Slicer Bar:**
   - **Date Range Slicer:** Between slider on `dim_date[Full_Date]`.
   - **Year / Quarter Buttons:** Chiclet / Tile slicer using `dim_date[Year]` and `dim_date[Quarter]`.
   - **Region Dropdown:** Dropdown slicer from `dim_regions[Region]`.
   - **Customer Segment Dropdown:** Dropdown slicer from `dim_customers[Segment]`.
2. **KPI Scorecard Strip (New Card Visual):**
   - **Card 1:** Callout: `[Total Net Revenue]`. Subtitle: `[KPI Card Revenue Subtitle]`. Conditional formatting color linked to `[KPI Color YoY Growth]`.
   - **Card 2:** Callout: `[Total Profit]`. Subtitle: `[YoY Profit Growth %]`.
   - **Card 3:** Callout: `[Profit Margin %]`. Subtitle: `Margin Target: 35%`.
   - **Card 4:** Callout: `[Total Orders]`. Subtitle: `[Total Units Sold]`.
   - **Card 5:** Callout: `[Average Order Value]`. Subtitle: `Average Spend / Order`.
3. **Monthly Trend Visual (Combo Chart):**
   - **X-Axis:** `dim_date[Year_Month]`
   - **Column Y-Axis:** `[Total Net Revenue]`
   - **Line Y-Axis:** `[Total Profit]`, `[Rolling 3-Month Revenue]`
4. **Category Donut Visual:**
   - **Legend:** `dim_products[Category]`
   - **Values:** `[Total Net Revenue]`
   - **Detail Labels:** Category Name + Data Value + Percent of Total.

---

## 3. Page 2: Product & Category Deep-Dive

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  RETAIL SALES PERFORMANCE | Product & Category Deep-Dive            [Filter: Category] │
├────────────────────────────────────────────┬───────────────────────────────────────────┤
│ [CHART 1: Top 10 SKUs by Net Revenue]      │ [CHART 2: Volume vs Profit Margin %]      │
│ Horizontal Bar Chart:                      │ Scatter Plot:                             │
│ 1. ThinkPad Carbon X1 Ultrabook ($1.8M)    │ • X-Axis: Total Units Sold                │
│ 2. Herman Miller Aeron Chair ($1.6M)       │ • Y-Axis: Profit Margin %                 │
│ 3. ASUS ROG Zephyrus G14 ($1.4M)           │ • Bubble Size: Net Revenue                │
│ 4. MacBook Air 15-inch M3 ($1.3M)          │ • Color: Category                         │
│ 5. Roborock S8 Pro Robot Vacuum ($1.1M)    │ • Quadrant lines: Target Margin (35%),    │
│ 6. Steelcase Gesture Task Chair ($1.0M)    │   Avg Volume (600 units)                  │
├────────────────────────────────────────────┴───────────────────────────────────────────┤
│ [TABLE 1: Comprehensive Sub-Category Performance Matrix]                              │
│ Columns: Sub-Category | Units Sold | Gross Rev | Discount % | Net Rev | Profit | Margin│
│ • In-cell conditional formatting data bars for Revenue and Margin %                   │
│ • Drill-through enabled to Transaction Details                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Visual Specifications for Page 2:
1. **Top 10 Products Ranking Visual:**
   - **Y-Axis:** `dim_products[Product_Name]` (Filtered via Top N filter: Top 10 by `[Total Net Revenue]`).
   - **X-Axis:** `[Total Net Revenue]`.
   - **Data Labels:** Enabled, displaying value formatted in millions (`$1.8M`).
2. **Scatter Plot (Portfolio Quadrant Analysis):**
   - **X-Axis:** `[Total Units Sold]`
   - **Y-Axis:** `[Profit Margin %]`
   - **Size:** `[Total Net Revenue]`
   - **Play Axis:** `dim_date[Year]` (Allows animating product shifts over time).
   - **Reference Lines:** Constant X at median volume; Constant Y at 35% margin threshold.
3. **Sub-Category Matrix:**
   - **Rows:** `dim_products[Category]`, `dim_products[Sub_Category]`
   - **Values:** `[Total Units Sold]`, `[Total Net Revenue]`, `[Total Discounts]`, `[Total Profit]`, `[Profit Margin %]`
   - **Formatting:** Data bars on `Total Net Revenue`; Gradient background color on `Profit Margin %` (Red to Green).

---

## 4. Page 3: Customer & Regional Geography

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  RETAIL SALES PERFORMANCE | Customer & Regional Analytics           [Filter: Region]   │
├────────────────────────────────────────────┬───────────────────────────────────────────┤
│ [CHART 1: US State-Level Revenue Map]      │ [CHART 2: Customer Segment Matrix]        │
│ Filled / Bubble Map:                       │ Clustered Bar:                            │
│ • State location (California, New York,    │ • Consumer: $8.0M Revenue | $1,025 AOV    │
│   Texas, Florida, Washington, etc.)        │ • Corporate: $4.3M Revenue | $1,040 AOV   │
│ • Bubble Size: [Total Net Revenue]         │ • Home Office: $1.8M Revenue | $1,020 AOV │
│ • Tooltip: Regional Director, Orders, AOV  │ • Small Business: $1.2M Rev | $1,032 AOV  │
├────────────────────────────────────────────┼───────────────────────────────────────────┤
│ [CHART 3: RFM Customer Tier Distribution]  │ [CHART 4: Shipping Mode & Delivery SLA]   │
│ Treemap / Stacked Column:                  │ Clustered Bar & Line:                     │
│ • Super VIP Loyalists (23+ Orders, 34% rev)│ • Standard Class: 5.0 Days ($8.9M Rev)    │
│ • Core Regulars (16-22 Orders, 55% rev)    │ • Second Class: 3.0 Days ($3.7M Rev)      │
│ • Occasional Buyers (<=15 Orders, 11% rev) │ • First Class: 1.5 Days ($2.1M Rev)       │
│                                            │ • Same Day: 0.5 Days ($0.6M Rev)          │
└────────────────────────────────────────────┴───────────────────────────────────────────┘
```

---

## 5. Page 4: Returns & Operational Risk Analysis

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  RETAIL SALES PERFORMANCE | Returns & Operational Risk Audit       [Filter: Status]    │
├────────────────────────────────────────────┬───────────────────────────────────────────┤
│ [CHART 1: Return Rate % by Category]       │ [CHART 2: Return Reasons Root-Cause]      │
│ Bar Chart with Target Benchmark:           │ Pareto / Donut Chart:                     │
│ • Apparel & Footwear: 13.2% (High Alert)   │ • Wrong Size / Variant: 32%               │
│ • Technology: 7.1%                         │ • Defective Item: 28%                     │
│ • Home & Kitchen: 6.2%                     │ • Late Delivery: 16%                      │
│ • Furniture: 5.1%                          │ • Buyer Remorse: 14%                      │
│ • Office Supplies: 2.0% (Low Risk)         │ • Not as Described: 10%                   │
├────────────────────────────────────────────┴───────────────────────────────────────────┤
│ [FINANCIAL IMPACT SUMMARY]: Gross Value Returned: $1.01M | Refunds Issued: $1.01M     │
│ Restocking Fees Recovered: $50.5K | Net Margin Impact: -2.1% Company Profit           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Interactive Features: Drill-Through, Bookmarks & Tooltips

1. **Custom Report Page Tooltips:**
   - Create a dedicated tooltip canvas ($320 \times 240$ px) named `Tooltip_Product`.
   - When hovering over any product bar on Page 1 or 2, the tooltip displays: SKU Image / Code, 12-month mini sparkline of revenue, return rate %, and unit margin.
2. **Page Navigation Bookmarks:**
   - Implement buttons on the top navigation bar linking between:
     - 📊 *Overview* $\rightarrow$ Page 1
     - 📦 *Products* $\rightarrow$ Page 2
     - 👥 *Customers & Regions* $\rightarrow$ Page 3
     - ⚠️ *Returns & SLA* $\rightarrow$ Page 4
3. **Clear All Filters Action:**
   - A bookmark button titled **"Reset Filters"** that reverts all slicers to their default state (All Years, All Categories, All Regions).
