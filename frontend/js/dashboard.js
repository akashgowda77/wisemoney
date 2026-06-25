function animateNumber(el, to, duration = 900) {
  const from = Number(el.dataset.from || 0);
  el.dataset.from = String(from);
  const start = performance.now();
  const diff = to - from;

  function tick(now) {
    const t = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - t, 3);
    const val = from + diff * eased;
    el.textContent = WiseMoneyAPI.formatINR(val);
    if (t < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

function buildChart(ctx, config) {
  return new Chart(ctx, config);
}

function destroyChartInstance(elId) {
  const c = window.__wiseMoneyDashCharts?.[elId];
  if (c?.destroy) {
    try { c.destroy(); } catch (_) {}
  }
  if (window.__wiseMoneyDashCharts && window.__wiseMoneyDashCharts[elId]) {
    window.__wiseMoneyDashCharts[elId] = null;
  }
}

function renderWalletIntelligence({ wallets }) {
  const safeWallets = Array.isArray(wallets) ? wallets : [];

  const total = document.getElementById("dashWalletTotal");
  const largestName = document.getElementById("dashLargestWalletName");
  const largestBalance = document.getElementById("dashLargestWalletBalance");
  const mostActiveName = document.getElementById("dashMostActiveWalletName");
  const mostActiveActivity = document.getElementById("dashMostActiveWalletActivity");
  const distWrap = document.getElementById("dashWalletDistribution");
  const distEmpty = document.getElementById("dashWalletDistributionEmpty");
  const bigBalance = document.getElementById("dashWalletBalanceBig");

  const totalWallets = safeWallets.length;
  const totalBalance = safeWallets.reduce((acc, w) => acc + Number(w.balance ?? 0), 0);

  if (total) total.textContent = String(totalWallets);
  if (bigBalance) bigBalance.textContent = WiseMoneyAPI.formatINR(totalBalance);

  const largest = safeWallets
    .slice()
    .sort((a, b) => Number(b.balance ?? 0) - Number(a.balance ?? 0))[0];

  if (largestName) largestName.textContent = largest?.name ?? "—";
  if (largestBalance) largestBalance.textContent = largest ? WiseMoneyAPI.formatINR(largest.balance) : "—";

  // Distribution (wallet breakdown)
  if (distWrap) distWrap.innerHTML = "";
  if (!safeWallets.length) {
    if (distEmpty) distEmpty.style.display = "block";
    return;
  }
  if (distEmpty) distEmpty.style.display = "none";

  // Future-proof: render generic wallet distribution rows
  // (supports savings/emergency/investment wallets later without redesign)
  const topList = safeWallets.slice().sort((a, b) => Number(b.balance ?? 0) - Number(a.balance ?? 0));
  topList.slice(0, 5).forEach((w) => {
    const item = document.createElement("div");
    item.className = "card-glass p-3";
    item.style.background = "rgba(255,255,255,.04)";
    item.innerHTML = `
      <div class="d-flex justify-content-between align-items-center gap-2">
        <div style="font-weight:900;">${w.name}</div>
        <div style="font-weight:900;">${WiseMoneyAPI.formatINR(w.balance)}</div>
      </div>
    `;
    distWrap?.appendChild(item);
  });

  // Most Active requires per-wallet stats; we do async caller in loadDashboard.
  if (mostActiveName) mostActiveName.textContent = largest?.name ?? "—";
  if (mostActiveActivity) mostActiveActivity.textContent = "—";
}

async function renderMostActiveWallet(wallets) {
  const safeWallets = Array.isArray(wallets) ? wallets : [];
  const mostActiveName = document.getElementById("dashMostActiveWalletName");
  const mostActiveActivity = document.getElementById("dashMostActiveWalletActivity");

  if (!safeWallets.length) {
    if (mostActiveName) mostActiveName.textContent = "—";
    if (mostActiveActivity) mostActiveActivity.textContent = "—";
    return;
  }

  let best = null;
  let bestScore = -Infinity;

  for (const w of safeWallets) {
    try {
      const stats = await WiseMoneyAPI.apiGet(`/wallet/${w.id}/stats`);
      const transferIn = Number(stats?.transfer_in ?? 0);
      const transferOut = Number(stats?.transfer_out ?? 0);
      const activity = transferIn + transferOut;

      if (activity > bestScore) {
        bestScore = activity;
        best = w;
      }
    } catch (_) {
      // ignore
    }
  }

  if (!best) return;

  if (bestScore <= 0) {
    const largest = safeWallets
      .slice()
      .sort((a, b) => Number(b.balance ?? 0) - Number(a.balance ?? 0))[0];
    best = largest || best;
    bestScore = 0;
  }

  if (mostActiveName) mostActiveName.textContent = best?.name ?? "—";
  if (mostActiveActivity) {
    if (bestScore > 0) mostActiveActivity.textContent = `${WiseMoneyAPI.formatINR(bestScore)} activity`;
    else mostActiveActivity.textContent = "No activity yet";
  }
}

async function loadDashboard() {
  WiseMoneyAuth.requireAuth();

  const [dash, score, health, categories, advisor, wallets] = await Promise.all([
    WiseMoneyAPI.apiGet("/dashboard/"),
    WiseMoneyAPI.apiGet("/dashboard/score"),
    WiseMoneyAPI.apiGet("/dashboard/health"),
    WiseMoneyAPI.apiGet("/insights/categories"),
    WiseMoneyAPI.apiGet("/advisor/recommend"),
    WiseMoneyAPI.apiGet("/wallet/"),
  ]);

  // defensive nulls
  const safeDash = dash || {};
  const safeWallets = Array.isArray(wallets) ? wallets : [];


  // KPI cards
  const incomeCard = document.getElementById("incomeCard");
  const expenseCard = document.getElementById("expenseCard");
  const walletCard = document.getElementById("walletCard");
  const scoreCard = document.getElementById("scoreCard");

  const financialOverview = safeDash?.financial_overview || {};

  const totalIncome = financialOverview?.total_income ?? 0;
  const totalExpense = financialOverview?.total_expense ?? 0;
  const walletBalance = financialOverview?.wallet_balance ?? 0;

  if (incomeCard) animateNumber(incomeCard, totalIncome);
  if (expenseCard) animateNumber(expenseCard, totalExpense);
  if (walletCard) animateNumber(walletCard, walletBalance);
  if (scoreCard) scoreCard.textContent = `${score?.financial_score ?? 0}`;

  // Wallet Intelligence (multi-wallet)
  renderWalletIntelligence({ wallets: safeWallets });
  await renderMostActiveWallet(safeWallets);


  // Charts
  const incomeExpenseChartEl = document.getElementById("incomeExpenseChart");
  const expensePieChartEl = document.getElementById("expensePieChart");

  // Income vs Expense: use trend from report to get a time series
  const trend = await WiseMoneyAPI.apiGet("/report/trend");
  if (incomeExpenseChartEl) {
    const labels = (trend || []).map((x) => x.month);
    const incomeData = (trend || []).map((x) => x.income);
    const expenseData = (trend || []).map((x) => x.expense);

    buildChart(incomeExpenseChartEl.getContext("2d"), {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Income",
            data: incomeData,
            borderColor: "rgba(124,77,255,1)",
            backgroundColor: "rgba(124,77,255,.12)",
            fill: true,
            tension: 0.35,
          },
          {
            label: "Expense",
            data: expenseData,
            borderColor: "rgba(0,212,255,1)",
            backgroundColor: "rgba(0,212,255,.10)",
            fill: true,
            tension: 0.35,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: "rgba(255,255,255,.75)" },
          },
        },
        scales: {
          x: {
            ticks: { color: "rgba(255,255,255,.65)" },
            grid: { color: "rgba(255,255,255,.06)" },
          },
          y: {
            ticks: { color: "rgba(255,255,255,.65)" },
            grid: { color: "rgba(255,255,255,.06)" },
          },
        },
      },
    });
  }

  // Expense Breakdown (pie) - from /insights/categories
  if (expensePieChartEl) {
    const safeCats = Array.isArray(categories) ? categories : [];
    const labels = safeCats.map((x) => x.category);
    const amounts = safeCats.map((x) => x.total);

    buildChart(expensePieChartEl.getContext("2d"), {
      type: "doughnut",
      data: {
        labels,
        datasets: [
          {
            data: amounts,
            backgroundColor: [
              "rgba(124,77,255,.85)",
              "rgba(0,212,255,.75)",
              "rgba(46,229,157,.65)",
              "rgba(255,176,32,.65)",
              "rgba(255,77,109,.65)",
              "rgba(255,77,255,.45)",
            ],
            borderColor: "rgba(0,0,0,.0)",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "rgba(255,255,255,.75)" } },
        },
      },
    });
  }

  // Goals progress section - from advisor.goal_analysis
  const goalContainer = document.getElementById("goalContainer");
  const goalsEmpty = document.getElementById("goalsEmpty");

  if (goalContainer) {
    const goals = Array.isArray(advisor?.goal_analysis) ? advisor.goal_analysis : [];
    goalContainer.innerHTML = "";

    if (!goals.length) {
      if (goalsEmpty) goalsEmpty.style.display = "block";
    } else {
      if (goalsEmpty) goalsEmpty.style.display = "none";
      goals.forEach((g) => {
        const pct = Math.max(0, Math.min(100, Number(g.progress_percentage ?? 0)));
        const col = document.createElement("div");
        col.className = "col-12";
        col.innerHTML = `
          <div class="card-glass p-3" style="background:rgba(255,255,255,.05);">
            <div class="d-flex justify-content-between align-items-start gap-2">
              <div>
                <div style="font-weight:900;">${g.goal_name ?? "—"}</div>
                <div class="small-muted mt-1">${WiseMoneyAPI.formatINR(g.remaining_amount ?? 0)} remaining</div>
              </div>
              <div style="text-align:right;">
                <div style="font-weight:900; font-size:18px;">${pct.toFixed(2)}%</div>
                <div class="small-muted">progress</div>
              </div>
            </div>
            <div class="progress mt-3" style="height:10px; background:rgba(255,255,255,.06)">
              <div class="progress-bar" role="progressbar" style="width:${pct}%; background:linear-gradient(135deg, var(--brand), var(--brand-2));" aria-valuenow="${pct}" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
          </div>
        `;
        goalContainer.appendChild(col);
      });
    }
  }

  // AI Advisor Summary section
  const advisorContainer = document.getElementById("advisorContainer");
  const advisorEmpty = document.getElementById("advisorEmpty");
  if (advisorContainer) {
    const recommendations = Array.isArray(advisor?.recommendations)
      ? advisor.recommendations
      : [];

    const finScore = advisor?.financial_health?.financial_score ?? 0;
    advisorContainer.innerHTML = "";

    if (!recommendations.length) {
      if (advisorEmpty) advisorEmpty.style.display = "block";
    } else {
      if (advisorEmpty) advisorEmpty.style.display = "none";

      const scoreLine = document.createElement("div");
      scoreLine.className = "card-glass p-3";
      scoreLine.innerHTML = `
        <div style="font-weight:900; margin-bottom:8px;">
          <i class="fa-solid fa-star me-2" style="color:var(--warning);"></i>
          Financial Score: ${finScore}
        </div>
        <div class="small-muted">Top spending: <b>${advisor?.top_spending_category ?? "—"}</b></div>
      `;
      advisorContainer.appendChild(scoreLine);

      const recWrap = document.createElement("div");
      recWrap.className = "d-flex flex-column gap-2";

      recommendations.slice(0, 4).forEach((r) => {
        const item = document.createElement("div");
        item.className = "card-glass p-3";
        item.innerHTML = `<div style="font-weight:800; margin-bottom:6px;">Recommendation</div><div class="small-muted" style="color:rgba(255,255,255,.78)">${r}</div>`;
        recWrap.appendChild(item);
      });

      advisorContainer.appendChild(recWrap);
    }
  }
}

window.addEventListener("DOMContentLoaded", loadDashboard);

