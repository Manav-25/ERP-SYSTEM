# 🏭 MINI ERP — Shiv Furniture Management System

A production-ready, enterprise-grade Mini ERP system for **Shiv Furniture**, covering the complete **Demand-to-Delivery** business workflow.

---

## 📐 Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                     MINI ERP System                           │
├─────────────────────────┬─────────────────────────────────────┤
│   Frontend (Node.js)    │     Backend (Python FastAPI)        │
│   Port: 3000            │     Port: 8000                      │
│   Express + EJS         │     REST API + JWT                  │
│   Bootstrap 5           │     SQLAlchemy ORM                  │
├─────────────────────────┴─────────────────────────────────────┤
│                    MySQL Database                              │
│                    Port: 3306                                  │
└───────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Project Structure

```
ERP mini/
├── backend/                    # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── config.py           # Settings / .env config
│   │   ├── database.py         # SQLAlchemy DB setup
│   │   ├── models/             # DB models (ORM)
│   │   │   ├── user.py         # Users, Roles, Permissions
│   │   │   ├── product.py      # Products, Categories
│   │   │   ├── customer.py     # Customers
│   │   │   ├── vendor.py       # Vendors
│   │   │   ├── sales.py        # Sales Orders, Deliveries
│   │   │   ├── purchase.py     # Purchase Orders, GR
│   │   │   ├── bom.py          # BOM, Work Centers, Operations
│   │   │   ├── manufacturing.py# MOs, Work Orders, Components
│   │   │   ├── inventory.py    # Stock Ledger, Reservations
│   │   │   └── audit.py        # Audit Logs, Notifications
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── routers/            # API route handlers
│   │   │   ├── auth.py         # Login, JWT, Password
│   │   │   ├── users.py        # User CRUD
│   │   │   ├── products.py     # Product CRUD
│   │   │   ├── inventory.py    # Stock Ledger, Summary
│   │   │   ├── sales.py        # SO, Customers, Deliveries
│   │   │   ├── purchase.py     # PO, Vendors, Receipts
│   │   │   ├── manufacturing.py# MO, BOM, Work Orders
│   │   │   ├── dashboard.py    # KPIs, Charts, Activity
│   │   │   ├── reports.py      # Reports + Excel Export
│   │   │   └── audit.py        # Audit Log viewer
│   │   ├── services/
│   │   │   ├── inventory_service.py    # Stock movement logic
│   │   │   └── procurement_service.py  # Auto PO/MO creation
│   │   ├── middleware/
│   │   │   └── auth_middleware.py      # JWT + RBAC guards
│   │   └── utils/
│   │       ├── security.py     # Hashing, JWT tokens
│   │       └── helpers.py      # Sequencer, pagination
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                   # Node.js Express Frontend
│   ├── src/
│   │   ├── app.js              # Express app entry point
│   │   ├── routes/             # Page routes
│   │   │   ├── auth.js         # Login, Logout, Forgot Password
│   │   │   ├── dashboard.js    # Dashboard page
│   │   │   ├── products.js     # Product CRUD pages
│   │   │   ├── inventory.js    # Inventory & Ledger pages
│   │   │   ├── sales.js        # SO, Customers, Deliveries
│   │   │   ├── purchase.js     # PO, Vendors, Receipts
│   │   │   ├── manufacturing.js# MO, BOM pages
│   │   │   ├── users.js        # User management
│   │   │   ├── reports.js      # Report pages + Excel export
│   │   │   └── api-proxy.js    # JSON API proxy for frontend JS
│   │   ├── middleware/
│   │   │   └── auth.js         # Session authentication
│   │   ├── config/config.js
│   │   └── utils/api.js        # Axios API helper
│   ├── views/                  # EJS Templates
│   │   ├── auth/               # Login, Forgot Password
│   │   ├── dashboard/          # Main dashboard
│   │   ├── products/           # Product pages
│   │   ├── inventory/          # Inventory pages
│   │   ├── sales/              # Sales pages
│   │   ├── purchase/           # Purchase pages
│   │   ├── manufacturing/      # MFG pages + BOM
│   │   ├── users/              # User management
│   │   ├── reports/            # All report views
│   │   └── partials/           # Sidebar, Navbar, Pagination
│   ├── public/
│   │   ├── css/style.css       # Custom ERP CSS (Dark Mode, KPIs)
│   │   └── js/main.js          # Frontend JavaScript
│   └── package.json
│
└── database/
    ├── schema.sql              # Complete MySQL schema
    └── seed.sql                # Sample data
```

---

## 🚀 Setup & Installation

### Prerequisites
- **MySQL 8.0+**
- **Python 3.11+**
- **Node.js 18+**

---

### Step 1: MySQL Database Setup

```sql
-- In MySQL shell or MySQL Workbench:
source /path/to/ERP mini/database/schema.sql
source /path/to/ERP mini/database/seed.sql
```

Or using command line:
```bash
mysql -u root -p < "database/schema.sql"
mysql -u root -p < "database/seed.sql"
```

---

### Step 2: Backend (Python FastAPI)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your MySQL credentials

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will run at:** `http://localhost:8000`
**API Docs (Swagger):** `http://localhost:8000/api/docs`

---

### Step 3: Frontend (Node.js)

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
copy .env.example .env
# Edit .env (set API_BASE_URL=http://localhost:8000/api/v1)

# Start frontend (development)
npm run dev

# Start frontend (production)
npm start
```

**Frontend will run at:** `http://localhost:3000`

---

## 🔑 Default Login Credentials

| Username | Password | Role |
|----------|----------|------|
| `admin` | `Admin@123` | Administrator |
| `sales1` | `Admin@123` | Sales User |
| `purchase1` | `Admin@123` | Purchase User |
| `mfg1` | `Admin@123` | Manufacturing User |
| `inv1` | `Admin@123` | Inventory Manager |
| `owner` | `Admin@123` | Business Owner |

---

## ✅ Modules & Features

### 🔐 Authentication
- JWT-based login/logout
- BCrypt password hashing
- Role-Based Access Control (RBAC)
- Forgot & reset password
- Session management

### 📦 Product Management
- Product CRUD with categories
- Procurement strategy: **MTS** / **MTO**
- Procurement type: **Purchase** / **Manufacturing**
- Free Qty = On Hand − Reserved
- Low stock alerts & reorder points
- Image upload support

### 🏭 Inventory Management
- Real-time stock levels
- Stock Ledger (every movement tracked)
- Stock Reservations
- Inventory Valuation
- Movement types: Purchase Receipt, Sales Delivery, MFG Consumption/Production, Manual Adjustment

### 🛒 Sales Module
- **Workflow:** Draft → Confirmed → Partially Delivered → Fully Delivered
- Customer management (with GST)
- Stock availability check on confirm
- Auto stock reservation on confirm
- Auto procurement trigger on shortage
- Delivery processing with partial delivery support

### 🚚 Purchase Module
- **Workflow:** Draft → Confirmed → Partially Received → Fully Received
- Vendor management
- Goods Receipt processing
- Auto-generated POs from procurement engine
- Stock update on receipt

### 🏗️ Manufacturing Module
- **Workflow:** Draft → Confirmed → In Progress → Completed
- Auto-load Bill of Materials
- Work Order generation from operations
- Component consumption from stock
- Finished goods production to stock
- Auto-generated MOs from procurement engine

### 📋 Bill of Materials (BoM)
- Multi-level component definitions
- Operations with Work Centers & durations
- Version control

### ⚙️ Procurement Automation
- Triggered automatically on SO confirmation
- Checks Free Qty vs Required Qty
- Creates PO if `procurement_type = purchase`
- Creates MO if `procurement_type = manufacturing`
- Notifications sent on trigger

### 📊 Dashboard
- KPI cards: Products, Sales, Purchase, Manufacturing, Inventory Value, Delayed Orders
- Sales trend chart (line chart)
- Inventory by category (donut chart)
- Recent activity feed
- Alert notifications

### 📈 Reports
- Sales Report (with Excel export)
- Purchase Report
- Inventory Report (stock levels + valuation)
- Manufacturing Report
- Profit Report (Revenue, Cost, Gross Margin)

### 👥 User Management (Admin only)
- Create/edit/deactivate users
- Assign multiple roles
- View last login

### 🔍 Audit Logs (Admin only)
- All changes tracked
- Login activity
- Module-level filtering

---

## 🎨 UI Features

- ✅ Responsive layout (desktop + mobile)
- ✅ Collapsible sidebar
- ✅ Dark Mode toggle (persisted in localStorage)
- ✅ Status tabs for filtering orders
- ✅ Live notification panel with badge
- ✅ Inline forms / modals for quick create
- ✅ Data tables with pagination
- ✅ KPI cards with gradient styling
- ✅ Dynamic order item rows (add/remove)
- ✅ Auto-calculated line totals
- ✅ Progress bars for manufacturing
- ✅ Demo credentials on login page

---

## 🔌 API Reference

Full Swagger documentation available at:
```
http://localhost:8000/api/docs
```

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User login |
| GET | `/api/v1/dashboard/stats` | Dashboard KPIs |
| GET/POST | `/api/v1/products` | Product list/create |
| GET/POST | `/api/v1/sales/orders` | Sales order list/create |
| POST | `/api/v1/sales/orders/{id}/confirm` | Confirm SO + trigger procurement |
| POST | `/api/v1/sales/deliveries` | Process delivery |
| GET/POST | `/api/v1/purchase/orders` | PO list/create |
| POST | `/api/v1/purchase/receipts` | Goods receipt |
| GET/POST | `/api/v1/manufacturing/orders` | MO list/create |
| POST | `/api/v1/manufacturing/orders/{id}/start` | Start production |
| POST | `/api/v1/manufacturing/orders/{id}/complete` | Complete + add to stock |
| GET/POST | `/api/v1/manufacturing/boms` | BOM list/create |
| GET | `/api/v1/inventory/ledger` | Stock ledger |
| GET | `/api/v1/reports/sales` | Sales report JSON |
| GET | `/api/v1/reports/export/sales/excel` | Excel export |

---

## 🔧 Environment Configuration

### Backend `.env`
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/mini_erp
SECRET_KEY=your-super-secret-jwt-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS=http://localhost:3000
UPLOAD_DIR=uploads
```

### Frontend `.env`
```env
PORT=3000
API_BASE_URL=http://localhost:8000/api/v1
SESSION_SECRET=your-session-secret
NODE_ENV=development
```

---

## 🏗️ Production Deployment

### Docker Compose (recommended)

```yaml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: mini_erp
    volumes:
      - ./database/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
      - ./database/seed.sql:/docker-entrypoint-initdb.d/02-seed.sql
    ports: ["3306:3306"]

  backend:
    build: ./backend
    environment:
      DATABASE_URL: mysql+pymysql://root:password@mysql:3306/mini_erp
      SECRET_KEY: change-this-in-production
    ports: ["8000:8000"]
    depends_on: [mysql]

  frontend:
    build: ./frontend
    environment:
      API_BASE_URL: http://backend:8000/api/v1
      SESSION_SECRET: change-this-in-production
    ports: ["3000:3000"]
    depends_on: [backend]
```

---

## 🛡️ Security Features

- BCrypt password hashing (salt rounds: 12)
- JWT access tokens (configurable expiry)
- Refresh token rotation
- Role-Based Access Control (RBAC) on every API endpoint
- Admin role bypasses permission checks
- CORS configured for frontend origin only
- Input validation via Pydantic schemas
- SQL injection prevention via SQLAlchemy ORM

---

## 📝 Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend Server | Node.js 18 + Express 4 |
| Template Engine | EJS 3 |
| CSS Framework | Bootstrap 5.3 |
| Charts | Chart.js 4 |
| Icons | Font Awesome 6 |
| Backend API | Python FastAPI |
| ORM | SQLAlchemy 2 |
| Auth | python-jose + passlib |
| Database | MySQL 8 |
| Validation | Pydantic v2 |
| Reports | openpyxl (Excel) |

---

*Built for Shiv Furniture — Complete Demand-to-Delivery ERP*
