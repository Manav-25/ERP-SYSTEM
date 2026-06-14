"""
MINI ERP — Bulk Data Seeder
Adds 90 more products (total 100), 100 sales orders, 100 purchase orders
Run: python database/seed_bulk.py
"""

import pymysql
import random
from datetime import date, timedelta
from decimal import Decimal

# ── DB Connection ──────────────────────────────────────────────────────
DB = dict(host='localhost', user='root', password='', database='mini_erp',
          charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=False)

def get_conn():
    return pymysql.connect(**DB)

# ── Helpers ────────────────────────────────────────────────────────────
def rand_date(start_days_ago=365, end_days_ago=0):
    offset = random.randint(end_days_ago, start_days_ago)
    return date.today() - timedelta(days=offset)

def rand_future_date(min_days=7, max_days=45):
    return date.today() + timedelta(days=random.randint(min_days, max_days))

# ── Product Data ───────────────────────────────────────────────────────
PRODUCT_TEMPLATES = [
    # (name, description, cat_id, cost, price, qty, reorder, strategy, type)
    # Finished Goods (cat 1)
    ('Sofa Set 3+2', '3+2 seater wooden sofa set with cushions', 1, 12000, 28000, 8, 2, 'MTO', 'manufacturing'),
    ('Coffee Table', 'Solid wood coffee table 4x2 ft', 1, 2200, 5500, 20, 5, 'MTS', 'manufacturing'),
    ('Dining Chair', 'Cushioned dining chair with armrests', 1, 1400, 3200, 40, 10, 'MTS', 'manufacturing'),
    ('King Bed Frame', 'King size wooden bed frame with headboard', 1, 9500, 22000, 6, 2, 'MTO', 'manufacturing'),
    ('Queen Bed Frame', 'Queen size wooden bed frame', 1, 7500, 17000, 8, 2, 'MTO', 'manufacturing'),
    ('Single Bed', 'Single wooden bed with storage', 1, 4500, 10000, 12, 3, 'MTS', 'manufacturing'),
    ('Shoe Rack', '4-tier wooden shoe rack', 1, 1800, 4200, 25, 8, 'MTS', 'manufacturing'),
    ('TV Unit', 'Wall-mounted TV unit with shelves', 1, 5500, 13000, 10, 3, 'MTO', 'manufacturing'),
    ('Study Table', 'Student study table with drawer', 1, 2800, 6500, 18, 5, 'MTS', 'manufacturing'),
    ('Computer Desk', 'L-shaped computer desk', 1, 4200, 9800, 12, 4, 'MTS', 'manufacturing'),
    ('Dressing Table', 'Dressing table with mirror', 1, 5000, 11500, 8, 2, 'MTO', 'manufacturing'),
    ('Chest of Drawers', '5-drawer chest of drawers', 1, 4800, 11000, 10, 3, 'MTO', 'manufacturing'),
    ('Side Table', 'Bedside table with drawer', 1, 1200, 2800, 30, 10, 'MTS', 'manufacturing'),
    ('Office Chair', 'Ergonomic office chair', 1, 3500, 8500, 15, 5, 'MTS', 'manufacturing'),
    ('Bar Stool', 'High wooden bar stool', 1, 1600, 3800, 22, 8, 'MTS', 'manufacturing'),
    ('Rocking Chair', 'Traditional rocking chair', 1, 2600, 6000, 10, 3, 'MTS', 'manufacturing'),
    ('Garden Bench', 'Outdoor teak garden bench', 1, 3200, 7500, 12, 4, 'MTS', 'manufacturing'),
    ('Folding Table', 'Foldable multipurpose table', 1, 1500, 3500, 30, 10, 'MTS', 'manufacturing'),
    ('Patio Chair', 'Outdoor wooden patio chair', 1, 1800, 4200, 20, 6, 'MTS', 'manufacturing'),
    ('Kitchen Cabinet', 'Wall-mounted kitchen cabinet', 1, 6500, 15000, 8, 2, 'MTO', 'manufacturing'),
    ('Bathroom Cabinet', 'Bathroom vanity cabinet', 1, 4000, 9500, 10, 3, 'MTO', 'manufacturing'),
    ('Ladder Shelf', '5-tier ladder bookshelf', 1, 2200, 5200, 15, 5, 'MTS', 'manufacturing'),
    ('Corner Shelf', 'Wall-mounted corner shelf', 1, 1100, 2500, 25, 8, 'MTS', 'manufacturing'),
    ('Display Cabinet', 'Glass-door display cabinet', 1, 7000, 16000, 7, 2, 'MTO', 'manufacturing'),
    ('Filing Cabinet', '3-drawer wooden filing cabinet', 1, 3800, 8800, 12, 4, 'MTS', 'manufacturing'),
    # Raw Materials (cat 2)
    ('Sheesham Wood Plank', 'Sheesham wood 6x2 ft plank', 2, 950, 1300, 180, 40, 'MTS', 'purchase'),
    ('Mango Wood Plank', 'Mango wood 6x2 ft plank', 2, 700, 950, 200, 50, 'MTS', 'purchase'),
    ('Rubber Wood Sheet', 'Rubber wood 8x4 ft sheet', 2, 650, 900, 150, 35, 'MTS', 'purchase'),
    ('MDF Sheet 12mm', 'MDF board 8x4 ft 12mm', 2, 450, 650, 250, 60, 'MTS', 'purchase'),
    ('MDF Sheet 18mm', 'MDF board 8x4 ft 18mm', 2, 580, 820, 200, 50, 'MTS', 'purchase'),
    ('Plywood Sheet 12mm', 'Plywood 8x4 ft 12mm', 2, 520, 730, 220, 55, 'MTS', 'purchase'),
    ('Bamboo Sheet', 'Bamboo composite sheet', 2, 400, 580, 100, 25, 'MTS', 'purchase'),
    ('Walnut Wood Plank', 'Premium walnut wood plank', 2, 1800, 2500, 80, 20, 'MTS', 'purchase'),
    ('Oak Wood Plank', 'Oak wood 6x2 ft plank', 2, 2200, 3000, 60, 15, 'MTS', 'purchase'),
    ('Pine Wood Plank', 'Pine wood 6x2 ft plank', 2, 600, 850, 220, 50, 'MTS', 'purchase'),
    # Semi-Finished (cat 3)
    ('Chair Leg Set (4pc)', 'Pre-turned chair leg set', 3, 350, 600, 120, 30, 'MTS', 'manufacturing'),
    ('Table Top Panel', 'Pre-finished table top panel', 3, 1200, 2000, 50, 15, 'MTS', 'manufacturing'),
    ('Drawer Assembly', 'Pre-assembled drawer unit', 3, 800, 1400, 40, 10, 'MTS', 'manufacturing'),
    ('Door Panel Set', 'Wardrobe door panels (pair)', 3, 1500, 2600, 35, 8, 'MTS', 'manufacturing'),
    ('Headboard Panel', 'Bed headboard pre-panel', 3, 1800, 3200, 20, 5, 'MTS', 'manufacturing'),
    ('Cabinet Frame', 'Pre-assembled cabinet frame', 3, 2200, 3800, 18, 5, 'MTS', 'manufacturing'),
    ('Shelf Board Set', 'Set of 5 pre-cut shelf boards', 3, 950, 1600, 45, 12, 'MTS', 'manufacturing'),
    ('Bed Slat Set', 'Bed slat set (12 pcs)', 3, 600, 1000, 60, 15, 'MTS', 'manufacturing'),
    # Consumables (cat 4)
    ('Wood Glue 1L', 'Professional wood adhesive', 4, 180, 280, 200, 50, 'MTS', 'purchase'),
    ('Sandpaper Pack', 'Assorted grit sandpaper pack', 4, 80, 130, 400, 100, 'MTS', 'purchase'),
    ('Wood Stain Dark', 'Dark walnut wood stain 1L', 4, 220, 360, 150, 40, 'MTS', 'purchase'),
    ('Wood Stain Light', 'Light oak wood stain 1L', 4, 220, 360, 150, 40, 'MTS', 'purchase'),
    ('Primer Coat', 'Wood primer coat 1L', 4, 150, 250, 180, 45, 'MTS', 'purchase'),
    ('Lacquer Finish', 'Clear lacquer wood finish 1L', 4, 280, 450, 120, 30, 'MTS', 'purchase'),
    ('Drawer Slider Set', 'Full-extension drawer sliders pair', 4, 120, 200, 300, 75, 'MTS', 'purchase'),
    ('Cabinet Hinge Set', 'Soft-close cabinet hinges pack 10', 4, 90, 150, 350, 80, 'MTS', 'purchase'),
    ('Bolt & Nut Set', 'Furniture bolt and nut set 50pc', 4, 60, 100, 600, 150, 'MTS', 'purchase'),
    ('Corner Bracket Set', 'Metal corner brackets 20pc', 4, 75, 120, 400, 100, 'MTS', 'purchase'),
    ('Dowel Pins Pack', 'Wooden dowel pins 50pc', 4, 40, 70, 500, 120, 'MTS', 'purchase'),
    ('Foam Sheet 2in', '2-inch foam sheet 6x3 ft', 4, 350, 550, 100, 25, 'MTS', 'purchase'),
    ('Foam Sheet 4in', '4-inch foam sheet 6x3 ft', 4, 650, 1000, 80, 20, 'MTS', 'purchase'),
    ('Velvet Fabric 1m', 'Upholstery velvet fabric per meter', 4, 180, 300, 300, 75, 'MTS', 'purchase'),
    ('Jute Fabric 1m', 'Natural jute upholstery fabric', 4, 90, 150, 400, 100, 'MTS', 'purchase'),
    ('D-Ring Hooks 10pc', 'D-ring picture hanging hooks', 4, 50, 85, 600, 150, 'MTS', 'purchase'),
    # Spare Parts (cat 5)
    ('Caster Wheel Set', 'Furniture caster wheels 4pc set', 5, 140, 250, 200, 50, 'MTS', 'purchase'),
    ('Leveling Foot 4pc', 'Adjustable leveling feet set', 5, 80, 140, 300, 75, 'MTS', 'purchase'),
    ('Table Leg Extender', 'Adjustable leg height extender', 5, 110, 190, 180, 45, 'MTS', 'purchase'),
    ('Glass Shelf Bracket', 'Glass shelf support bracket pair', 5, 95, 160, 250, 60, 'MTS', 'purchase'),
    ('Sofa Leg Set 4pc', 'Replacement sofa wooden leg set', 5, 320, 550, 100, 25, 'MTS', 'purchase'),
    ('Cabinet Lock', 'Furniture push-lock mechanism', 5, 65, 110, 400, 100, 'MTS', 'purchase'),
    ('Drawer Handle', 'Chrome-finish drawer handle', 5, 45, 80, 600, 150, 'MTS', 'purchase'),
    ('Door Knob Wooden', 'Wooden decorative door knob', 5, 55, 95, 500, 120, 'MTS', 'purchase'),
    ('Rubber Foot Pad', 'Self-adhesive rubber foot pads 8pc', 5, 30, 55, 800, 200, 'MTS', 'purchase'),
    ('Chair Leg Cap', 'Plastic leg caps (fits 25mm) 4pc', 5, 25, 45, 1000, 250, 'MTS', 'purchase'),
]

SO_STATUSES   = ['draft', 'confirmed', 'confirmed', 'dispatched', 'delivered', 'delivered', 'cancelled']
PO_STATUSES   = ['draft', 'confirmed', 'confirmed', 'fully_received', 'fully_received', 'cancelled']

def seed_products(conn):
    print(">> Seeding products...")
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) as c FROM products")
        existing = cur.fetchone()['c']

    added = 0
    with conn.cursor() as cur:
        for i, p in enumerate(PRODUCT_TEMPLATES, existing + 1):
            code = f'PRD-{i:03d}'
            # Skip if code already exists
            cur.execute("SELECT id FROM products WHERE product_code=%s", (code,))
            if cur.fetchone():
                continue
            cur.execute("""
                INSERT INTO products
                  (product_code, product_name, description, category_id,
                   cost_price, sales_price, on_hand_qty, reorder_point,
                   procurement_strategy, procurement_type, is_active, created_by)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,1)
            """, (code, p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8]))

            # Stock ledger opening entry
            cur.execute("""
                INSERT INTO stock_ledger
                  (product_id, movement_type, quantity, balance_qty,
                   unit_cost, reference_number, notes, created_by)
                VALUES (LAST_INSERT_ID(),'opening_stock',%s,%s,%s,'OPENING','Opening stock',1)
            """, (p[5], p[5], p[3]))
            added += 1

    conn.commit()
    print(f"   OK Added {added} products")


def seed_sales_orders(conn, count=100):
    print(">> Seeding sales orders...")
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM customers WHERE is_active=1")
        customers = [r['id'] for r in cur.fetchall()]
        cur.execute("SELECT id, sales_price FROM products WHERE is_active=1")
        products = cur.fetchall()
        cur.execute("SELECT last_number FROM sequence_counters WHERE prefix='SO'")
        row = cur.fetchone()
        seq = (row['last_number'] or 0)

    added = 0
    with conn.cursor() as cur:
        for _ in range(count):
            seq += 1
            order_num  = f'SO-{seq:05d}'
            cust_id    = random.choice(customers)
            order_date = rand_date(365, 0)
            exp_del    = order_date + timedelta(days=random.randint(7, 30))
            status     = random.choice(SO_STATUSES)
            num_items  = random.randint(1, 4)
            items      = random.sample(products, min(num_items, len(products)))

            subtotal = 0
            tax_amt  = 0
            for it in items:
                qty   = random.randint(1, 10)
                price = float(it['sales_price']) * random.uniform(0.9, 1.1)
                tax   = random.choice([0, 5, 12, 18])
                base  = qty * price
                line  = base * (1 + tax / 100)
                subtotal += base
                tax_amt  += line - base

            total = subtotal + tax_amt

            cur.execute("""
                INSERT INTO sales_orders
                  (order_number, customer_id, order_date, expected_delivery_date,
                   status, subtotal, tax_amount, discount_amount, total_amount,
                   notes, created_by)
                VALUES (%s,%s,%s,%s,%s,%s,%s,0,%s,%s,1)
            """, (order_num, cust_id, order_date, exp_del,
                  status, round(subtotal, 2), round(tax_amt, 2),
                  round(total, 2),
                  random.choice(['', 'Urgent delivery', 'Handle with care',
                                 'Include installation', 'Call before delivery', ''])))
            so_id = cur.lastrowid

            for it in items:
                qty   = random.randint(1, 10)
                price = float(it['sales_price']) * random.uniform(0.9, 1.1)
                tax   = random.choice([0, 5, 12, 18])
                base  = qty * price
                line  = base * (1 + tax / 100)
                cur.execute("""
                    INSERT INTO sales_order_items
                      (sales_order_id, product_id, ordered_qty, delivered_qty,
                       unit_price, discount_pct, tax_pct, line_total)
                    VALUES (%s,%s,%s,0,%s,0,%s,%s)
                """, (so_id, it['id'], qty, round(price, 2), tax, round(line, 2)))

            added += 1

        cur.execute("UPDATE sequence_counters SET last_number=%s WHERE prefix='SO'", (seq,))

    conn.commit()
    print(f"   OK Added {added} sales orders")


def seed_purchase_orders(conn, count=100):
    print(">> Seeding purchase orders...")
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM vendors WHERE is_active=1")
        vendors = [r['id'] for r in cur.fetchall()]
        cur.execute("SELECT id, cost_price FROM products WHERE is_active=1 AND procurement_type='purchase'")
        products = cur.fetchall()
        if not products:
            cur.execute("SELECT id, cost_price FROM products WHERE is_active=1")
            products = cur.fetchall()
        cur.execute("SELECT last_number FROM sequence_counters WHERE prefix='PO'")
        row = cur.fetchone()
        seq = (row['last_number'] or 0)

    added = 0
    with conn.cursor() as cur:
        for _ in range(count):
            seq += 1
            order_num    = f'PO-{seq:05d}'
            vend_id      = random.choice(vendors)
            order_date   = rand_date(365, 0)
            exp_receipt  = order_date + timedelta(days=random.randint(5, 20))
            status       = random.choice(PO_STATUSES)
            num_items    = random.randint(1, 4)
            items        = random.sample(products, min(num_items, len(products)))

            subtotal = 0
            tax_amt  = 0
            for it in items:
                qty   = random.randint(10, 100)
                price = float(it['cost_price']) * random.uniform(0.88, 1.05)
                tax   = random.choice([0, 5, 12, 18])
                base  = qty * price
                line  = base * (1 + tax / 100)
                subtotal += base
                tax_amt  += line - base

            total = subtotal + tax_amt

            cur.execute("""
                INSERT INTO purchase_orders
                  (order_number, vendor_id, order_date, expected_receipt_date,
                   status, subtotal, tax_amount, total_amount,
                   notes, created_by)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,1)
            """, (order_num, vend_id, order_date, exp_receipt,
                  status, round(subtotal, 2), round(tax_amt, 2), round(total, 2),
                  random.choice(['', 'Priority order', 'Quality check required',
                                 'Bulk discount applied', 'Advance paid', ''])))
            po_id = cur.lastrowid

            for it in items:
                qty   = random.randint(10, 100)
                price = float(it['cost_price']) * random.uniform(0.88, 1.05)
                tax   = random.choice([0, 5, 12, 18])
                base  = qty * price
                line  = base * (1 + tax / 100)
                recv  = qty if status == 'fully_received' else 0
                cur.execute("""
                    INSERT INTO purchase_order_items
                      (purchase_order_id, product_id, ordered_qty, received_qty,
                       unit_price, tax_pct, line_total)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (po_id, it['id'], qty, recv, round(price, 2), tax, round(line, 2)))

            added += 1

        cur.execute("UPDATE sequence_counters SET last_number=%s WHERE prefix='PO'", (seq,))

    conn.commit()
    print(f"   OK Added {added} purchase orders")


# ── Main ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 55)
    print("  MINI ERP - Bulk Seeder")
    print("  Adding 90 products + 100 sales + 100 purchase orders")
    print("=" * 55)

    conn = get_conn()
    try:
        seed_products(conn)
        seed_sales_orders(conn, 100)
        seed_purchase_orders(conn, 100)
        print("=" * 55)
        print("  All done! Refresh your browser.")
        print("=" * 55)
    except Exception as e:
        conn.rollback()
        print(f"\n  ERROR: {e}")
        import traceback; traceback.print_exc()
    finally:
        conn.close()
