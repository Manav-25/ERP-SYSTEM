/* =====================================================================
   MINI ERP — Core App (API + Auth + Components)
   Pure HTML/CSS/JS — No Node.js required
   ===================================================================== */

// Auto-detect API base: if running from the FastAPI server, use same origin; else fallback to localhost:8000
const API_BASE = (location.hostname === 'localhost' || location.hostname === '127.0.0.1')
  ? `${location.protocol}//${location.hostname}:8000/api/v1`
  : '/api/v1';

/* ── RBAC Configuration ───────────────────────────────────────────── */
const RBAC = {
  // Pages each role can VIEW
  pages: {
    'admin':               ['dashboard','sales-orders','customers','purchase-orders','vendors',
                            'products','inventory','stock-ledger','mfg-orders','boms',
                            'reports','users','deliveries'],
    'business_owner':      ['dashboard','sales-orders','customers','purchase-orders','vendors',
                            'products','inventory','stock-ledger','mfg-orders','boms','reports'],
    'sales_user':          ['dashboard','sales-orders','customers','deliveries','reports'],
    'purchase_user':       ['dashboard','purchase-orders','vendors','products','reports'],
    'manufacturing_user':  ['dashboard','mfg-orders','boms','products','inventory','reports'],
    'inventory_manager':   ['dashboard','inventory','stock-ledger','products','reports'],
  },
  // Modules each role can CREATE/EDIT/DELETE in
  write: {
    'admin':               ['all'],
    'business_owner':      [],  // read-only
    'sales_user':          ['sales-orders','customers','deliveries'],
    'purchase_user':       ['purchase-orders','vendors'],
    'manufacturing_user':  ['mfg-orders','boms'],
    'inventory_manager':   ['inventory','stock-ledger','products'],
  },
  // Sidebar nav groups per role
  nav: {
    'admin': [
      { label:'Main',        items:['dashboard'] },
      { label:'Sales',       items:['sales-orders','customers','deliveries'] },
      { label:'Purchasing',  items:['purchase-orders','vendors'] },
      { label:'Operations',  items:['products','inventory','stock-ledger'] },
      { label:'Manufacturing',items:['mfg-orders','boms'] },
      { label:'Analytics',   items:['reports'] },
      { label:'Admin',       items:['users'] },
    ],
    'business_owner': [
      { label:'Main',        items:['dashboard'] },
      { label:'Sales',       items:['sales-orders','customers'] },
      { label:'Purchasing',  items:['purchase-orders','vendors'] },
      { label:'Operations',  items:['products','inventory','stock-ledger'] },
      { label:'Manufacturing',items:['mfg-orders','boms'] },
      { label:'Analytics',   items:['reports'] },
    ],
    'sales_user': [
      { label:'Main',        items:['dashboard'] },
      { label:'Sales',       items:['sales-orders','customers','deliveries'] },
      { label:'Analytics',   items:['reports'] },
    ],
    'purchase_user': [
      { label:'Main',        items:['dashboard'] },
      { label:'Purchasing',  items:['purchase-orders','vendors'] },
      { label:'Catalog',     items:['products'] },
      { label:'Analytics',   items:['reports'] },
    ],
    'manufacturing_user': [
      { label:'Main',        items:['dashboard'] },
      { label:'Manufacturing',items:['mfg-orders','boms'] },
      { label:'Catalog',     items:['products','inventory'] },
      { label:'Analytics',   items:['reports'] },
    ],
    'inventory_manager': [
      { label:'Main',        items:['dashboard'] },
      { label:'Inventory',   items:['inventory','stock-ledger','products'] },
      { label:'Analytics',   items:['reports'] },
    ],
  },
  // Page meta: href, icon, label
  meta: {
    'dashboard':       { href:'/static/dashboard.html',              icon:'fa-chart-pie',          label:'Dashboard' },
    'sales-orders':    { href:'/static/pages/sales-orders.html',     icon:'fa-file-invoice-dollar', label:'Sales Orders' },
    'customers':       { href:'/static/pages/customers.html',        icon:'fa-users',              label:'Customers' },
    'deliveries':      { href:'/static/pages/deliveries.html',       icon:'fa-truck-fast',         label:'Deliveries' },
    'purchase-orders': { href:'/static/pages/purchase-orders.html',  icon:'fa-truck',              label:'Purchase Orders' },
    'vendors':         { href:'/static/pages/vendors.html',          icon:'fa-building',           label:'Vendors' },
    'products':        { href:'/static/pages/products.html',         icon:'fa-box',                label:'Products' },
    'inventory':       { href:'/static/pages/inventory.html',        icon:'fa-warehouse',          label:'Inventory' },
    'stock-ledger':    { href:'/static/pages/stock-ledger.html',     icon:'fa-clipboard-list',     label:'Stock Ledger' },
    'mfg-orders':      { href:'/static/pages/mfg-orders.html',       icon:'fa-cogs',               label:'MFG Orders' },
    'boms':            { href:'/static/pages/boms.html',             icon:'fa-sitemap',            label:'Bill of Materials' },
    'reports':         { href:'/static/pages/reports.html',          icon:'fa-chart-bar',          label:'Reports' },
    'users':           { href:'/static/pages/users.html',            icon:'fa-users-cog',          label:'Users' },
  }
};

/* ── Auth ─────────────────────────────────────────────────────────── */
const Auth = {
  getToken: () => localStorage.getItem('erp_token'),
  getUser:  () => { try { return JSON.parse(localStorage.getItem('erp_user')||'null'); } catch{return null;} },
  getRoles: () => { try { return JSON.parse(localStorage.getItem('erp_roles')||'[]'); } catch{return[];} },
  isLoggedIn: () => !!localStorage.getItem('erp_token'),
  save(data) {
    localStorage.setItem('erp_token', data.access_token);
    localStorage.setItem('erp_refresh', data.refresh_token || '');
    localStorage.setItem('erp_user', JSON.stringify(data.user));
    localStorage.setItem('erp_roles', JSON.stringify((data.user?.roles||[]).map(r=>r.name)));
  },
  clear() {
    ['erp_token','erp_refresh','erp_user','erp_roles'].forEach(k=>localStorage.removeItem(k));
  },
  requireAuth() {
    if (!this.isLoggedIn()) { window.location.href = '/static/login.html'; return false; }
    return true;
  },
  redirectIfAuth() {
    if (this.isLoggedIn()) { window.location.href = '/static/dashboard.html'; }
  },
  hasRole(role)  { return this.getRoles().includes(role); },
  isAdmin()      { return this.getRoles().includes('admin'); },
  /** Returns true if user can VIEW this page */
  canAccess(page) {
    if (this.isAdmin()) return true;
    const roles = this.getRoles();
    return roles.some(r => (RBAC.pages[r]||[]).includes(page));
  },
  /** Returns true if user can CREATE/EDIT/DELETE in this module */
  canWrite(module) {
    if (this.isAdmin()) return true;
    const roles = this.getRoles();
    return roles.some(r => {
      const w = RBAC.write[r]||[];
      return w.includes('all') || w.includes(module);
    });
  },
  /** Get primary role for display */
  primaryRole() {
    const roles = this.getRoles();
    const order = ['admin','business_owner','sales_user','purchase_user','manufacturing_user','inventory_manager'];
    for (const r of order) if (roles.includes(r)) return r;
    return roles[0] || 'user';
  },
  /** Get nav groups for current user */
  getNavGroups() {
    const role = this.primaryRole();
    return RBAC.nav[role] || RBAC.nav['sales_user'];
  },
  logout() { this.clear(); window.location.href = '/static/login.html'; }
};

/* ── API Client ───────────────────────────────────────────────────── */
const API = {
  async request(method, path, body=null, params=null) {
    const url = new URL(API_BASE + path);
    if (params) Object.entries(params).forEach(([k,v])=>{ if(v!==null&&v!==undefined&&v!=='') url.searchParams.set(k,v); });
    const headers = { 'Content-Type': 'application/json' };
    if (Auth.getToken()) headers['Authorization'] = `Bearer ${Auth.getToken()}`;
    const opts = { method, headers };
    if (body && method !== 'GET') opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    if (res.status === 401) { Auth.clear(); window.location.href = '/static/login.html'; return null; }
    const data = await res.json().catch(()=>null);
    if (!res.ok) throw new Error(data?.detail || `HTTP ${res.status}`);
    return data;
  },
  get:    (path, params)      => API.request('GET', path, null, params),
  post:   (path, body)        => API.request('POST', path, body),
  put:    (path, body)        => API.request('PUT', path, body),
  patch:  (path, body)        => API.request('PATCH', path, body),
  delete: (path)              => API.request('DELETE', path),
};

/* ── Toast Notifications ──────────────────────────────────────────── */
const Toast = {
  container: null,
  init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.style.cssText = 'position:fixed;top:1rem;right:1rem;z-index:99999;display:flex;flex-direction:column;gap:.5rem;';
      document.body.appendChild(this.container);
    }
  },
  show(msg, type='info', duration=4000) {
    this.init();
    const colors = { success:'#10b981', danger:'#ef4444', warning:'#f59e0b', info:'#6366f1' };
    const icons  = { success:'fa-check-circle', danger:'fa-exclamation-circle', warning:'fa-exclamation-triangle', info:'fa-info-circle' };
    const t = document.createElement('div');
    t.style.cssText = `background:#fff;border:1px solid #e2e8f0;border-left:4px solid ${colors[type]};border-radius:.75rem;padding:.875rem 1rem;display:flex;align-items:center;gap:.625rem;box-shadow:0 10px 25px rgba(0,0,0,.12);min-width:280px;max-width:380px;animation:slideInRight .3s ease;font-family:Inter,sans-serif;font-size:.875rem;font-weight:500;color:#0f172a;`;
    t.innerHTML = `<i class="fas ${icons[type]}" style="color:${colors[type]};font-size:1rem;flex-shrink:0"></i><span style="flex:1">${msg}</span><button onclick="this.parentElement.remove()" style="background:none;border:none;cursor:pointer;color:#94a3b8;font-size:1.1rem;line-height:1;padding:0 0 0 .5rem;">×</button>`;
    this.container.appendChild(t);
    setTimeout(()=>{ t.style.animation='slideOutRight .3s ease'; setTimeout(()=>t.remove(),300); }, duration);
  },
  success: (m) => Toast.show(m,'success'),
  error:   (m) => Toast.show(m,'danger'),
  warning: (m) => Toast.show(m,'warning'),
  info:    (m) => Toast.show(m,'info'),
};

/* ── Loading ──────────────────────────────────────────────────────── */
const Loader = {
  show(id='pageLoader') { const el=document.getElementById(id); if(el) el.style.display='flex'; },
  hide(id='pageLoader') { const el=document.getElementById(id); if(el) el.style.display='none'; },
  btn(btn, loading=true) {
    if (loading) {
      btn._html = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    } else {
      btn.disabled = false;
      btn.innerHTML = btn._html || btn.innerHTML;
    }
  }
};

/* ── UI Components ────────────────────────────────────────────────── */
const UI = {
  /* Sidebar */
  renderSidebar(activePage='') {
    const user    = Auth.getUser();
    const initial = user?.full_name?.charAt(0)?.toUpperCase() || 'U';
    const role    = Auth.primaryRole();
    const groups  = Auth.getNavGroups();

    // Role badge style map
    const roleBadge = {
      admin:               { bg:'#6366f1', label:'Admin' },
      business_owner:      { bg:'#f59e0b', label:'Owner' },
      sales_user:          { bg:'#10b981', label:'Sales' },
      purchase_user:       { bg:'#3b82f6', label:'Purchase' },
      manufacturing_user:  { bg:'#8b5cf6', label:'Manufacturing' },
      inventory_manager:   { bg:'#06b6d4', label:'Inventory' },
    };
    const badge = roleBadge[role] || { bg:'#94a3b8', label: role };

    const navItem = (page, active) => {
      const m = RBAC.meta[page];
      if (!m) return '';
      return `
        <div class="nav-item">
          <a href="${m.href}" class="nav-link ${active===page?'active':''}">
            <i class="nav-icon fas ${m.icon}"></i><span>${m.label}</span>
          </a>
        </div>`;
    };

    const navGroups = groups.map(g => `
      <div class="nav-section-label">${g.label}</div>
      ${g.items.map(p => navItem(p, activePage)).join('')}
    `).join('');

    const html = `
      <aside class="sidebar" id="sidebar">
        <div class="sidebar-brand">
          <div class="brand-icon"><i class="fas fa-industry"></i></div>
          <div class="brand-text">
            <div class="brand-title">MINI ERP</div>
            <div class="brand-subtitle">Shiv Furniture</div>
          </div>
        </div>
        <nav class="sidebar-nav">${navGroups}</nav>
        <div class="sidebar-footer">
          <div class="user-card" onclick="document.getElementById('changePwdModal').classList.add('show')" style="cursor:pointer">
            <div class="user-avatar">${initial}</div>
            <div style="flex:1;min-width:0">
              <div class="user-name">${user?.full_name||user?.username||'User'}</div>
              <div style="margin-top:.2rem">
                <span style="font-size:.62rem;font-weight:700;padding:.15rem .45rem;border-radius:4px;background:${badge.bg};color:#fff;letter-spacing:.02em">${badge.label}</span>
              </div>
            </div>
          </div>
          <button onclick="Auth.logout()"
            style="display:flex;align-items:center;justify-content:center;gap:.5rem;width:100%;
                   margin-top:.45rem;padding:.45rem;border-radius:9px;border:1px solid rgba(255,255,255,.07);
                   background:transparent;color:rgba(255,255,255,.3);font-size:.75rem;font-weight:500;
                   cursor:pointer;font-family:inherit;transition:all .15s;"
            onmouseenter="this.style.background='rgba(239,68,68,.12)';this.style.color='#f87171';this.style.borderColor='rgba(239,68,68,.2)'"
            onmouseleave="this.style.background='transparent';this.style.color='rgba(255,255,255,.3)';this.style.borderColor='rgba(255,255,255,.07)'">
            <i class="fas fa-arrow-right-from-bracket" style="font-size:.7rem;"></i> Sign Out
          </button>
        </div>
      </aside>
      <div id="sidebarOverlay" onclick="closeSidebar()" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:999;backdrop-filter:blur(2px);"></div>`;
    const el = document.getElementById('sidebar-container');
    if (el) el.innerHTML = html;
  },

  /* Topbar */
  renderTopbar(title='Dashboard') {
    const user = Auth.getUser();
    const initial = user?.full_name?.charAt(0)?.toUpperCase() || 'A';
    const html = `
      <header class="topbar" id="topbar">
        <button class="topbar-toggle" onclick="toggleSidebar()" style="display:flex;"><i class="fas fa-bars"></i></button>
        <div style="flex:1"><div class="page-title">${title}</div></div>
        <div class="topbar-actions">
          <button class="topbar-btn" onclick="toggleGlobalSearch()" title="Search (Ctrl+K)"><i class="fas fa-search"></i></button>
          <button class="topbar-btn" onclick="toggleDarkMode()" id="darkModeBtn" title="Toggle Dark Mode"><i class="fas fa-moon"></i></button>
          <div style="position:relative;">
            <button class="topbar-btn" onclick="UI.toggleNotifications()" id="notifBtn">
              <i class="fas fa-bell"></i>
              <span class="notif-dot" id="notifDot" style="display:none"></span>
            </button>
            <div class="notif-dropdown" id="notifDropdown">
              <div class="notif-header"><i class="fas fa-bell" style="color:var(--primary);margin-right:.5rem"></i>Notifications</div>
              <div class="notif-list" id="notifList"><div style="padding:2rem;text-align:center;color:var(--text-muted);font-size:.825rem;"><i class="fas fa-spinner fa-spin" style="display:block;margin-bottom:.5rem"></i>Loading...</div></div>
            </div>
          </div>
          <div style="position:relative;">
            <button class="topbar-btn" onclick="UI.toggleUserMenu()" id="userMenuBtn" style="width:auto;padding:0 .75rem;gap:.5rem;font-weight:600;color:var(--text-primary);">
              <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,var(--primary),var(--secondary));display:flex;align-items:center;justify-content:center;color:#fff;font-size:.75rem;font-weight:700;">${initial}</div>
              <span style="font-size:.825rem;">${user?.full_name||user?.username||'User'}</span>
              <i class="fas fa-chevron-down" style="font-size:.7rem;opacity:.5"></i>
            </button>
            <div id="userMenuDrop" style="display:none;position:absolute;top:calc(100% + .5rem);right:0;background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-lg);box-shadow:var(--shadow-xl);width:200px;z-index:9999;">
              <div style="padding:.875rem 1rem;border-bottom:1px solid var(--border);">
                <div style="font-size:.825rem;font-weight:600;color:var(--text-primary);">${user?.full_name||'User'}</div>
                <div style="font-size:.75rem;color:var(--text-muted);">${user?.email||''}</div>
              </div>
              <div style="padding:.5rem;">
                <button onclick="document.getElementById('changePwdModal').classList.add('show');document.getElementById('userMenuDrop').style.display='none'" style="display:flex;align-items:center;gap:.6rem;width:100%;padding:.55rem .75rem;border:none;background:none;border-radius:var(--radius);color:var(--text-secondary);font-size:.825rem;cursor:pointer;font-family:inherit;">
                  <i class="fas fa-key"></i> Change Password
                </button>
                <button onclick="Auth.logout()" style="display:flex;align-items:center;gap:.6rem;width:100%;padding:.55rem .75rem;border:none;background:none;border-radius:var(--radius);color:var(--danger);font-size:.825rem;cursor:pointer;font-family:inherit;font-weight:600;">
                  <i class="fas fa-sign-out-alt"></i> Sign Out
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>`;
    const el = document.getElementById('topbar-container');
    if (el) el.innerHTML = html;
  },

  /* Change Password Modal */
  renderChangePwdModal() {
    const html = `
      <div class="modal" id="changePwdModal">
        <div class="modal-backdrop" onclick="this.parentElement.classList.remove('show')"></div>
        <div class="modal-dialog">
          <div class="modal-header">
            <div class="modal-title"><i class="fas fa-key" style="color:var(--primary);margin-right:.5rem"></i>Change Password</div>
            <button class="modal-close" onclick="document.getElementById('changePwdModal').classList.remove('show')">×</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Current Password</label>
              <input type="password" id="cpCurrent" class="form-control" placeholder="Current password">
            </div>
            <div class="form-group">
              <label class="form-label">New Password</label>
              <input type="password" id="cpNew" class="form-control" placeholder="Min. 8 characters">
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline" onclick="document.getElementById('changePwdModal').classList.remove('show')">Cancel</button>
            <button class="btn btn-primary" onclick="UI.changePassword()"><i class="fas fa-save"></i> Update</button>
          </div>
        </div>
      </div>`;
    const el = document.getElementById('modal-container');
    if (el) el.innerHTML = html;
  },

  async changePassword() {
    const current = document.getElementById('cpCurrent').value;
    const newPwd  = document.getElementById('cpNew').value;
    if (!current || !newPwd) return Toast.error('Fill all fields');
    if (newPwd.length < 8) return Toast.error('Password must be 8+ characters');
    try {
      await API.post('/auth/change-password', { current_password: current, new_password: newPwd });
      Toast.success('Password updated successfully');
      document.getElementById('changePwdModal').classList.remove('show');
    } catch(e) { Toast.error(e.message); }
  },

  toggleNotifications() {
    const dd = document.getElementById('notifDropdown');
    dd.classList.toggle('show');
    document.addEventListener('click', function close(e) {
      if (!document.getElementById('notifBtn').contains(e.target) && !dd.contains(e.target)) {
        dd.classList.remove('show');
        document.removeEventListener('click', close);
      }
    }, { once: true });
  },

  toggleUserMenu() {
    const m = document.getElementById('userMenuDrop');
    m.style.display = m.style.display === 'none' ? 'block' : 'none';
    if (m.style.display === 'block') {
      document.addEventListener('click', function close(e) {
        if (!document.getElementById('userMenuBtn').contains(e.target) && !m.contains(e.target)) {
          m.style.display = 'none';
          document.removeEventListener('click', close);
        }
      }, { once: true });
    }
  },

  /* Pagination */
  renderPagination(containerId, data, onPageChange) {
    const el = document.getElementById(containerId);
    if (!el || !data) return;
    const { page=1, pages=1, total=0 } = data;
    if (pages <= 1) { el.innerHTML = ''; return; }
    let html = `<div style="display:flex;align-items:center;justify-content:space-between;padding:1rem 1.25rem;border-top:1px solid var(--border);">
      <span style="font-size:.825rem;color:var(--text-muted)">Showing page ${page} of ${pages} (${total} records)</span>
      <div class="pagination">`;
    if (page > 1) html += `<div class="page-item"><a class="page-link" onclick="(${onPageChange})(${page-1})" href="#">‹</a></div>`;
    const start = Math.max(1, page-2), end = Math.min(pages, page+2);
    for (let i=start; i<=end; i++) {
      html += `<div class="page-item ${i===page?'active':''}"><a class="page-link" onclick="(${onPageChange})(${i})" href="#">${i}</a></div>`;
    }
    if (page < pages) html += `<div class="page-item"><a class="page-link" onclick="(${onPageChange})(${page+1})" href="#">›</a></div>`;
    html += `</div></div>`;
    el.innerHTML = html;
  },

  /* Status badge */
  badge(status) {
    const map = {
      draft:'badge-secondary', confirmed:'badge-primary', delivered:'badge-success',
      cancelled:'badge-danger', received:'badge-success', partial:'badge-warning',
      in_progress:'badge-info', done:'badge-success', pending:'badge-warning',
      active:'badge-success', inactive:'badge-secondary',
    };
    return `<span class="badge ${map[status]||'badge-secondary'}">${status}</span>`;
  },

  /* Format currency */
  currency: (n) => '₹' + (parseFloat(n)||0).toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2}),
  number:   (n) => (parseFloat(n)||0).toLocaleString('en-IN'),
  date:     (d) => d ? new Date(d).toLocaleDateString('en-IN',{day:'2-digit',month:'short',year:'numeric'}) : '—',
};

/* ── Init Page ────────────────────────────────────────────────────── */
function initPage(activePage, title) {
  if (!Auth.requireAuth()) return false;

  // Apply saved theme
  const theme = localStorage.getItem('erp-theme') || 'light';
  document.documentElement.setAttribute('data-theme', theme);

  // Role-based access check (skip for dashboard — everyone can see it)
  if (activePage !== 'dashboard' && !Auth.canAccess(activePage)) {
    UI.renderSidebar(activePage);
    UI.renderTopbar('Access Denied');
    UI.renderChangePwdModal();

    // Replace page main content with a denial message
    const main = document.querySelector('main') || document.querySelector('.main-content');
    if (main) {
      const role = Auth.primaryRole().replace(/_/g,' ');
      main.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:center;min-height:60vh;">
          <div style="text-align:center;max-width:420px;padding:2rem;">
            <div style="width:72px;height:72px;border-radius:20px;background:#fee2e2;display:flex;align-items:center;justify-content:center;margin:0 auto 1.25rem;font-size:2rem;color:#ef4444;">
              <i class="fas fa-lock"></i>
            </div>
            <h2 style="font-size:1.4rem;font-weight:800;color:var(--text-primary);margin-bottom:.5rem">Access Denied</h2>
            <p style="color:var(--text-secondary);font-size:.9rem;margin-bottom:1.5rem">
              Your role (<strong>${role}</strong>) does not have permission to view this page.
              Please contact your administrator if you believe this is an error.
            </p>
            <a href="/static/dashboard.html" class="btn btn-primary">
              <i class="fas fa-arrow-left"></i> Back to Dashboard
            </a>
          </div>
        </div>`;
    }

    const l = document.getElementById('pageLoader');
    if (l) { l.style.opacity='0'; setTimeout(()=>l.remove(),300); }
    return false;
  }

  UI.renderSidebar(activePage);
  UI.renderTopbar(title);
  UI.renderChangePwdModal();
  loadNotifications();

  // Business owner = view-only: apply read-only mode globally
  if (Auth.hasRole('business_owner') && !Auth.isAdmin()) {
    document.body.classList.add('read-only-mode');
  }

  // Hide loader
  setTimeout(() => {
    const l = document.getElementById('pageLoader');
    if (l) { l.style.opacity='0'; setTimeout(()=>l.remove(),400); }
  }, 300);

  return true;
}


/* ── RBAC UI Helpers (call after initPage) ────────────────────────── */
/** Hide/disable write-action buttons if user cannot write to this module */
function applyWriteAccess(module) {
  if (Auth.canWrite(module)) return;
  // Disable all create/edit/delete buttons
  document.querySelectorAll('[data-action="create"],[data-action="edit"],[data-action="delete"]').forEach(el => {
    el.style.display = 'none';
  });
  // Also hide elements with class .write-only
  document.querySelectorAll('.write-only').forEach(el => el.style.display='none');
}

/* ── Notifications ────────────────────────────────────────────────── */
async function loadNotifications() {
  try {
    const data = await API.get('/dashboard/notifications', { limit: 8 });
    const list = document.getElementById('notifList');
    const dot = document.getElementById('notifDot');
    if (!list) return;
    const items = data?.notifications || data || [];
    if (!items.length) { list.innerHTML = '<div style="padding:2rem;text-align:center;color:var(--text-muted);font-size:.825rem;"><i class="fas fa-bell-slash" style="display:block;margin-bottom:.5rem;opacity:.3;font-size:1.5rem"></i>No notifications</div>'; return; }
    dot.style.display = 'block';
    const typeIcon = { low_stock:'fa-box-open', system:'fa-cog', alert:'fa-exclamation-triangle', info:'fa-info-circle' };
    const typeColor= { low_stock:'rgba(239,68,68,.1)', system:'rgba(99,102,241,.1)', alert:'rgba(245,158,11,.1)', info:'rgba(59,130,246,.1)' };
    const typeText = { low_stock:'var(--danger)', system:'var(--primary)', alert:'var(--warning)', info:'var(--info)' };
    list.innerHTML = items.map(n=>`
      <div class="notif-item">
        <div class="notif-icon" style="background:${typeColor[n.type]||'rgba(99,102,241,.1)'};color:${typeText[n.type]||'var(--primary)'}"><i class="fas ${typeIcon[n.type]||'fa-bell'}"></i></div>
        <div class="notif-body">
          <div class="notif-title">${n.message||n.title||''}</div>
          <div class="notif-time">${UI.date(n.created_at)}</div>
        </div>
      </div>`).join('');
  } catch(e) {}
}

/* ── Sidebar toggle ───────────────────────────────────────────────── */
function toggleSidebar() {
  const s = document.getElementById('sidebar');
  const o = document.getElementById('sidebarOverlay');
  if (window.innerWidth <= 768) {
    s.classList.toggle('open');
    o.style.display = s.classList.contains('open') ? 'block' : 'none';
  } else { document.body.classList.toggle('sidebar-collapsed'); }
}
function closeSidebar() {
  document.getElementById('sidebar')?.classList.remove('open');
  const o = document.getElementById('sidebarOverlay');
  if (o) o.style.display = 'none';
}

/* ── Dark Mode ────────────────────────────────────────────────────── */
function toggleDarkMode() {
  const html = document.documentElement;
  const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('erp-theme', next);
  const btn = document.getElementById('darkModeBtn');
  if (btn) btn.querySelector('i').className = next==='dark' ? 'fas fa-sun' : 'fas fa-moon';
}

/* ── Animated Counters ────────────────────────────────────────────── */
function animateCounters() {
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = parseFloat(el.dataset.count);
    const prefix = el.dataset.prefix || '';
    const suffix = el.dataset.suffix || '';
    const duration = 1000;
    const start = performance.now();
    function update(now) {
      const p = Math.min((now-start)/duration,1);
      const ease = 1-Math.pow(1-p,3);
      el.textContent = prefix + Math.floor(target*ease).toLocaleString('en-IN') + suffix;
      if (p < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
  });
}

/* ── Global Search ────────────────────────────────────────────────── */
function toggleGlobalSearch() {
  let o = document.getElementById('searchOverlay');
  if (o) { o.remove(); return; }
  o = document.createElement('div');
  o.id = 'searchOverlay';
  o.style.cssText = 'position:fixed;inset:0;background:rgba(15,23,42,.6);z-index:9999;display:flex;align-items:flex-start;justify-content:center;padding-top:8vh;backdrop-filter:blur(6px);animation:gsIn .18s ease;';

  const pages = [
    ['Dashboard',      '/static/dashboard.html',                'fa-chart-pie',          '#6366f1'],
    ['Products',       '/static/pages/products.html',           'fa-box',                '#10b981'],
    ['Sales Orders',   '/static/pages/sales-orders.html',       'fa-file-invoice-dollar','#3b82f6'],
    ['Customers',      '/static/pages/customers.html',          'fa-users',              '#8b5cf6'],
    ['Purchase Orders','/static/pages/purchase-orders.html',    'fa-truck',              '#f59e0b'],
    ['Vendors',        '/static/pages/vendors.html',            'fa-building',           '#ef4444'],
    ['Inventory',      '/static/pages/inventory.html',          'fa-warehouse',          '#06b6d4'],
    ['MFG Orders',     '/static/pages/mfg-orders.html',         'fa-cogs',               '#8b5cf6'],
    ['Bill of Materials','/static/pages/boms.html',             'fa-sitemap',            '#f97316'],
    ['Stock Ledger',   '/static/pages/stock-ledger.html',       'fa-clipboard-list',     '#10b981'],
    ['Reports',        '/static/pages/reports.html',            'fa-chart-bar',          '#6366f1'],
    ['Users',          '/static/pages/users.html',              'fa-users-cog',          '#ef4444'],
  ];

  o.innerHTML = `
    <div style="background:var(--bg-card);border-radius:16px;width:100%;max-width:580px;margin:0 1rem;
                box-shadow:0 30px 60px rgba(0,0,0,.3);overflow:hidden;animation:gsSlide .2s ease;">
      <!-- Search input row -->
      <div style="display:flex;align-items:center;gap:.75rem;padding:1rem 1.25rem;
                  border-bottom:1.5px solid var(--border);">
        <i class="fas fa-search" style="color:var(--primary);font-size:1rem;flex-shrink:0;"></i>
        <input id="gsi" type="text" placeholder="Search pages & modules…"
               style="flex:1;border:none;outline:none;background:transparent;font-size:1rem;
                      color:var(--text-primary);font-family:inherit;caret-color:var(--primary);"
               oninput="gsFilter(this.value)" autofocus>
        <div style="display:flex;align-items:center;gap:.35rem;">
          <kbd style="background:var(--bg-main);border:1.5px solid var(--border);padding:.2rem .5rem;
                      border-radius:6px;font-size:.68rem;color:var(--text-muted);font-family:inherit;">Esc</kbd>
        </div>
      </div>
      <!-- Quick links grid -->
      <div style="padding:1rem;max-height:55vh;overflow-y:auto;" id="gsResults">
        <div style="font-size:.68rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
                    color:var(--text-muted);margin-bottom:.65rem;padding:0 .25rem;">Quick Navigation</div>
        <div id="gsGrid" style="display:grid;grid-template-columns:repeat(2,1fr);gap:.4rem;">
          ${pages.map(([label,href,icon,color])=>`
            <a href="${href}" class="gs-item" data-label="${label.toLowerCase()}"
               style="display:flex;align-items:center;gap:.65rem;padding:.6rem .75rem;
                      border-radius:10px;background:var(--bg-main);border:1.5px solid transparent;
                      text-decoration:none;transition:all .15s;color:var(--text-primary);"
               onmouseenter="this.style.background='var(--bg-card2)';this.style.borderColor='${color}'"
               onmouseleave="this.style.background='var(--bg-main)';this.style.borderColor='transparent'">
              <div style="width:30px;height:30px;border-radius:8px;background:${color}20;
                          display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                <i class="fas ${icon}" style="color:${color};font-size:.78rem;"></i>
              </div>
              <span style="font-size:.82rem;font-weight:600;">${label}</span>
            </a>`).join('')}
        </div>
        <div id="gsEmpty" style="display:none;padding:2rem;text-align:center;color:var(--text-muted);font-size:.85rem;">
          <i class="fas fa-search" style="display:block;font-size:1.5rem;opacity:.3;margin-bottom:.5rem;"></i>
          No matching pages found
        </div>
      </div>
      <!-- Footer hint -->
      <div style="padding:.6rem 1.25rem;border-top:1px solid var(--border);display:flex;gap:1rem;
                  font-size:.7rem;color:var(--text-muted);">
        <span><kbd style="background:var(--bg-main);border:1px solid var(--border);padding:.1rem .35rem;border-radius:4px;margin-right:.3rem;">↑↓</kbd>Navigate</span>
        <span><kbd style="background:var(--bg-main);border:1px solid var(--border);padding:.1rem .35rem;border-radius:4px;margin-right:.3rem;">Enter</kbd>Open</span>
        <span><kbd style="background:var(--bg-main);border:1px solid var(--border);padding:.1rem .35rem;border-radius:4px;margin-right:.3rem;">Esc</kbd>Close</span>
      </div>
    </div>`;

  o.addEventListener('click', e => { if (e.target===o) o.remove(); });
  document.body.appendChild(o);
  document.addEventListener('keydown', function esc(e) {
    if (e.key==='Escape') { o.remove(); document.removeEventListener('keydown',esc); }
  });
}

function gsFilter(val) {
  const q = val.toLowerCase().trim();
  const items = document.querySelectorAll('.gs-item');
  let visible = 0;
  items.forEach(el => {
    const match = !q || el.dataset.label.includes(q);
    el.style.display = match ? '' : 'none';
    if (match) visible++;
  });
  document.getElementById('gsEmpty').style.display = visible ? 'none' : 'block';
}

document.addEventListener('keydown', e => { if ((e.ctrlKey||e.metaKey) && e.key==='k') { e.preventDefault(); toggleGlobalSearch(); } });

/* ── CSS Animations ───────────────────────────────────────────────── */
const style = document.createElement('style');
style.textContent = `
  @keyframes slideInRight { from{opacity:0;transform:translateX(20px)} to{opacity:1;transform:translateX(0)} }
  @keyframes slideOutRight { from{opacity:1;transform:translateX(0)} to{opacity:0;transform:translateX(20px)} }
  @keyframes gsIn    { from{opacity:0} to{opacity:1} }
  @keyframes gsSlide { from{opacity:0;transform:translateY(-16px) scale(.97)} to{opacity:1;transform:translateY(0) scale(1)} }
`;
document.head.appendChild(style);

/* ── Flash auto-dismiss ───────────────────────────────────────────── */
setTimeout(() => {
  document.querySelectorAll('.alert').forEach(el => {
    el.style.transition='opacity .4s'; el.style.opacity='0';
    setTimeout(()=>el.remove(),400);
  });
}, 5000);

/* ── Table row click ──────────────────────────────────────────────── */
document.addEventListener('click', e => {
  const row = e.target.closest('tr[data-href]');
  if (row) window.location.href = row.dataset.href;
});
