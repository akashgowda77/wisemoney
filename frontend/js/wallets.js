let __walletsState = {
  wallets: [],
  activeWalletIdForModal: null,
  walletStatsCache: {},
};

function qs(id) {
  return document.getElementById(id);
}

function show(el) {
  if (el) el.style.display = "";
}

function hide(el) {
  if (el) el.style.display = "none";
}

function clampMoney(n) {
  const v = Number(n ?? 0);
  return Number.isFinite(v) ? v : 0;
}

function formatActivity(a) {
  // Stats may not provide activity fields consistently; we display a simple number.
  return WiseMoneyAPI.formatINR(clampMoney(a));
}

function toastInit() {
  const toastEl = qs("wisemoneyToast");
  const toastBody = qs("wisemoneyToastBody");
  if (!toastEl || !toastBody || typeof bootstrap === "undefined") return null;

  const toast = new bootstrap.Toast(toastEl, { delay: 2800 });

  return {
    showToast: (msg, tone = "info") => {
      toastBody.textContent = msg;
      // tone styling is intentionally minimal (existing CSS uses dark toast background)
      toast.show();
    },
  };
}

let __toast = null;

function computeWalletKPIs(wallets) {
  const safeWallets = Array.isArray(wallets) ? wallets : [];

  const totalWallets = safeWallets.length;
  const totalBalance = safeWallets.reduce((acc, w) => acc + clampMoney(w.balance), 0);

  const largest = safeWallets
    .slice()
    .sort((a, b) => clampMoney(b.balance) - clampMoney(a.balance))[0];

  return {
    totalWallets,
    totalBalance,
    largest,
  };
}

async function fetchAllWallets() {
  return WiseMoneyAPI.apiGet("/wallet/").then((x) => x || []);
}

function updateWalletSelects(wallets) {
  const fromSel = qs("fromWallet");
  const toSel = qs("toWallet");

  if (!fromSel || !toSel) return;

  const safeWallets = Array.isArray(wallets)
    ? wallets
    : [];

  const options = safeWallets
    .map(
      (w) => `
        <option value="${w.id}">
          ${w.name} (${WiseMoneyAPI.formatINR(w.balance)})
        </option>
      `
    )
    .join("");

  fromSel.innerHTML = options;
  toSel.innerHTML = options;

  if (safeWallets.length) {
    fromSel.value = String(safeWallets[0].id);

    if (safeWallets.length > 1) {
      toSel.value = String(safeWallets[1].id);
    } else {
      toSel.value = String(safeWallets[0].id);
    }
  }
}

function renderWalletCards(wallets) {
  const container = qs("walletsList");
  const emptyEl = qs("walletsEmpty");
  const emptyCta = qs("walletsEmptyCta");

  if (!container) return;

  container.innerHTML = "";

  const safeWallets = Array.isArray(wallets) ? wallets : [];

  if (!safeWallets.length) {
    show(emptyEl);
    show(emptyCta);
    return;
  }

  hide(emptyEl);
  hide(emptyCta);

  safeWallets.forEach((w) => {
    const col = document.createElement("div");
    col.className = "col-12";
    col.innerHTML = `
      <div class="card-glass p-3" style="background:rgba(255,255,255,.04);">
        <div class="d-flex align-items-start justify-content-between gap-3">
          <div>
            <div style="font-weight:900; font-size:16px; margin-bottom:6px;">${w.name}</div>
            <div class="small-muted">Balance: <b>${WiseMoneyAPI.formatINR(w.balance)}</b></div>
            <div class="small-muted mt-1">Wallet ID: <b>${w.id}</b></div>
          </div>
          <div class="d-flex flex-column align-items-end" style="gap:10px; min-width:140px;">
            <button type="button" class="btn btn-light rounded-4" data-walletid="${w.id}" data-action="openStats">
              <i class="fa-solid fa-arrow-right-long me-2"></i>View
            </button>
            <button type="button" class="btn btn-outline-light rounded-4" data-walletid="${w.id}" data-action="deleteWallet">
              <i class="fa-solid fa-trash me-2"></i>Delete
            </button>
          </div>
        </div>
      </div>
    `;
    container.appendChild(col);
  });
}

async function computeMostActiveWallet(wallets) {
  const safeWallets = Array.isArray(wallets) ? wallets : [];
  if (!safeWallets.length) return { mostActive: null, activityScore: 0 };

  // If stats fields are not present, fallback to 0.
  let best = null;
  let bestScore = -Infinity;

  for (const w of safeWallets) {
    try {
      const stats = await WiseMoneyAPI.apiGet(`/wallet/${w.id}/stats`);
      const transferIn = clampMoney(stats?.transfer_in);
      const transferOut = clampMoney(stats?.transfer_out);
      const activity = transferIn + transferOut;

      if (activity > bestScore) {
        bestScore = activity;
        best = w;
      }

      __walletsState.walletStatsCache[w.id] = stats || {};
    } catch (e) {
      // ignore
    }
  }

  if (!best) return { mostActive: null, activityScore: 0 };

  if (bestScore <= 0) {
    const largest = safeWallets
      .slice()
      .sort((a, b) => clampMoney(b.balance) - clampMoney(a.balance))[0];
    return { mostActive: largest || best, activityScore: 0 };
  }

  return { mostActive: best, activityScore: bestScore };
}

async function updateDashboardKPIs(wallets) {
  const kpisEl = {
    totalWallets: qs("wTotalWallets"),
    totalBalance: qs("wTotalBalance"),
    largestName: qs("wLargestWalletName"),
    largestBalance: qs("wLargestWalletBalance"),
    mostActiveName: qs("wMostActiveWalletName"),
    mostActiveActivity: qs("wMostActiveWalletActivity"),
  };

  const { totalWallets, totalBalance, largest } = computeWalletKPIs(wallets);

  if (kpisEl.totalWallets) kpisEl.totalWallets.textContent = String(totalWallets);
  if (kpisEl.totalBalance) kpisEl.totalBalance.textContent = WiseMoneyAPI.formatINR(totalBalance);

  if (kpisEl.largestName) kpisEl.largestName.textContent = largest?.name ?? "—";
  if (kpisEl.largestBalance) kpisEl.largestBalance.textContent = largest ? WiseMoneyAPI.formatINR(largest.balance) : "—";

  const { mostActive, activityScore } = await computeMostActiveWallet(wallets);

  if (kpisEl.mostActiveName) kpisEl.mostActiveName.textContent = mostActive?.name ?? "—";
  if (kpisEl.mostActiveActivity) {
    kpisEl.mostActiveActivity.textContent = bestActivityLabel(mostActive, activityScore);
  }
}

function bestActivityLabel(mostActive, activityScore) {
  if (!mostActive) return "—";
  if (activityScore > 0) return `${formatActivity(activityScore)} activity`;
  return "No activity yet";
}

function wireWalletListHandlers() {
  const container = qs("walletsList");
  if (!container) return;

  container.addEventListener("click", async (e) => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;

    const walletId = String(btn.getAttribute("data-walletid"));
    const action = btn.getAttribute("data-action");

    if (action === "openStats") {
      await openWalletStatsModal(walletId);
    }

    if (action === "deleteWallet") {
      __walletsState.activeWalletIdForModal = walletId;
      const modalEl = qs("deleteWalletConfirmModal");
      if (!modalEl) return;
      const modal = new bootstrap.Modal(modalEl);
      modal.show();
    }
  });
}

async function openWalletStatsModal(walletId) {
  __walletsState.activeWalletIdForModal = walletId;

  const modalEl = qs("walletStatsModal");
  const titleEl = qs("walletStatsTitle");
  const subtitleEl = qs("walletStatsSubtitle");

  const stats = __walletsState.walletStatsCache[walletId]
    ? __walletsState.walletStatsCache[walletId]
    : await WiseMoneyAPI.apiGet(`/wallet/${walletId}/stats`);

  if (subtitleEl) subtitleEl.textContent = `Wallet ID: ${walletId}`;

  const wallets = __walletsState.wallets || [];
  const wallet = wallets.find((w) => String(w.id) === String(walletId));

  if (titleEl) titleEl.textContent = wallet?.name || stats?.wallet_name || "Wallet Details";

  qs("wsCurrentBalance").textContent = WiseMoneyAPI.formatINR(stats?.current_balance ?? 0);
  qs("wsGoalFunding").textContent = WiseMoneyAPI.formatINR(stats?.goal_funding ?? 0);
  qs("wsTotalIncome").textContent = WiseMoneyAPI.formatINR(stats?.total_income ?? 0);
  qs("wsTotalExpense").textContent = WiseMoneyAPI.formatINR(stats?.total_expense ?? 0);
  qs("wsTransferIn").textContent = WiseMoneyAPI.formatINR(stats?.transfer_in ?? 0);
  qs("wsTransferOut").textContent = WiseMoneyAPI.formatINR(stats?.transfer_out ?? 0);

  if (modalEl) {
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  }
}

function wireCreateWalletForm() {
  const form = qs("createWalletForm");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = qs("walletName")?.value?.trim();
    const balance = Number(qs("walletBalance")?.value);

    if (!name) return alert("Enter wallet name");
    if (!Number.isFinite(balance) || balance < 0) return alert("Enter a valid initial balance");

    const submitBtn = form.querySelector("button[type='submit']");
    if (submitBtn) submitBtn.disabled = true;

    try {
      await WiseMoneyAPI.apiPost("/wallet/", { name, balance });
      form.reset();

      // Refresh
      await refreshAll();

      __toast?.showToast("Wallet created successfully");
    } catch (err) {
      console.error(err);
      alert(err?.message || String(err));
    } finally {
      if (submitBtn) submitBtn.disabled = false;
    }
  });
}

function wireTransferForm() {
  const form = qs("transferForm");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const from_wallet = Number(qs("fromWallet").value);
    const to_wallet = Number(qs("toWallet").value);
    const amount = Number(qs("transferAmount").value);

    if (!from_wallet || !to_wallet) return alert("Select source and destination wallets");
    if (!Number.isFinite(amount) || amount <= 0) return alert("Enter a valid transfer amount");
    if (from_wallet === to_wallet) return alert("From Wallet and To Wallet must be different");

    const submitBtn = form.querySelector("button[type='submit']");
    if (submitBtn) submitBtn.disabled = true;

    try {
      await WiseMoneyAPI.apiPost("/wallet/transfer", {
        from_wallet,
        to_wallet,
        amount,
      });

      // Refresh wallets + KPIs + breakdown
      await refreshAll();

      __toast?.showToast("Transfer completed successfully");
    } catch (err) {
      console.error(err);
      alert(err?.message || String(err));
    } finally {
      if (submitBtn) submitBtn.disabled = false;
    }
  });
}

function wireDeleteConfirm() {
  const confirmBtn = qs("confirmDeleteWalletBtn");
  const deleteModalEl = qs("deleteWalletConfirmModal");

  if (!confirmBtn) return;

  confirmBtn.addEventListener("click", async () => {
    const walletId = __walletsState.activeWalletIdForModal;
    if (!walletId) return;

    confirmBtn.disabled = true;

    // Use fetch direct with auth header to perform DELETE.
    try {
      const token = WiseMoneyAPI?.token || localStorage.getItem("token");
      const res = await fetch(`${WiseMoneyAPI.API_BASE}/wallet/${walletId}`, {
        method: "DELETE",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      let data;
      const ct = res.headers.get("content-type") || "";
      if (ct.includes("application/json")) data = await res.json();
      else data = await res.text();

      if (!res.ok) {
        const detail = data && data.detail ? data.detail : res.statusText;
        throw new Error(detail || `Delete failed (${res.status})`);
      }

      await refreshAll();
      __toast?.showToast("Wallet deleted successfully");

      if (deleteModalEl) {
        const modal = bootstrap.Modal.getInstance(deleteModalEl) || new bootstrap.Modal(deleteModalEl);
        modal.hide();
      }
    } catch (err) {
      console.error(err);
      alert(err?.message || String(err));
    } finally {
      confirmBtn.disabled = false;
      __walletsState.activeWalletIdForModal = null;
    }
  });
}

async function refreshAll() {
  __walletsState.wallets = await fetchAllWallets();

  updateWalletSelects(__walletsState.wallets);
  renderWalletCards(__walletsState.wallets);
  await updateDashboardKPIs(__walletsState.wallets);

  // If modal is open, keep it updated if we have stats cache
  if (__walletsState.activeWalletIdForModal) {
    const wid = __walletsState.activeWalletIdForModal;
    try {
      await openWalletStatsModal(wid);
    } catch (_) {
      // ignore
    }
  }

  // Let dashboard refresh wallet intelligence (no full-page reload)
  window.dispatchEvent(new CustomEvent("wisemoney:wallets-updated"));
}

function wireJumpCreateWalletCTA() {
  const btn = qs("jumpCreateWallet");
  if (!btn) return;

  btn.addEventListener("click", () => {
    const formCard = qs("createWalletCard");
    formCard?.scrollIntoView({ behavior: "smooth", block: "start" });
  });
}

async function initWalletsPage() {
  WiseMoneyAuth.requireAuth();

  __toast = toastInit();

  wireJumpCreateWalletCTA();
  wireWalletListHandlers();
  wireCreateWalletForm();
  wireTransferForm();
  wireDeleteConfirm();

  // Allow refresh button in HTML
  window.WiseMoneyWallets = {
    refreshAll,
    refreshWalletsOnly: refreshAll,
  };

  await refreshAll();
}

window.addEventListener("DOMContentLoaded", initWalletsPage);

