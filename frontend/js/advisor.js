async function initAdvisorPage() {
  WiseMoneyAuth.requireAuth();

  const [recommend] = await Promise.all([
    WiseMoneyAPI.apiGet("/advisor/recommend"),
  ]);

  const scoreEl = document.getElementById("financialScore");
  const topCatEl = document.getElementById("topCategory");
  const recsEl = document.getElementById("recommendations");
  const savingsAnalysisEl = document.getElementById("savingsAnalysis");
  const goalAnalysisEl = document.getElementById("goalAnalysis");

  const financialHealth = recommend?.financial_health || {};
  const financialSummary = recommend?.financial_summary || {};

  if (scoreEl) {
    const fs = financialHealth?.financial_score ?? 0;
    scoreEl.innerHTML = `<div class="value">${fs}</div><div class="small-muted">${(financialHealth?.health_status || "").toString() || (fs >= 85 ? "Excellent" : "Advisor Score")}</div>`;
  }

  if (topCatEl) topCatEl.textContent = recommend?.top_spending_category ?? "—";

  if (recsEl) {
    const list = Array.isArray(recommend?.recommendations) ? recommend.recommendations : [];
    recsEl.innerHTML = "";
    if (!list.length) {
      recsEl.innerHTML = `<div class="small-muted">No recommendations yet.</div>`;
    } else {
      list.forEach((r) => {
        const item = document.createElement("div");
        item.className = "card-glass p-3";
        item.innerHTML = `<div style="font-weight:900; margin-bottom:6px;"><i class="fa-solid fa-lightbulb" style="color:var(--brand-2)"></i> Tip</div><div class="small-muted" style="color:rgba(255,255,255,.80)">${r}</div>`;
        recsEl.appendChild(item);
      });
    }
  }

  // Savings analysis - derive from backend returned income/expense/wallet_balance
  const income = financialSummary?.income ?? 0;
  const expense = financialSummary?.expense ?? 0;
  const wallet = financialSummary?.wallet_balance ?? 0;

  if (savingsAnalysisEl) {
    const net = income - expense;
    const ratio = income > 0 ? (net / income) * 100 : 0;

    savingsAnalysisEl.innerHTML = `
      <div class="d-flex gap-2 flex-wrap">
        <div class="card-glass p-3" style="flex:1; min-width:220px;">
          <div class="small-muted">Total Income</div>
          <div style="font-weight:900; font-size:22px;">${WiseMoneyAPI.formatINR(income)}</div>
        </div>
        <div class="card-glass p-3" style="flex:1; min-width:220px;">
          <div class="small-muted">Total Expense</div>
          <div style="font-weight:900; font-size:22px;">${WiseMoneyAPI.formatINR(expense)}</div>
        </div>
        <div class="card-glass p-3" style="flex:1; min-width:220px;">
          <div class="small-muted">Wallet Balance</div>
          <div style="font-weight:900; font-size:22px;">${WiseMoneyAPI.formatINR(wallet)}</div>
        </div>
      </div>

      <div class="card-glass p-3 mt-3">
        <div style="font-weight:900; margin-bottom:6px;">Savings Analysis</div>
        <div class="small-muted">Net savings: <b>${WiseMoneyAPI.formatINR(net)}</b></div>
        <div class="small-muted">Savings ratio: <b>${ratio.toFixed(2)}%</b></div>
      </div>
    `;
  }

  // Goal analysis
  if (goalAnalysisEl) {
    const goals = Array.isArray(recommend?.goal_analysis) ? recommend.goal_analysis : [];
    if (!goals.length) {
      goalAnalysisEl.innerHTML = `<div class="small-muted">No goals available.</div>`;
    } else {
      goalAnalysisEl.innerHTML = "";
      goals.forEach((g) => {
        const pct = Math.max(0, Math.min(100, Number(g.progress_percentage ?? 0)));
        const card = document.createElement("div");
        card.className = "card-glass p-3 mb-3";
        card.innerHTML = `
          <div class="d-flex justify-content-between align-items-start gap-2">
            <div>
              <div style="font-weight:900;">${g.goal_name ?? "—"}</div>
              <div class="small-muted">Remaining: <b>${WiseMoneyAPI.formatINR(g.remaining_amount ?? 0)}</b></div>
            </div>
            <div style="text-align:right;">
              <div style="font-weight:900; font-size:18px;">${pct.toFixed(2)}%</div>
              <div class="small-muted">progress</div>
            </div>
          </div>
          <div class="progress mt-3" style="height:10px; background:rgba(255,255,255,.06)">
            <div class="progress-bar" role="progressbar" style="width:${pct}%; background:linear-gradient(135deg, var(--brand), var(--brand-2));"></div>
          </div>
          <div class="small-muted mt-2">Estimated months: <b>${g.estimated_months ?? "—"}</b></div>
        `;
        goalAnalysisEl.appendChild(card);
      });
    }
  }
}

window.addEventListener("DOMContentLoaded", initAdvisorPage);

