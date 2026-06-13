-- ============================================================
-- MINI ERP - Seed Data
-- ============================================================
USE mini_erp;

-- Sequence Counters
INSERT INTO sequence_counters (prefix, last_number) VALUES
('SO', 0), ('PO', 0), ('MO', 0), ('WO', 0),
('DEL', 0), ('GR', 0), ('BOM', 0), ('CUST', 0), ('VEND', 0);

-- Roles
INSERT INTO roles (name, description) VALUES
('admin', 'Full system access'),
('sales_user', 'Sales order management'),
('purchase_user', 'Purchase order management'),
('manufacturing_user', 'Manufacturing management'),
('inventory_manager', 'Inventory and stock management'),
('business_owner', 'Dashboard and reports access');

-- Permissions
INSERT INTO permissions (module, action, description) VALUES
('users','read','View users'),('users','create','Create users'),('users','update','Update users'),('users','delete','Delete users'),
('products','read','View products'),('products','create','Create products'),('products','update','Update products'),('products','delete','Delete products'),
('sales','read','View sales'),('sales','create','Create sales'),('sales','update','Update sales'),('sales','delete','Delete sales'),
('purchase','read','View purchase'),('purchase','create','Create purchase'),('purchase','update','Update purchase'),('purchase','delete','Delete purchase'),
('manufacturing','read','View manufacturing'),('manufacturing','create','Create manufacturing'),('manufacturing','update','Update manufacturing'),
('inventory','read','View inventory'),('inventory','adjust','Adjust inventory'),
('bom','read','View BoM'),('bom','create','Create BoM'),('bom','update','Update BoM'),
('reports','read','View reports'),('audit','read','View audit logs'),
('dashboard','read','View dashboard');

-- Admin user (password: Admin@123)
INSERT INTO users (username, email, password_hash, full_name, is_active) VALUES
('admin', 'admin@minierp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMqJqhcanFp8.uW9MRPJmNjFve', 'System Administrator', TRUE),
('sales1', 'sales@minierp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMqJqhcanFp8.uW9MRPJmNjFve', 'Sales User', TRUE),
('purchase1', 'purchase@minierp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMqJqhcanFp8.uW9MRPJmNjFve', 'Purchase User', TRUE),
('mfg1', 'mfg@minierp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMqJqhcanFp8.uW9MRPJmNjFve', 'Manufacturing User', TRUE),
('inv1', 'inventory@minierp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMqJqhcanFp8.uW9MRPJmNjFve', 'Inventory Manager', TRUE),
('owner', 'owner@minierp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMqJqhcanFp8.uW9MRPJmNjFve', 'Business Owner', TRUE);

-- Assign roles to users
INSERT INTO user_roles (user_id, role_id) VALUES
(1,1),(2,2),(3,3),(4,4),(5,5),(6,6);

-- Categories
INSERT INTO categories (name, description) VALUES
('Finished Goods', 'Final manufactured products'),
('Raw Materials', 'Raw materials for manufacturing'),
('Semi-Finished', 'Work-in-progress products'),
('Consumables', 'Consumable items'),
('Spare Parts', 'Spare parts and accessories');

-- Work Centers
INSERT INTO work_centers (name, description, capacity_per_hour, cost_per_hour) VALUES
('Assembly Station', 'Main furniture assembly', 5.00, 150.00),
('Painting Station', 'Paint and finishing', 8.00, 100.00),
('Packing Station', 'Product packing and dispatch', 10.00, 75.00),
('CNC Machine', 'Wood cutting and shaping', 3.00, 200.00),
('Quality Control', 'QC inspection', 15.00, 125.00);

-- Sample Products
INSERT INTO products (product_code, product_name, description, category_id, cost_price, sales_price, on_hand_qty, reorder_point, procurement_strategy, procurement_type) VALUES
('PRD-001', 'Wooden Chair', '4-leg wooden chair with cushion', 1, 1200.00, 2500.00, 50.000, 10.000, 'MTS', 'manufacturing'),
('PRD-002', 'Wooden Table', '6-seater dining table', 1, 3500.00, 7500.00, 20.000, 5.000, 'MTO', 'manufacturing'),
('PRD-003', 'Teak Wood Plank', 'Premium teak wood 6x2 ft', 2, 800.00, 1100.00, 200.000, 50.000, 'MTS', 'purchase'),
('PRD-004', 'Wood Screws (Pack)', 'Box of 100 screws', 4, 50.00, 80.00, 500.000, 100.000, 'MTS', 'purchase'),
('PRD-005', 'Chair Cushion', 'Foam cushion for chair', 2, 200.00, 350.00, 100.000, 20.000, 'MTS', 'purchase'),
('PRD-006', 'Wood Polish', 'Premium teak wood polish 1L', 4, 120.00, 200.00, 80.000, 15.000, 'MTS', 'purchase'),
('PRD-007', 'Wooden Wardrobe', '3-door wooden wardrobe', 1, 8000.00, 18000.00, 10.000, 3.000, 'MTO', 'manufacturing'),
('PRD-008', 'Bookshelf', '5-shelf wooden bookshelf', 1, 2500.00, 5500.00, 15.000, 5.000, 'MTS', 'manufacturing'),
('PRD-009', 'Nails Pack', 'Pack of 200 nails', 4, 30.00, 50.00, 300.000, 50.000, 'MTS', 'purchase'),
('PRD-010', 'Plywood Sheet', '8x4 ft plywood 18mm', 2, 600.00, 850.00, 150.000, 30.000, 'MTS', 'purchase');

-- Sample Customers
INSERT INTO customers (customer_code, company_name, contact_name, email, phone, city, state, gst_number) VALUES
('CUST-001', 'Ramesh Furniture Mart', 'Ramesh Kumar', 'ramesh@example.com', '9876543210', 'Mumbai', 'Maharashtra', '27AABCR1234A1Z5'),
('CUST-002', 'Modern Home Decor', 'Priya Sharma', 'priya@modernhome.com', '9812345678', 'Pune', 'Maharashtra', '27AABCS5678B2Z6'),
('CUST-003', 'City Interiors', 'Amit Patel', 'amit@cityinteriors.com', '9823456789', 'Nashik', 'Maharashtra', '27AABCC9012C3Z7'),
('CUST-004', 'Royal Furnishings', 'Sunita Desai', 'sunita@royalfurni.com', '9834567890', 'Aurangabad', 'Maharashtra', '27AABCR3456D4Z8'),
('CUST-005', 'Home & Living', 'Vijay Singh', 'vijay@homeliving.com', '9845678901', 'Nagpur', 'Maharashtra', '27AABCH7890E5Z9');

-- Sample Vendors
INSERT INTO vendors (vendor_code, company_name, contact_name, email, phone, city, state, lead_time_days) VALUES
('VEND-001', 'Timber World', 'Suresh Joshi', 'suresh@timberworld.com', '9765432109', 'Kolhapur', 'Maharashtra', 7),
('VEND-002', 'Hardware Plus', 'Mahesh Kulkarni', 'mahesh@hwplus.com', '9754321098', 'Pune', 'Maharashtra', 3),
('VEND-003', 'Foam Masters', 'Rekha Nair', 'rekha@foammasters.com', '9743210987', 'Mumbai', 'Maharashtra', 5),
('VEND-004', 'Polish & Finish Co.', 'Ganesh Rao', 'ganesh@polishco.com', '9732109876', 'Hyderabad', 'Telangana', 10),
('VEND-005', 'Plywood King', 'Deepak Shah', 'deepak@plywoodking.com', '9721098765', 'Ahmedabad', 'Gujarat', 7);

-- Sample BOM: Wooden Chair
INSERT INTO boms (bom_code, product_id, version, quantity, notes, created_by) VALUES
('BOM-001', 1, '1.0', 1.000, 'Standard wooden chair BOM', 1);

INSERT INTO bom_components (bom_id, component_product_id, quantity, unit_of_measure) VALUES
(1, 3, 2.000, 'PCS'),  -- Teak Wood Plank x2
(1, 4, 1.000, 'PCS'),  -- Wood Screws x1
(1, 5, 1.000, 'PCS'),  -- Chair Cushion x1
(1, 6, 0.250, 'LTR'),  -- Wood Polish 250ml
(1, 9, 0.500, 'PCS');  -- Nails Pack x0.5

INSERT INTO operations (bom_id, name, work_center_id, sequence, duration_hours) VALUES
(1, 'Wood Cutting & Shaping', 4, 1, 1.00),
(1, 'Assembly', 1, 2, 2.00),
(1, 'Painting & Finishing', 2, 3, 1.50),
(1, 'Quality Check', 5, 4, 0.50),
(1, 'Packing', 3, 5, 0.25);

-- Opening Stock Ledger
INSERT INTO stock_ledger (product_id, movement_type, quantity, balance_qty, unit_cost, reference_number, notes, created_by) VALUES
(1, 'opening_stock', 50.000, 50.000, 1200.00, 'OPENING', 'Opening stock', 1),
(2, 'opening_stock', 20.000, 20.000, 3500.00, 'OPENING', 'Opening stock', 1),
(3, 'opening_stock', 200.000, 200.000, 800.00, 'OPENING', 'Opening stock', 1),
(4, 'opening_stock', 500.000, 500.000, 50.00, 'OPENING', 'Opening stock', 1),
(5, 'opening_stock', 100.000, 100.000, 200.00, 'OPENING', 'Opening stock', 1),
(6, 'opening_stock', 80.000, 80.000, 120.00, 'OPENING', 'Opening stock', 1),
(7, 'opening_stock', 10.000, 10.000, 8000.00, 'OPENING', 'Opening stock', 1),
(8, 'opening_stock', 15.000, 15.000, 2500.00, 'OPENING', 'Opening stock', 1),
(9, 'opening_stock', 300.000, 300.000, 30.00, 'OPENING', 'Opening stock', 1),
(10, 'opening_stock', 150.000, 150.000, 600.00, 'OPENING', 'Opening stock', 1);
