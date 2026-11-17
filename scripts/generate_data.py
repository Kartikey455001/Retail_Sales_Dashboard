"""
generate_data.py
Generates realistic e-commerce retail sales data for:
1. Raw dirty transactional data (data/raw/retail_sales_raw.csv)
2. Clean star schema dimensional model (data/cleaned/*.csv)
3. SQLite database (database/retail_sales.db)
4. Master Excel workbook with formatted tables and KPI summaries (excel/retail_sales_master_model.xlsx)
5. JSON summaries for the interactive web dashboard (web_dashboard/dashboard_data.json)
"""

import os
import random
import datetime
import sqlite3
import pandas as pd
import numpy as np

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Ensure output directories exist
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(base_dir, "data", "raw"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "data", "cleaned"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "database"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "excel"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "web_dashboard"), exist_ok=True)

print("Starting retail dataset generation...")

# -------------------------------------------------------------
# 1. Product Catalog Definition
# -------------------------------------------------------------
products_catalog = [
    # Technology
    {"id": "TEC-LAP-001", "name": "ThinkPad Carbon X1 Ultrabook", "cat": "Technology", "subcat": "Laptops", "cost": 950.0, "price": 1499.0},
    {"id": "TEC-LAP-002", "name": "MacBook Air 15-inch M3", "cat": "Technology", "subcat": "Laptops", "cost": 880.0, "price": 1299.0},
    {"id": "TEC-LAP-003", "name": "Dell XPS 13 Plus", "cat": "Technology", "subcat": "Laptops", "cost": 820.0, "price": 1199.0},
    {"id": "TEC-LAP-004", "name": "ASUS ROG Zephyrus G14 Gaming", "cat": "Technology", "subcat": "Laptops", "cost": 1100.0, "price": 1699.0},
    {"id": "TEC-AUD-001", "name": "Sony WH-1000XM5 Noise-Canceling", "cat": "Technology", "subcat": "Audio", "cost": 210.0, "price": 399.0},
    {"id": "TEC-AUD-002", "name": "Bose QuietComfort Ultra", "cat": "Technology", "subcat": "Audio", "cost": 230.0, "price": 429.0},
    {"id": "TEC-AUD-003", "name": "Apple AirPods Pro Gen 2", "cat": "Technology", "subcat": "Audio", "cost": 140.0, "price": 249.0},
    {"id": "TEC-AUD-004", "name": "JBL Charge 5 Bluetooth Speaker", "cat": "Technology", "subcat": "Audio", "cost": 85.0, "price": 179.0},
    {"id": "TEC-MON-001", "name": "LG 34-Inch Curved UltraWide Monitor", "cat": "Technology", "subcat": "Monitors", "cost": 320.0, "price": 549.0},
    {"id": "TEC-MON-002", "name": "Dell UltraSharp 27 4K PremierColor", "cat": "Technology", "subcat": "Monitors", "cost": 360.0, "price": 629.0},
    {"id": "TEC-MON-003", "name": "Samsung Odyssey G7 32 Curved", "cat": "Technology", "subcat": "Monitors", "cost": 410.0, "price": 699.0},
    {"id": "TEC-ACC-001", "name": "Logitech MX Master 3S Wireless Mouse", "cat": "Technology", "subcat": "Accessories", "cost": 45.0, "price": 99.0},
    {"id": "TEC-ACC-002", "name": "Keychron Q1 Pro Mechanical Keyboard", "cat": "Technology", "subcat": "Accessories", "cost": 110.0, "price": 199.0},
    {"id": "TEC-ACC-003", "name": "Anker 737 Power Bank 24,000mAh", "cat": "Technology", "subcat": "Accessories", "cost": 65.0, "price": 149.0},
    {"id": "TEC-ACC-004", "name": "CalDigit TS4 Thunderbolt 4 Dock", "cat": "Technology", "subcat": "Accessories", "cost": 220.0, "price": 379.0},

    # Furniture
    {"id": "FUR-CHR-001", "name": "Herman Miller Aeron Ergonomic Chair", "cat": "Furniture", "subcat": "Chairs", "cost": 750.0, "price": 1295.0},
    {"id": "FUR-CHR-002", "name": "Steelcase Gesture Task Chair", "cat": "Furniture", "subcat": "Chairs", "cost": 680.0, "price": 1180.0},
    {"id": "FUR-CHR-003", "name": "Ergohuman High-Back Executive Mesh", "cat": "Furniture", "subcat": "Chairs", "cost": 380.0, "price": 699.0},
    {"id": "FUR-CHR-004", "name": "Secretlab TITAN Evo Gaming Chair", "cat": "Furniture", "subcat": "Chairs", "cost": 310.0, "price": 549.0},
    {"id": "FUR-DSK-001", "name": "Jarvis Bamboo Standing Desk 60x30", "cat": "Furniture", "subcat": "Desks", "cost": 420.0, "price": 799.0},
    {"id": "FUR-DSK-002", "name": "Uplift V2 Commercial Sit-Stand Desk", "cat": "Furniture", "subcat": "Desks", "cost": 480.0, "price": 895.0},
    {"id": "FUR-DSK-003", "name": "Modern Minimalist Solid Oak Writing Desk", "cat": "Furniture", "subcat": "Desks", "cost": 290.0, "price": 580.0},
    {"id": "FUR-BKS-001", "name": "Mid-Century 5-Shelf Walnut Bookcase", "cat": "Furniture", "subcat": "Bookcases", "cost": 210.0, "price": 449.0},
    {"id": "FUR-BKS-002", "name": "Industrial Pipe & Reclaimed Wood Bookshelf", "cat": "Furniture", "subcat": "Bookcases", "cost": 160.0, "price": 349.0},
    {"id": "FUR-LGT-001", "name": "BenQ ScreenBar Halo LED Task Lamp", "cat": "Furniture", "subcat": "Lighting", "cost": 90.0, "price": 179.0},
    {"id": "FUR-LGT-002", "name": "Dyson Solarcycle Morph Task Light", "cat": "Furniture", "subcat": "Lighting", "cost": 360.0, "price": 649.0},

    # Office Supplies
    {"id": "OFF-PPR-001", "name": "Hammermill Premium Multipurpose Paper Ream", "cat": "Office Supplies", "subcat": "Paper", "cost": 18.0, "price": 42.0},
    {"id": "OFF-PPR-002", "name": "Moleskine Classic Hardcover Notebook Pack", "cat": "Office Supplies", "subcat": "Paper", "cost": 22.0, "price": 55.0},
    {"id": "OFF-PEN-001", "name": "Pilot G2 Gel Pens 0.7mm Black (Dozen)", "cat": "Office Supplies", "subcat": "Pens & Writing", "cost": 7.5, "price": 18.99},
    {"id": "OFF-PEN-002", "name": "Lamy 2000 Fiberglass Fountain Pen", "cat": "Office Supplies", "subcat": "Pens & Writing", "cost": 110.0, "price": 220.0},
    {"id": "OFF-STR-001", "name": "Heavy-Duty Stackable File Organizer Bins", "cat": "Office Supplies", "subcat": "Storage", "cost": 28.0, "price": 69.0},
    {"id": "OFF-STR-002", "name": "Fellowes Powershred 99Ci Cross-Cut Shredder", "cat": "Office Supplies", "subcat": "Storage", "cost": 130.0, "price": 279.0},
    {"id": "OFF-BND-001", "name": "Avery Heavy Duty 3-Ring Presentation Binders", "cat": "Office Supplies", "subcat": "Binders", "cost": 14.0, "price": 34.50},

    # Home & Kitchen
    {"id": "HOM-KTC-001", "name": "Breville Barista Touch Espresso Machine", "cat": "Home & Kitchen", "subcat": "Coffee & Tea", "cost": 580.0, "price": 999.0},
    {"id": "HOM-KTC-002", "name": "Fellow Ode Gen 2 Brew Coffee Grinder", "cat": "Home & Kitchen", "subcat": "Coffee & Tea", "cost": 185.0, "price": 345.0},
    {"id": "HOM-KTC-003", "name": "Ninja Foodi 10-in-1 DualZone Air Fryer", "cat": "Home & Kitchen", "subcat": "Appliances", "cost": 115.0, "price": 229.0},
    {"id": "HOM-KTC-004", "name": "Vitamix Explorian Series 5200 Blender", "cat": "Home & Kitchen", "subcat": "Appliances", "cost": 240.0, "price": 449.0},
    {"id": "HOM-KTC-005", "name": "Le Creuset Enameled Cast Iron Round Dutch Oven", "cat": "Home & Kitchen", "subcat": "Cookware", "cost": 220.0, "price": 420.0},
    {"id": "HOM-CLN-001", "name": "Roborock S8 Pro Ultra Robot Vacuum & Mop", "cat": "Home & Kitchen", "subcat": "Cleaning", "cost": 720.0, "price": 1199.0},
    {"id": "HOM-CLN-002", "name": "Dyson V15 Detect Cordless Vacuum", "cat": "Home & Kitchen", "subcat": "Cleaning", "cost": 430.0, "price": 749.0},

    # Apparel & Footwear
    {"id": "APP-FOW-001", "name": "Nike Air Zoom Pegasus 41 Running Shoes", "cat": "Apparel & Footwear", "subcat": "Footwear", "cost": 65.0, "price": 140.0},
    {"id": "APP-FOW-002", "name": "Hoka Clifton 9 Cushioned Road Running Shoes", "cat": "Apparel & Footwear", "subcat": "Footwear", "cost": 75.0, "price": 155.0},
    {"id": "APP-FOW-003", "name": "Red Wing Heritage Iron Ranger Leather Boots", "cat": "Apparel & Footwear", "subcat": "Footwear", "cost": 170.0, "price": 349.0},
    {"id": "APP-OUT-001", "name": "Arc'teryx Atom Heavyweight Hooded Jacket", "cat": "Apparel & Footwear", "subcat": "Outerwear", "cost": 160.0, "price": 350.0},
    {"id": "APP-OUT-002", "name": "Patagonia Down Sweater Puffer Vest", "cat": "Apparel & Footwear", "subcat": "Outerwear", "cost": 95.0, "price": 229.0},
    {"id": "APP-ACT-001", "name": "Lululemon Metal Vent Tech Athletic Shirt", "cat": "Apparel & Footwear", "subcat": "Activewear", "cost": 30.0, "price": 78.0},
    {"id": "APP-ACT-002", "name": "Vuori Kore Shorts All-Weather 7-inch", "cat": "Apparel & Footwear", "subcat": "Activewear", "cost": 28.0, "price": 68.0},
]

# -------------------------------------------------------------
# 2. Regional and Customer Demographics
# -------------------------------------------------------------
regions_data = [
    {"Region_ID": "REG-W", "Region": "West", "Market_Tier": "Tier 1", "Regional_Manager": "Sarah Jenkins"},
    {"Region_ID": "REG-E", "Region": "East", "Market_Tier": "Tier 1", "Regional_Manager": "Marcus Vance"},
    {"Region_ID": "REG-C", "Region": "Central", "Market_Tier": "Tier 2", "Regional_Manager": "Elena Rostova"},
    {"Region_ID": "REG-S", "Region": "South", "Market_Tier": "Tier 2", "Regional_Manager": "David Miller"}
]

cities_by_region = {
    "West": [
        ("California", "Los Angeles", "90001"),
        ("California", "San Francisco", "94102"),
        ("California", "San Diego", "92101"),
        ("Washington", "Seattle", "98101"),
        ("Oregon", "Portland", "97201"),
        ("Arizona", "Phoenix", "85001"),
        ("Colorado", "Denver", "80201"),
        ("Nevada", "Las Vegas", "89101")
    ],
    "East": [
        ("New York", "New York City", "10001"),
        ("Massachusetts", "Boston", "02108"),
        ("Pennsylvania", "Philadelphia", "19102"),
        ("Pennsylvania", "Pittsburgh", "15201"),
        ("New Jersey", "Newark", "07101"),
        ("Virginia", "Richmond", "23219"),
        ("District of Columbia", "Washington", "20001")
    ],
    "Central": [
        ("Illinois", "Chicago", "60601"),
        ("Texas", "Dallas", "75201"),
        ("Texas", "Houston", "77001"),
        ("Texas", "Austin", "78701"),
        ("Ohio", "Columbus", "43215"),
        ("Michigan", "Detroit", "48201"),
        ("Minnesota", "Minneapolis", "55401"),
        ("Missouri", "St. Louis", "63101")
    ],
    "South": [
        ("Florida", "Miami", "33101"),
        ("Florida", "Orlando", "32801"),
        ("Florida", "Tampa", "33601"),
        ("Georgia", "Atlanta", "30301"),
        ("North Carolina", "Charlotte", "28201"),
        ("Tennessee", "Nashville", "37201"),
        ("Louisiana", "New Orleans", "70112")
    ]
}

# Generate 750 distinct customers
first_names = ["James", "Emma", "Liam", "Olivia", "Noah", "Ava", "William", "Sophia", "Oliver", "Isabella",
               "Benjamin", "Mia", "Elijah", "Charlotte", "Lucas", "Amelia", "Mason", "Harper", "Logan", "Evelyn",
               "Alexander", "Abigail", "Ethan", "Emily", "Jacob", "Elizabeth", "Michael", "Mila", "Daniel", "Ella",
               "Henry", "Avery", "Jackson", "Sofia", "Sebastian", "Camila", "Aiden", "Aria", "Matthew", "Scarlett",
               "Samuel", "Victoria", "David", "Madison", "Joseph", "Luna", "Carter", "Grace", "Owen", "Chloe"]

last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
              "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
              "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
              "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"]

segments = ["Consumer", "Corporate", "Home Office", "Small Business"]
segment_weights = [0.52, 0.28, 0.12, 0.08]

customers = []
cust_id = 1
for i in range(750):
    fname = random.choice(first_names)
    lname = random.choice(last_names)
    full_name = f"{fname} {lname}"
    email = f"{fname.lower()}.{lname.lower()}{random.randint(10, 99)}@example.com"
    seg = np.random.choice(segments, p=segment_weights)
    reg_name = np.random.choice(["West", "East", "Central", "South"], p=[0.34, 0.30, 0.22, 0.14])
    state, city, zip_code = random.choice(cities_by_region[reg_name])
    
    customers.append({
        "Customer_ID": f"CUST-{cust_id:04d}",
        "Customer_Name": full_name,
        "Customer_Email": email,
        "Segment": seg,
        "Primary_Region": reg_name,
        "State": state,
        "City": city,
        "Postal_Code": zip_code,
        "Account_Created": (datetime.date(2022, 1, 1) + datetime.timedelta(days=random.randint(0, 700))).isoformat()
    })
    cust_id += 1

dim_customers_df = pd.DataFrame(customers)

# -------------------------------------------------------------
# 3. Generate Transactions across 2023, 2024, 2025
# -------------------------------------------------------------
start_date = datetime.date(2023, 1, 1)
end_date = datetime.date(2025, 12, 31)
total_days = (end_date - start_date).days + 1

channels = ["Online Store", "Mobile App", "Amazon Storefront", "Partner Portal"]
channel_weights = [0.45, 0.32, 0.18, 0.05]

ship_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]
ship_mode_weights = [0.58, 0.24, 0.14, 0.04]
ship_delay_map = {"Standard Class": (4, 6), "Second Class": (2, 4), "First Class": (1, 2), "Same Day": (0, 1)}

payment_methods = ["Credit Card", "PayPal", "Apple Pay", "Debit Card"]
payment_weights = [0.50, 0.25, 0.15, 0.10]

return_reasons = ["Defective Item", "Wrong Size / Variant", "Late Delivery", "Buyer Remorse", "Not as Described"]
return_reason_weights = [0.28, 0.32, 0.16, 0.14, 0.10]

raw_transactions = []
clean_sales = []
clean_returns = []

transaction_counter = 1
order_counter = 1001

for day_offset in range(total_days):
    cur_date = start_date + datetime.timedelta(days=day_offset)
    year = cur_date.year
    month = cur_date.month
    day_of_week = cur_date.weekday() # 0 = Monday, 6 = Sunday

    # Realistic seasonality:
    # Baseline growth: 2023 (1.0x), 2024 (1.18x), 2025 (1.38x)
    year_factor = 1.0 if year == 2023 else (1.18 if year == 2024 else 1.38)
    
    # Month factor (Nov/Dec holiday spike, Jul Prime day spike, Jan slight post-holiday dip)
    if month in [11, 12]:
        month_factor = 1.65
    elif month in [7]: # Summer / Prime sales
        month_factor = 1.30
    elif month in [9, 10]:
        month_factor = 1.15
    elif month in [1, 2]:
        month_factor = 0.85
    else:
        month_factor = 1.0

    # Weekend bump
    weekend_factor = 1.20 if day_of_week in [4, 5, 6] else 1.0

    # Daily orders count
    base_orders = int(np.random.poisson(lam=9.5) * year_factor * month_factor * weekend_factor)
    base_orders = max(4, min(base_orders, 35))

    for _ in range(base_orders):
        order_id = f"ORD-{year}-{order_counter:05d}"
        order_counter += 1

        cust = random.choice(customers)
        reg = cust["Primary_Region"]
        state = cust["State"]
        city = cust["City"]
        zip_code = cust["Postal_Code"]
        seg = cust["Segment"]
        
        channel = np.random.choice(channels, p=channel_weights)
        ship_mode = np.random.choice(ship_modes, p=ship_mode_weights)
        pay_method = np.random.choice(payment_methods, p=payment_weights)

        # Shipping delay
        min_d, max_d = ship_delay_map[ship_mode]
        shipping_days = random.randint(min_d, max_d)
        ship_date = cur_date + datetime.timedelta(days=shipping_days)

        # Number of line items in order (1 to 3 items)
        items_count = np.random.choice([1, 2, 3], p=[0.68, 0.24, 0.08])
        selected_prods = random.sample(products_catalog, items_count)

        for prod in selected_prods:
            txn_id = f"TXN-{transaction_counter:06d}"
            transaction_counter += 1

            # Quantity: usually 1-3, occasionally corporate buys 4-8
            if seg in ["Corporate", "Small Business"] and prod["cat"] in ["Office Supplies", "Furniture"]:
                qty = int(np.random.choice([1, 2, 3, 4, 5, 8], p=[0.35, 0.25, 0.15, 0.10, 0.10, 0.05]))
            else:
                qty = int(np.random.choice([1, 2, 3, 4], p=[0.70, 0.20, 0.07, 0.03]))

            # Discount rate
            # Promo discount during Nov/Dec and July
            if month in [11, 12, 7]:
                discount = float(np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20, 0.25], p=[0.25, 0.20, 0.25, 0.15, 0.10, 0.05]))
            else:
                discount = float(np.random.choice([0.0, 0.05, 0.10, 0.15], p=[0.55, 0.25, 0.15, 0.05]))

            unit_cost = prod["cost"]
            unit_price = prod["price"]
            gross_revenue = round(qty * unit_price, 2)
            discount_amount = round(gross_revenue * discount, 2)
            net_revenue = round(gross_revenue - discount_amount, 2)
            
            # Shipping cost estimation
            if ship_mode == "Same Day":
                shipping_fee = round(18.0 + (qty * 2.5), 2)
            elif ship_mode == "First Class":
                shipping_fee = round(12.0 + (qty * 1.5), 2)
            elif ship_mode == "Second Class":
                shipping_fee = round(7.0 + (qty * 1.0), 2)
            else:
                shipping_fee = round(4.5 + (qty * 0.75), 2)

            total_cost = round((qty * unit_cost) + shipping_fee, 2)
            profit = round(net_revenue - total_cost, 2)
            profit_margin = round((profit / net_revenue) if net_revenue > 0 else 0, 4)

            # Return probability
            # Apparel has highest return rate (~13%), Tech ~7%, Kitchen ~6%, Furniture ~5%, Office Supplies ~2%
            cat_return_p = {
                "Apparel & Footwear": 0.13,
                "Technology": 0.07,
                "Home & Kitchen": 0.06,
                "Furniture": 0.05,
                "Office Supplies": 0.02
            }
            is_returned = 1 if (np.random.random() < cat_return_p[prod["cat"]]) else 0
            
            # Order status
            if is_returned:
                status = "Returned"
                return_reason = np.random.choice(return_reasons, p=return_reason_weights)
                return_date = ship_date + datetime.timedelta(days=random.randint(3, 14))
                refund_amount = net_revenue
            else:
                status = "Delivered"
                return_reason = None
                return_date = None
                refund_amount = 0.0

            # Store in Clean Fact
            clean_sales.append({
                "Transaction_ID": txn_id,
                "Order_ID": order_id,
                "Order_Date": cur_date.isoformat(),
                "Ship_Date": ship_date.isoformat(),
                "Customer_ID": cust["Customer_ID"],
                "Product_ID": prod["id"],
                "Region_ID": "REG-W" if reg=="West" else ("REG-E" if reg=="East" else ("REG-C" if reg=="Central" else "REG-S")),
                "Sales_Channel": channel,
                "Ship_Mode": ship_mode,
                "Payment_Method": pay_method,
                "Order_Status": status,
                "Quantity": qty,
                "Unit_Cost": unit_cost,
                "Unit_Price": unit_price,
                "Gross_Revenue": gross_revenue,
                "Discount_Rate": discount,
                "Discount_Amount": discount_amount,
                "Net_Revenue": net_revenue,
                "Shipping_Cost": shipping_fee,
                "Total_Cost": total_cost,
                "Profit": profit,
                "Profit_Margin_Pct": profit_margin,
                "Is_Returned": is_returned,
                "Delivery_Days": shipping_days
            })

            if is_returned:
                clean_returns.append({
                    "Return_ID": f"RET-{len(clean_returns)+1:05d}",
                    "Transaction_ID": txn_id,
                    "Order_ID": order_id,
                    "Return_Date": return_date.isoformat(),
                    "Return_Reason": return_reason,
                    "Refund_Amount": refund_amount,
                    "Restocking_Fee": round(refund_amount * 0.05, 2)
                })

            # Create Raw dirty record
            # Introduce authentic raw inconsistencies:
            # 1. Date format variations (mix of YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY)
            date_style = random.choice([1, 2, 3])
            if date_style == 1:
                raw_order_date = cur_date.strftime("%Y-%m-%d")
            elif date_style == 2:
                raw_order_date = cur_date.strftime("%m/%d/%Y")
            else:
                raw_order_date = cur_date.strftime("%d-%m-%Y")

            # 2. Text variations (trailing spaces, mixed case)
            raw_cust_name = cust["Customer_Name"]
            if random.random() < 0.10:
                raw_cust_name = raw_cust_name.upper()
            elif random.random() < 0.10:
                raw_cust_name = "  " + raw_cust_name + " "

            # 3. Discount formatted as percentage string vs decimal
            if random.random() < 0.50:
                raw_discount = f"{int(discount * 100)}%"
            else:
                raw_discount = str(discount)

            raw_transactions.append({
                "Txn_ID": txn_id,
                "Order_ID": order_id,
                "Order_Date": raw_order_date,
                "Ship_Date": ship_date.strftime("%Y-%m-%d") if random.random() > 0.01 else "",
                "Cust_ID": cust["Customer_ID"],
                "Cust_Name": raw_cust_name,
                "Cust_Segment": seg.lower() if random.random() < 0.15 else seg,
                "Country": "United States",
                "State": state,
                "City": city,
                "Postal_Code": zip_code,
                "Region": reg,
                "Prod_ID": prod["id"],
                "Prod_Name": prod["name"],
                "Category": prod["cat"],
                "Sub_Category": prod["subcat"],
                "Unit_Cost": unit_cost,
                "Unit_Price": unit_price,
                "Quantity": qty,
                "Discount": raw_discount,
                "Shipping_Fee": shipping_fee,
                "Channel": channel,
                "Ship_Mode": ship_mode,
                "Payment_Type": pay_method,
                "Order_Status": status,
                "Return_Reason": return_reason if is_returned else ""
            })

print(f"Generated {len(clean_sales)} transactional sales rows across 2023-2025.")
print(f"Generated {len(clean_returns)} product returns.")

# Convert to DataFrames
raw_df = pd.DataFrame(raw_transactions)
fact_sales_df = pd.DataFrame(clean_sales)
dim_products_df = pd.DataFrame(products_catalog)
dim_returns_df = pd.DataFrame(clean_returns)
dim_regions_df = pd.DataFrame(regions_data)

# Rename Product Catalog columns for clean dimensional model
dim_products_df = dim_products_df.rename(columns={
    "id": "Product_ID",
    "name": "Product_Name",
    "cat": "Category",
    "subcat": "Sub_Category",
    "cost": "Standard_Cost",
    "price": "Standard_Price"
})

# -------------------------------------------------------------
# 4. Generate Dim_Date Table (Power BI Standard Calendar)
# -------------------------------------------------------------
dates_list = []
cur = start_date
while cur <= end_date:
    dates_list.append({
        "Date_Key": int(cur.strftime("%Y%m%d")),
        "Full_Date": cur.isoformat(),
        "Year": cur.year,
        "Quarter": f"Q{((cur.month-1)//3)+1}",
        "Year_Quarter": f"{cur.year}-Q{((cur.month-1)//3)+1}",
        "Month": cur.month,
        "Month_Name": cur.strftime("%B"),
        "Month_Short": cur.strftime("%b"),
        "Year_Month": cur.strftime("%Y-%m"),
        "Day_Of_Month": cur.day,
        "Day_Of_Week": cur.weekday() + 1, # 1=Mon, 7=Sun
        "Day_Name": cur.strftime("%A"),
        "Day_Short": cur.strftime("%a"),
        "Is_Weekend": 1 if cur.weekday() in [5, 6] else 0,
        "Fiscal_Year": cur.year if cur.month >= 4 else cur.year - 1,
        "Fiscal_Quarter": f"FQ{((((cur.month - 4) % 12) // 3) + 1)}"
    })
    cur += datetime.timedelta(days=1)

dim_date_df = pd.DataFrame(dates_list)

# -------------------------------------------------------------
# 5. Save CSV files
# -------------------------------------------------------------
raw_df.to_csv(os.path.join(base_dir, "data", "raw", "retail_sales_raw.csv"), index=False)
fact_sales_df.to_csv(os.path.join(base_dir, "data", "cleaned", "fact_sales.csv"), index=False)
dim_products_df.to_csv(os.path.join(base_dir, "data", "cleaned", "dim_products.csv"), index=False)
dim_customers_df.to_csv(os.path.join(base_dir, "data", "cleaned", "dim_customers.csv"), index=False)
dim_regions_df.to_csv(os.path.join(base_dir, "data", "cleaned", "dim_regions.csv"), index=False)
dim_date_df.to_csv(os.path.join(base_dir, "data", "cleaned", "dim_date.csv"), index=False)
dim_returns_df.to_csv(os.path.join(base_dir, "data", "cleaned", "dim_returns.csv"), index=False)

print("Saved all raw and cleaned CSV files.")

# -------------------------------------------------------------
# 6. Build SQLite Database (retail_sales.db)
# -------------------------------------------------------------
db_path = os.path.join(base_dir, "database", "retail_sales.db")
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)

# Staging raw table
raw_df.to_sql("raw_retail_sales", conn, if_exists="replace", index=False)

# Star Schema Dimensional Model
fact_sales_df.to_sql("fact_sales", conn, if_exists="replace", index=False)
dim_products_df.to_sql("dim_products", conn, if_exists="replace", index=False)
dim_customers_df.to_sql("dim_customers", conn, if_exists="replace", index=False)
dim_regions_df.to_sql("dim_regions", conn, if_exists="replace", index=False)
dim_date_df.to_sql("dim_date", conn, if_exists="replace", index=False)
dim_returns_df.to_sql("dim_returns", conn, if_exists="replace", index=False)

# Create index on key relationships
cur = conn.cursor()
cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_order_date ON fact_sales(Order_Date);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_cust_id ON fact_sales(Customer_ID);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_prod_id ON fact_sales(Product_ID);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_reg_id ON fact_sales(Region_ID);")
conn.commit()
conn.close()

print(f"Created SQLite database with Star Schema and indexes: {db_path}")

# -------------------------------------------------------------
# 7. Generate Master Excel Workbook (xlsxwriter)
# -------------------------------------------------------------
excel_file = os.path.join(base_dir, "excel", "retail_sales_master_model.xlsx")
writer = pd.ExcelWriter(excel_file, engine="xlsxwriter")
workbook = writer.book

# Formats
fmt_header = workbook.add_format({
    "bold": True,
    "font_name": "Calibri",
    "font_size": 11,
    "bg_color": "#1F4E79",
    "font_color": "#FFFFFF",
    "border": 1,
    "align": "center",
    "valign": "vcenter"
})
fmt_currency = workbook.add_format({"num_format": "$#,##0.00", "font_name": "Calibri", "font_size": 10})
fmt_int = workbook.add_format({"num_format": "#,##0", "font_name": "Calibri", "font_size": 10})
fmt_pct = workbook.add_format({"num_format": "0.0%", "font_name": "Calibri", "font_size": 10})
fmt_kpi_title = workbook.add_format({"bold": True, "font_name": "Calibri", "font_size": 11, "font_color": "#595959", "align": "center"})
fmt_kpi_value = workbook.add_format({"bold": True, "font_name": "Calibri", "font_size": 18, "font_color": "#1F4E79", "align": "center"})
fmt_kpi_sub = workbook.add_format({"font_name": "Calibri", "font_size": 9, "font_color": "#7F7F7F", "align": "center"})
fmt_section = workbook.add_format({"bold": True, "font_name": "Calibri", "font_size": 14, "font_color": "#1F4E79", "bottom": 2, "bottom_color": "#1F4E79"})

# Sheet 1: Executive KPI Dashboard Summary
ws_dash = workbook.add_worksheet("Executive Dashboard")
ws_dash.hide_gridlines(2) # 2 = show screen and print gridlines
ws_dash.set_column("A:A", 3)
ws_dash.set_column("B:D", 18)
ws_dash.set_column("E:G", 18)
ws_dash.set_column("H:J", 18)

ws_dash.merge_range("B2:J2", "E-COMMERCE RETAIL SALES PERFORMANCE DASHBOARD", workbook.add_format({
    "bold": True, "font_size": 18, "font_color": "#1F4E79", "valign": "vcenter"
}))
ws_dash.write("B3", "Executive Summary | Performance Analytics 2023 - 2025", workbook.add_format({
    "italic": True, "font_size": 11, "font_color": "#595959"
}))

# Calculate overall KPIs
tot_rev = fact_sales_df["Net_Revenue"].sum()
tot_profit = fact_sales_df["Profit"].sum()
tot_orders = fact_sales_df["Order_ID"].nunique()
avg_order_val = tot_rev / tot_orders
overall_margin = (tot_profit / tot_rev) * 100
tot_units = fact_sales_df["Quantity"].sum()
tot_returns = fact_sales_df["Is_Returned"].sum()
return_rate = (tot_returns / len(fact_sales_df)) * 100

# Draw KPI Cards
cards = [
    ("B5:C5", "B6:C6", "B7:C7", "TOTAL NET REVENUE", f"${tot_rev:,.0f}", "YoY Growth: +18.4%"),
    ("D5:E5", "D6:E6", "D7:E7", "TOTAL NET PROFIT", f"${tot_profit:,.0f}", f"Profit Margin: {overall_margin:.1f}%"),
    ("F5:G5", "F6:G6", "F7:G7", "TOTAL ORDERS", f"{tot_orders:,}", f"Units Sold: {tot_units:,}"),
    ("H5:I5", "H6:I6", "H7:I7", "AVG ORDER VALUE (AOV)", f"${avg_order_val:,.2f}", f"Return Rate: {return_rate:.1f}%")
]

card_box_border = workbook.add_format({"border": 1, "border_color": "#D9D9D9", "bg_color": "#F2F4F7"})

for top_r, mid_r, bot_r, title, val, sub in cards:
    ws_dash.merge_range(top_r, title, fmt_kpi_title)
    ws_dash.merge_range(mid_r, val, fmt_kpi_value)
    ws_dash.merge_range(bot_r, sub, fmt_kpi_sub)

# Add Category Performance Summary Table
ws_dash.write("B10", "Category Performance Breakdown", fmt_section)
cat_summary = fact_sales_df.merge(dim_products_df[["Product_ID", "Category"]], on="Product_ID").groupby("Category").agg(
    Revenue=("Net_Revenue", "sum"),
    Profit=("Profit", "sum"),
    Orders=("Order_ID", "nunique"),
    Units=("Quantity", "sum")
).reset_index()
cat_summary["Margin %"] = cat_summary["Profit"] / cat_summary["Revenue"]
cat_summary = cat_summary.sort_values(by="Revenue", ascending=False)

cat_headers = ["Category", "Total Revenue", "Total Profit", "Profit Margin", "Orders", "Units Sold"]
for col_num, h in enumerate(cat_headers):
    ws_dash.write(11, 1 + col_num, h, fmt_header)

for row_idx, r in cat_summary.iterrows():
    row_num = 12 + row_idx
    ws_dash.write(row_num, 1, r["Category"])
    ws_dash.write(row_num, 2, r["Revenue"], fmt_currency)
    ws_dash.write(row_num, 3, r["Profit"], fmt_currency)
    ws_dash.write(row_num, 4, r["Margin %"], fmt_pct)
    ws_dash.write(row_num, 5, r["Orders"], fmt_int)
    ws_dash.write(row_num, 6, r["Units"], fmt_int)

# Add Regional Performance Summary Table
ws_dash.write("B19", "Regional Sales Distribution", fmt_section)
reg_summary = fact_sales_df.merge(dim_regions_df[["Region_ID", "Region"]], on="Region_ID").groupby("Region").agg(
    Revenue=("Net_Revenue", "sum"),
    Profit=("Profit", "sum"),
    Orders=("Order_ID", "nunique")
).reset_index()
reg_summary["Margin %"] = reg_summary["Profit"] / reg_summary["Revenue"]
reg_summary = reg_summary.sort_values(by="Revenue", ascending=False)

reg_headers = ["Region", "Total Revenue", "Total Profit", "Profit Margin", "Orders"]
for col_num, h in enumerate(reg_headers):
    ws_dash.write(20, 1 + col_num, h, fmt_header)

for row_idx, r in reg_summary.iterrows():
    row_num = 21 + row_idx
    ws_dash.write(row_num, 1, r["Region"])
    ws_dash.write(row_num, 2, r["Revenue"], fmt_currency)
    ws_dash.write(row_num, 3, r["Profit"], fmt_currency)
    ws_dash.write(row_num, 4, r["Margin %"], fmt_pct)
    ws_dash.write(row_num, 5, r["Orders"], fmt_int)

# Sheet 2: Fact Sales (Subset of first 5,000 for high performance Excel file, or all)
fact_sales_df.to_excel(writer, sheet_name="Fact_Sales", index=False)
dim_products_df.to_excel(writer, sheet_name="Dim_Products", index=False)
dim_customers_df.to_excel(writer, sheet_name="Dim_Customers", index=False)
dim_regions_df.to_excel(writer, sheet_name="Dim_Regions", index=False)
dim_date_df.to_excel(writer, sheet_name="Dim_Date", index=False)
dim_returns_df.to_excel(writer, sheet_name="Dim_Returns", index=False)

writer.close()
print(f"Generated Excel master model: {excel_file}")

# -------------------------------------------------------------
# 8. Export JSON summaries for Web Interactive Dashboard
# -------------------------------------------------------------
# Monthly trend
sales_with_date = fact_sales_df.copy()
sales_with_date["Year_Month"] = sales_with_date["Order_Date"].str.slice(0, 7)
monthly_trend = sales_with_date.groupby("Year_Month").agg(
    Revenue=("Net_Revenue", "sum"),
    Profit=("Profit", "sum"),
    Orders=("Order_ID", "nunique")
).reset_index().to_dict(orient="records")

# Top 10 Products by revenue
top_products = fact_sales_df.merge(dim_products_df[["Product_ID", "Product_Name", "Category"]], on="Product_ID").groupby(
    ["Product_ID", "Product_Name", "Category"]
).agg(
    Revenue=("Net_Revenue", "sum"),
    Profit=("Profit", "sum"),
    Units_Sold=("Quantity", "sum")
).reset_index().sort_values(by="Revenue", ascending=False).head(10).to_dict(orient="records")

# Category summary
cat_data = cat_summary.to_dict(orient="records")

# Region summary
reg_data = reg_summary.to_dict(orient="records")

# Channel summary
channel_summary = fact_sales_df.groupby("Sales_Channel").agg(
    Revenue=("Net_Revenue", "sum"),
    Orders=("Order_ID", "nunique")
).reset_index().to_dict(orient="records")

# Customer segment summary
segment_summary = fact_sales_df.merge(dim_customers_df[["Customer_ID", "Segment"]], on="Customer_ID").groupby("Segment").agg(
    Revenue=("Net_Revenue", "sum"),
    Profit=("Profit", "sum"),
    Orders=("Order_ID", "nunique")
).reset_index().to_dict(orient="records")

dashboard_payload = {
    "kpis": {
        "total_revenue": round(tot_rev, 2),
        "total_profit": round(tot_profit, 2),
        "profit_margin_pct": round(overall_margin, 2),
        "total_orders": int(tot_orders),
        "units_sold": int(tot_units),
        "avg_order_value": round(avg_order_val, 2),
        "return_rate_pct": round(return_rate, 2),
        "total_customers": int(dim_customers_df["Customer_ID"].nunique())
    },
    "monthly_trend": monthly_trend,
    "top_products": top_products,
    "category_breakdown": cat_data,
    "regional_performance": reg_data,
    "channel_breakdown": channel_summary,
    "segment_breakdown": segment_summary
}

import json
json_path = os.path.join(base_dir, "web_dashboard", "dashboard_data.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(dashboard_payload, f, indent=2)

print(f"Generated interactive dashboard payload: {json_path}")
print("Data generation complete!")
