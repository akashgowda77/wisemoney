async function renderProgressCard(container, { title, value, subtitle, pct, colorVar }) {
  const pctClamped = Math.max(0, Math.min(100, Number(pct ?? 0)));
  const card = document.createElement("div");
  card.className = "col-12";
  card.innerHTML = `
    <div class="card-glass p-3" style="background:rgba(255,255,255,.04);">
      <div class="d-flex justify-content-between align-items-start gap-2">
        <div>
          <div style="font-weight:900; margin-bottom:4px;">${title}</div>
          <div class="small-muted">${subtitle || ""}</div>
        </div>
        <div style="text-align:right;">
          <div style="font-weight:900; font-size:18px;">${Number(value ?? 0)}</div>
          <div class="small-muted">score</div>
        </div>
      </div>
      <div class="progress mt-3" style="height:10px; background:rgba(255,255,255,.06)">
        <div class="progress-bar" style="width:${pctClamped}%; background:linear-gradient(135deg, ${colorVar}, var(--brand-2));"></div>
      </div>
    </div>
  `;
  container.appendChild(card);
}

async function initFinancialHealthPage() {
  WiseMoneyAuth.requireAuth();

  const [dashHealth, dashScore, dashSnapshot, categories, insightsHealth] = await Promise.all([
    WiseMoneyAPI.apiGet("/dashboard/health"),
    WiseMoneyAPI.apiGet("/dashboard/score"),
    WiseMoneyAPI.apiGet("/dashboard/snapshot"),
    WiseMoneyAPI.apiGet("/insights/categories").catch(() => []),
    WiseMoneyAPI.apiGet("/insights/financial-health").catch(() => null),
  ]);

  const scoreEl = document.getElementById("fhScore");
  const gradeEl = document.getElementById("fhGrade");
  const statusEl = document.getElementById("fhStatus");
  const breakdownWrap = document.getElementById("scoreBreakdown");
  const breakdownEmpty = document.getElementById("scoreBreakdownEmpty");

  const emergencyRecommendedEl = document.getElementById("emergencyRecommended");
  const emergencyPctEl = document.getElementById("emergencyPct");
  const emergencyBarEl = document.getElementById("emergencyProgressBar");
  const emergencyEmpty = document.getElementById("emergencyEmpty");

  const goalSummaryEl = document.getElementById("goalSummary");
  const goalProgressBarEl = document.getElementById("goalProgressBar");

  const recsWrap = document.getElementById("fhRecommendations");
  const recsEmpty = document.getElementById("fhRecommendationsEmpty");

  const insightsWrap = document.getElementById("fhInsights");

  const safeHealth = dashHealth || {};
  const safeScore = dashScore || {};

  // Score header
  if (scoreEl) scoreEl.textContent = String(safeHealth.financial_score ?? safeScore.financial_score ?? 0);
  if (gradeEl) gradeEl.textContent = String(safeHealth.grade ?? safeScore.grade ?? "—");
  if (statusEl) statusEl.textContent = String(safeHealth.health_status ?? safeScore.health_status ?? "—");

  // Score breakdown
  const breakdown = safeHealth.score_breakdown || safeScore.score_breakdown || {};
  const breakdownEntries = [
    { key: "savings_score", title: "Savings Score", color: "var(--success)" },
    { key: "goal_score", title: "Goal Score", color: "var(--brand)" },
    { key: "budget_score", title: "Budget Score", color: "var(--brand-2)" },
    { key: "emergency_score", title: "Emergency Fund Score", color: "var(--warning)" },
    { key: "expense_control_score", title: "Expense Control Score", color: "var(--danger)" },
  ];

  const maxScoreByKey = {
    savings_score: 35,
    goal_score: 25,
    budget_score: 20,
    emergency_score: 15,
    expense_control_score: 5,
  };

  if (breakdownWrap) {
    breakdownWrap.innerHTML = "";
    const hasAny = Object.keys(breakdown || {}).length > 0;
    if (!hasAny) {
      if (breakdownEmpty) breakdownEmpty.style.display = "block";
    } else {
      if (breakdownEmpty) breakdownEmpty.style.display = "none";

      breakdownEntries.forEach((e) => {
        const value = Number(breakdown[e.key] ?? 0);
        const max = maxScoreByKey[e.key] ?? 100;
        const pct = max > 0 ? (value / max) * 100 : 0;
        renderProgressCard(breakdownWrap, {
          title: e.title,
          value,
          subtitle: `${value}/${max}`,
          pct,
          colorVar: e.color,
        });
      });
    }
  }

  // Emergency fund
  const recFund = Number(safeHealth.recommended_emergency_fund ?? 0);
  const completion = Number(safeHealth.emergency_fund_completion ?? 0);
  if (emergencyRecommendedEl) emergencyRecommendedEl.textContent = WiseMoneyAPI.formatINR(recFund);
  if (emergencyPctEl) emergencyPctEl.textContent = `${completion.toFixed(2)}%`;
  if (emergencyBarEl) emergencyBarEl.style.width = `${Math.max(0, Math.min(100, completion))}%`;

  if (recFund <= 0 && emergencyEmpty) emergencyEmpty.style.display = "block";

  // Goal progress (computed from /goals/records)
  // Backend provides goal_progress in /dashboard/health already (average progress)
  const goalProgress = Number(safeHealth.goal_progress ?? 0);
  if (goalProgressBarEl) {
    goalProgressBarEl.style.width = `${Math.max(0, Math.min(100, goalProgress))}%`;
  }
  if (goalSummaryEl) {
    const active = insightsHealth?.goal_insights?.active_goals ?? null;
    const achieved = insightsHealth?.goal_insights?.achieved_goals ?? null;
    const total = insightsHealth?.goal_insights?.total_goals ?? null;

    const makeChip = (label, val) => `
      <div class="card-glass p-3" style="flex:1; min-width:180px; background:rgba(255,255,255,.04);">
        <div class="small-muted">${label}</div>
        <div style="font-weight:900; font-size:20px;">${val ?? "—"}</div>
      </div>
    `;

    goalSummaryEl.innerHTML = [
      makeChip("Total Goals", total),
      makeChip("Active Goals", active),
      makeChip("Achieved Goals", achieved),
    ].join("");
  }

  // Recommendations
  const recs = Array.isArray(safeHealth.recommendations) ? safeHealth.recommendations : [];
  if (recsWrap) {
    recsWrap.innerHTML = "";
    if (!recs.length) {
      if (recsEmpty) recsEmpty.style.display = "block";
    } else {
      if (recsEmpty) recsEmpty.style.display = "none";
      recs.slice(0, 6).forEach((r) => {
        const el = document.createElement("div");
        el.className = "card-glass p-3";
        el.innerHTML = `<div style="font-weight:900; margin-bottom:6px;"><i class="fa-solid fa-lightbulb me-2" style="color:var(--brand-2);"></i>Recommendation</div><div class="small-muted" style="color:rgba(255,255,255,.80)">${r}</div>`;
        recsWrap.appendChild(el);
      });
    }
  }

  // Actionable insights (use /insights/financial-health)
  if (insightsWrap) {
    insightsWrap.innerHTML = "";
    if (insightsHealth) {
      const topCat = insightsHealth?.spending_insights?.top_category ?? null;
      const budgetBreaches = Array.isArray(insightsHealth?.budget_breaches)
        ? insightsHealth.budget_breaches
        : [];

      const insightCards = [];
      insightCards.push({
        icon: "fa-solid fa-tags",
        title: "Top Spending Category",
        value: topCat ?? "—",
      });

      insightCards.push({
        icon: "fa-solid fa-triangle-exclamation",
        title: "Breached Categories",
        value: String(budgetBreaches.length),
      });

      const avgProg = insightsHealth?.goal_insights?.average_progress ?? null;
      insightCards.push({
        icon: "fa-solid fa-chart-line",
        title: "Average Goal Progress",
        value: avgProg != null ? `${Number(avgProg).toFixed(2)}%` : "—",
      });

      const mostActiveWallet = insightsHealth?.wallet_insights?.most_active_wallet ?? null;
      insightCards.push({
        icon: "fa-solid fa-wallet",
        title: "Most Active Wallet",
        value: mostActiveWallet ?? "—",
      });

      insightCards.forEach((c) => {
        const el = document.createElement("div");
        el.className = "card-glass p-3";
        el.innerHTML = `
          <div style="font-weight:900; margin-bottom:6px;">
            <i class="${c.icon} me-2" style="color:var(--brand);"></i>${c.title}
          </div>
          <div style="font-weight:900; font-size:18px;">${c.value}</div>
        `;
        insightsWrap.appendChild(el);
      });

      if (budgetBreaches.length) {
        const topBreaches = budgetBreaches
          .slice(0, 3)
          .map((b) => `<div class="small-muted">${b.category}: ${WiseMoneyAPI.formatINR(b.spent)} (exceeded by ${WiseMoneyAPI.formatINR(b.exceeded_by)})</div>`)
          .join("");

        const breachEl = document.createElement("div");
        breachEl.className = "card-glass p-3";
        breachEl.innerHTML = `
          <div style="font-weight:900; margin-bottom:6px;">
            <i class="fa-solid fa-octagon-exclamation me-2" style="color:var(--danger);"></i>Largest Breaches
          </div>
          ${topBreaches}
        `;
        insightsWrap.appendChild(breachEl);
      }
    } else {
      insightsWrap.innerHTML = `<div class="small-muted">No additional insights available.</div>`;
    }
  }
}

window.addEventListener("DOMContentLoaded", initFinancialHealthPage);

