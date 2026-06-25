function qs(id) {
  return document.getElementById(id);
}

function toDateOnlyString(d) {
  // d can be Date or string
  if (!d) return "";
  const dt = typeof d === "string" ? new Date(d) : d;
  const yyyy = dt.getFullYear();
  const mm = String(dt.getMonth() + 1).padStart(2, "0");
  const dd = String(dt.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

function sortBy(a, b, key, dir) {
  const av = a[key];
  const bv = b[key];
  if (av === bv) return 0;
  const mul = dir === "desc" ? -1 : 1;
  return av > bv ? mul : -mul;
}

function renderTable(rows, { page, pageSize, container }) {
  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  const slice = rows.slice(start, end);

  container.innerHTML = "";

  if (!slice.length) {
    container.innerHTML = `
      <tr>
        <td colspan="8" class="small-muted text-center">No transactions found</td>
      </tr>
    `;
    return;
  }

  slice.forEach((t) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${t.id}</td>
      <td>${t.transaction_type}</td>
      <td>${t.category ?? "—"}</td>
      <td>${t.description ?? "—"}</td>
      <td>${WiseMoneyAPI.formatINR(t.amount)}</td>
      <td>${t.wallet_id ?? "—"}</td>
      <td class="small-muted">—</td>
    `;
    container.appendChild(tr);
  });

  return { start, end: Math.min(end, rows.length) };
}

async function loadWallets() {
  const wallets = await WiseMoneyAPI.apiGet("/wallet/");
  return wallets || [];
}

async function loadTransactions() {
  // Backend has /transactions/ with category/description/wallet_id but no pagination.
  return WiseMoneyAPI.apiGet("/transactions/");
}

async function createIncome(payload) {
  // backend expects /income/ with exact fields: amount, source, date?, wallet_id
  await WiseMoneyAPI.apiPost("/income/", payload);
}

async function createExpense(payload) {
  // backend expects /expense/ with exact fields: amount, category, date?, wallet_id
  await WiseMoneyAPI.apiPost("/expense/", payload);
}

async function refreshAndRender(state) {
  const [transactions, wallets] = await Promise.all([loadTransactions(), loadWallets()]);
  state.allTransactions = transactions || [];
  state.wallets = wallets || [];

  // Wallet select
  const walletSelect = qs("walletSelect");
  const expenseWalletSelect = qs("expenseWalletSelect");

  const options = state.wallets
      .map(
          w => `
          <option value="${w.id}">
              ${w.name} (${WiseMoneyAPI.formatINR(w.balance)})
          </option>
      `
      )
      .join("");

  // Income wallet
  if (walletSelect) {
      const current = walletSelect.value;

      walletSelect.innerHTML = options;

      if (
          current &&
          state.wallets.some(w => String(w.id) === current)
      ) {
          walletSelect.value = current;
      }
  }

  // Expense wallet
  if (expenseWalletSelect) {
      const current = expenseWalletSelect.value;

      expenseWalletSelect.innerHTML = options;

      if (
          current &&
          state.wallets.some(w => String(w.id) === current)
      ) {
          expenseWalletSelect.value = current;
      }
  }

  applyFiltersAndRender(state);
}

function applyFiltersAndRender(state) {
  const q = (qs("searchInput")?.value || "").trim().toLowerCase();
  const filterType = qs("typeFilter")?.value || "all";

  const sortKey = qs("sortBy")?.value || "id";
  const sortDir = qs("sortDir")?.value || "asc";

  const page = Number(qs("pageNum")?.value || state.page);
  const pageSize = state.pageSize;

  let rows = [...(state.allTransactions || [])];

  if (filterType !== "all") {
    rows = rows.filter((r) => r.transaction_type === filterType);
  }

  if (q) {
    rows = rows.filter((r) => {
      const hay = `${r.id} ${r.transaction_type} ${r.category ?? ""} ${r.description ?? ""} ${r.wallet_id ?? ""} ${r.amount}`.toLowerCase();
      return hay.includes(q);
    });
  }

  rows.sort((a, b) => sortBy(a, b, sortKey, sortDir));

  state.filteredTransactions = rows;
  state.page = page;

  const tbody = qs("txTbody");
  const pagerMeta = qs("pagerMeta");

  renderTable(rows, { page, pageSize, container: tbody });

  const totalPages = Math.max(1, Math.ceil(rows.length / pageSize));
  if (qs("pageNum")) {
    qs("pageNum").max = String(totalPages);
    qs("pageNum").value = String(Math.min(page, totalPages));
  }
  if (pagerMeta) {
    const start = (Math.min(page, totalPages) - 1) * pageSize + 1;
    const end = Math.min((Math.min(page, totalPages)) * pageSize, rows.length);
    pagerMeta.textContent = `Showing ${rows.length ? start : 0} - ${end} of ${rows.length}`;
  }
}

function wireUI(state) {
  // Filters
  qs("searchInput")?.addEventListener("input", () => {
    state.page = 1;
    applyFiltersAndRender(state);
  });

  qs("typeFilter")?.addEventListener("change", () => {
    state.page = 1;
    applyFiltersAndRender(state);
  });

  qs("sortBy")?.addEventListener("change", () => {
    state.page = 1;
    applyFiltersAndRender(state);
  });

  qs("sortDir")?.addEventListener("change", () => {
    state.page = 1;
    applyFiltersAndRender(state);
  });

  qs("pageNum")?.addEventListener("change", () => {
    applyFiltersAndRender(state);
  });

  // Page size not required by spec; keep fixed.

  // Income/Expense forms
  const addIncomeBtn = qs("addIncomeBtn");
  if (addIncomeBtn) {
    addIncomeBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      const amount = Number(qs("incomeAmount").value);
      const source = qs("incomeSource").value;
      const date = qs("incomeDate").value;
      const walletId =
        Number(
            qs("walletSelect").value
        );

      if (!source) return alert("Enter income source");
      if (!walletId) return alert("Select wallet");

      await createIncome({ amount, source, date: date ? `${date}` : undefined, wallet_id: walletId });
      await refreshAndRender(state);
      alert("Income added");
    });
  }

  const addExpenseBtn = qs("addExpenseBtn");
  if (addExpenseBtn) {
    addExpenseBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      const amount = Number(qs("expenseAmount").value);
      const category = qs("expenseCategory").value;
      const date = qs("expenseDate").value;
      const walletId = Number(qs("expenseWalletSelect").value);

      if (!category) return alert("Enter expense category");
      if (!walletId) return alert("Select wallet");
      
      console.log({
          amount,
          category,
          date: date ? `${date}` : undefined,
          walletId
      });
      console.log(
          "Expense Wallet:",
          qs("expenseWalletSelect").value
      );
      
      await createExpense({ amount, category, date: date ? `${date}` : undefined, wallet_id: walletId });
      await refreshAndRender(state);
      alert("Expense added");
    });
  }

  // Add wallet if desired is not required by task.
}

async function initTransactionsPage() {
  WiseMoneyAuth.requireAuth();

  const state = {
    allTransactions: [],
    filteredTransactions: [],
    wallets: [],
    page: 1,
    pageSize: 8,
  };

  wireUI(state);
  await refreshAndRender(state);

  // Populate page dropdown based on current dataset
  const updatePagination = () => {
    const rows = state.filteredTransactions || state.allTransactions || [];
    const totalPages = Math.max(1, Math.ceil(rows.length / state.pageSize));
    const pageSelect = qs("pageNum");
    if (pageSelect) {
      pageSelect.innerHTML = "";
      for (let i = 1; i <= totalPages; i++) {
        const opt = document.createElement("option");
        opt.value = String(i);
        opt.textContent = String(i);
        pageSelect.appendChild(opt);
      }
      pageSelect.value = String(Math.min(state.page || 1, totalPages));
    }
  };

  const originalApplyFiltersAndRender = applyFiltersAndRender;
  applyFiltersAndRender = function (st) {
    originalApplyFiltersAndRender(st);
    updatePagination();
  };
}

window.addEventListener("DOMContentLoaded", initTransactionsPage);


