-- ============================================================
-- MINI ERP - Complete MySQL Database Schema
-- Shiv Furniture ERP System
-- ============================================================

CREATE DATABASE IF NOT EXISTS mini_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mini_erp;

-- ============================================================
-- AUTHENTICATION & USER MANAGEMENT
-- ============================================================

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    module VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    UNIQUE KEY uq_module_action (module, action)
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    password_reset_token VARCHAR(255) NULL,
    password_reset_expires TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username)
);

CREATE TABLE user_roles (
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

CREATE TABLE role_permissions (
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

-- ============================================================
-- PRODUCT MANAGEMENT
-- ============================================================

CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_code VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id INT,
    cost_price DECIMAL(15,2) DEFAULT 0.00,
    sales_price DECIMAL(15,2) DEFAULT 0.00,
    on_hand_qty DECIMAL(15,3) DEFAULT 0.000,
    reserved_qty DECIMAL(15,3) DEFAULT 0.000,
    reorder_point DECIMAL(15,3) DEFAULT 0.000,
    unit_of_measure VARCHAR(20) DEFAULT 'PCS',
    procurement_strategy ENUM('MTS','MTO') DEFAULT 'MTS',
    procurement_type ENUM('purchase','manufacturing') DEFAULT 'purchase',
    image_path VARCHAR(500) NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_product_code (product_code),
    INDEX idx_product_name (product_name),
    INDEX idx_category (category_id)
);

-- ============================================================
-- CUSTOMER & VENDOR MANAGEMENT
-- ============================================================

CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_code VARCHAR(50) NOT NULL UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(30),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'India',
    gst_number VARCHAR(20),
    credit_limit DECIMAL(15,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_customer_code (customer_code),
    INDEX idx_company_name (company_name)
);

CREATE TABLE vendors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_code VARCHAR(50) NOT NULL UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(30),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'India',
    gst_number VARCHAR(20),
    payment_terms VARCHAR(100),
    lead_time_days INT DEFAULT 7,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_vendor_code (vendor_code),
    INDEX idx_company_name (company_name)
);

-- ============================================================
-- SALES MODULE
-- ============================================================

CREATE TABLE sales_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    expected_delivery_date DATE,
    status ENUM('draft','confirmed','partially_delivered','fully_delivered','cancelled') DEFAULT 'draft',
    subtotal DECIMAL(15,2) DEFAULT 0.00,
    tax_amount DECIMAL(15,2) DEFAULT 0.00,
    discount_amount DECIMAL(15,2) DEFAULT 0.00,
    total_amount DECIMAL(15,2) DEFAULT 0.00,
    notes TEXT,
    created_by INT,
    confirmed_by INT NULL,
    confirmed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (confirmed_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_order_number (order_number),
    INDEX idx_status (status),
    INDEX idx_customer (customer_id),
    INDEX idx_order_date (order_date)
);

CREATE TABLE sales_order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sales_order_id INT NOT NULL,
    product_id INT NOT NULL,
    ordered_qty DECIMAL(15,3) NOT NULL,
    delivered_qty DECIMAL(15,3) DEFAULT 0.000,
    unit_price DECIMAL(15,2) NOT NULL,
    discount_pct DECIMAL(5,2) DEFAULT 0.00,
    tax_pct DECIMAL(5,2) DEFAULT 0.00,
    line_total DECIMAL(15,2) NOT NULL,
    FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_so_id (sales_order_id),
    INDEX idx_product (product_id)
);

CREATE TABLE deliveries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    delivery_number VARCHAR(50) NOT NULL UNIQUE,
    sales_order_id INT NOT NULL,
    delivery_date DATE NOT NULL,
    status ENUM('pending','in_transit','delivered','cancelled') DEFAULT 'pending',
    notes TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id),
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE delivery_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    delivery_id INT NOT NULL,
    sales_order_item_id INT NOT NULL,
    product_id INT NOT NULL,
    delivered_qty DECIMAL(15,3) NOT NULL,
    FOREIGN KEY (delivery_id) REFERENCES deliveries(id) ON DELETE CASCADE,
    FOREIGN KEY (sales_order_item_id) REFERENCES sales_order_items(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- ============================================================
-- PURCHASE MODULE
-- ============================================================

CREATE TABLE purchase_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    vendor_id INT NOT NULL,
    order_date DATE NOT NULL,
    expected_receipt_date DATE,
    status ENUM('draft','confirmed','partially_received','fully_received','cancelled') DEFAULT 'draft',
    subtotal DECIMAL(15,2) DEFAULT 0.00,
    tax_amount DECIMAL(15,2) DEFAULT 0.00,
    total_amount DECIMAL(15,2) DEFAULT 0.00,
    notes TEXT,
    auto_generated BOOLEAN DEFAULT FALSE,
    reference_so_id INT NULL,
    created_by INT,
    confirmed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id),
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (reference_so_id) REFERENCES sales_orders(id) ON DELETE SET NULL,
    INDEX idx_order_number (order_number),
    INDEX idx_status (status),
    INDEX idx_vendor (vendor_id)
);

CREATE TABLE purchase_order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_order_id INT NOT NULL,
    product_id INT NOT NULL,
    ordered_qty DECIMAL(15,3) NOT NULL,
    received_qty DECIMAL(15,3) DEFAULT 0.000,
    unit_price DECIMAL(15,2) NOT NULL,
    tax_pct DECIMAL(5,2) DEFAULT 0.00,
    line_total DECIMAL(15,2) NOT NULL,
    FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_po_id (purchase_order_id),
    INDEX idx_product (product_id)
);

CREATE TABLE goods_receipts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    receipt_number VARCHAR(50) NOT NULL UNIQUE,
    purchase_order_id INT NOT NULL,
    receipt_date DATE NOT NULL,
    notes TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders(id),
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE goods_receipt_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    receipt_id INT NOT NULL,
    purchase_order_item_id INT NOT NULL,
    product_id INT NOT NULL,
    received_qty DECIMAL(15,3) NOT NULL,
    FOREIGN KEY (receipt_id) REFERENCES goods_receipts(id) ON DELETE CASCADE,
    FOREIGN KEY (purchase_order_item_id) REFERENCES purchase_order_items(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- ============================================================
-- BILL OF MATERIALS
-- ============================================================

CREATE TABLE boms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bom_code VARCHAR(50) NOT NULL UNIQUE,
    product_id INT NOT NULL,
    version VARCHAR(20) DEFAULT '1.0',
    quantity DECIMAL(15,3) DEFAULT 1.000,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_product (product_id)
);

CREATE TABLE bom_components (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bom_id INT NOT NULL,
    component_product_id INT NOT NULL,
    quantity DECIMAL(15,3) NOT NULL,
    unit_of_measure VARCHAR(20) DEFAULT 'PCS',
    notes TEXT,
    FOREIGN KEY (bom_id) REFERENCES boms(id) ON DELETE CASCADE,
    FOREIGN KEY (component_product_id) REFERENCES products(id),
    INDEX idx_bom (bom_id)
);

CREATE TABLE work_centers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    capacity_per_hour DECIMAL(10,2) DEFAULT 1.00,
    cost_per_hour DECIMAL(10,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE operations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bom_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    work_center_id INT,
    sequence INT DEFAULT 1,
    duration_hours DECIMAL(8,2) DEFAULT 0.00,
    description TEXT,
    FOREIGN KEY (bom_id) REFERENCES boms(id) ON DELETE CASCADE,
    FOREIGN KEY (work_center_id) REFERENCES work_centers(id) ON DELETE SET NULL,
    INDEX idx_bom (bom_id)
);

-- ============================================================
-- MANUFACTURING MODULE
-- ============================================================

CREATE TABLE manufacturing_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mo_number VARCHAR(50) NOT NULL UNIQUE,
    product_id INT NOT NULL,
    bom_id INT,
    planned_qty DECIMAL(15,3) NOT NULL,
    produced_qty DECIMAL(15,3) DEFAULT 0.000,
    scheduled_start DATE,
    scheduled_end DATE,
    actual_start TIMESTAMP NULL,
    actual_end TIMESTAMP NULL,
    status ENUM('draft','confirmed','in_progress','completed','cancelled') DEFAULT 'draft',
    auto_generated BOOLEAN DEFAULT FALSE,
    reference_so_id INT NULL,
    notes TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (bom_id) REFERENCES boms(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (reference_so_id) REFERENCES sales_orders(id) ON DELETE SET NULL,
    INDEX idx_mo_number (mo_number),
    INDEX idx_status (status),
    INDEX idx_product (product_id)
);

CREATE TABLE work_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    wo_number VARCHAR(50) NOT NULL UNIQUE,
    manufacturing_order_id INT NOT NULL,
    operation_id INT,
    work_center_id INT,
    planned_duration_hours DECIMAL(8,2) DEFAULT 0.00,
    actual_duration_hours DECIMAL(8,2) DEFAULT 0.00,
    status ENUM('pending','in_progress','completed','cancelled') DEFAULT 'pending',
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (manufacturing_order_id) REFERENCES manufacturing_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (operation_id) REFERENCES operations(id) ON DELETE SET NULL,
    FOREIGN KEY (work_center_id) REFERENCES work_centers(id) ON DELETE SET NULL,
    INDEX idx_mo (manufacturing_order_id)
);

CREATE TABLE mo_components (
    id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturing_order_id INT NOT NULL,
    product_id INT NOT NULL,
    required_qty DECIMAL(15,3) NOT NULL,
    consumed_qty DECIMAL(15,3) DEFAULT 0.000,
    FOREIGN KEY (manufacturing_order_id) REFERENCES manufacturing_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_mo (manufacturing_order_id)
);

-- ============================================================
-- INVENTORY & STOCK LEDGER
-- ============================================================

CREATE TABLE stock_ledger (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    movement_type ENUM(
        'purchase_receipt',
        'sales_delivery',
        'manufacturing_consumption',
        'manufacturing_production',
        'manual_adjustment',
        'opening_stock',
        'return_from_customer',
        'return_to_vendor'
    ) NOT NULL,
    quantity DECIMAL(15,3) NOT NULL,
    balance_qty DECIMAL(15,3) NOT NULL,
    unit_cost DECIMAL(15,4) DEFAULT 0.0000,
    reference_type VARCHAR(50),
    reference_id INT,
    reference_number VARCHAR(100),
    notes TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_product (product_id),
    INDEX idx_movement_date (movement_date),
    INDEX idx_movement_type (movement_type),
    INDEX idx_reference (reference_type, reference_id)
);

CREATE TABLE stock_reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    reserved_qty DECIMAL(15,3) NOT NULL,
    reservation_type ENUM('sales_order','manufacturing_order') NOT NULL,
    reference_id INT NOT NULL,
    reference_number VARCHAR(100),
    is_released BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    released_at TIMESTAMP NULL,
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_product (product_id),
    INDEX idx_reference (reservation_type, reference_id)
);

-- ============================================================
-- NOTIFICATIONS
-- ============================================================

CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('info','warning','error','success') DEFAULT 'info',
    category ENUM('low_stock','procurement','manufacturing','sales','purchase','system') DEFAULT 'system',
    reference_type VARCHAR(50) NULL,
    reference_id INT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
);

-- ============================================================
-- AUDIT LOGS
-- ============================================================

CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    username VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    module VARCHAR(50) NOT NULL,
    record_type VARCHAR(50),
    record_id INT NULL,
    old_value JSON NULL,
    new_value JSON NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_action (action),
    INDEX idx_module (module),
    INDEX idx_created_at (created_at)
);

-- ============================================================
-- SEQUENCE COUNTERS (for auto-numbering)
-- ============================================================

CREATE TABLE sequence_counters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prefix VARCHAR(20) NOT NULL UNIQUE,
    last_number INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
