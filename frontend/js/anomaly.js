let __anomCharts = {};

function buildChart(canvasEl, config) {
  if (!canvasEl) return null;
  return new Chart(canvasEl.getContext("2d"), config);
}

function destroyIfAny(key) {
  if (__anomCharts[key]) {
    try { __anomCharts[key].destroy(); } catch (_) {}
    __anomCharts[key] = null;
  }
}

function severityToColor(sev) {
  const s = String(sev || "").toLowerCase();
  if (s.includes("high")) return "rgba(255,77,109,.85)";
  if (s.includes("medium")) return "rgba(255,176,32,.75)";
  return "rgba(46,229,157,.65)";
}

async function initAnomalyPage() {
  WiseMoneyAuth.requireAuth();

  const [detect, summary, largest] = await Promise.all([
    WiseMoneyAPI.apiGet("/anomaly/detect").catch(() => ({})),
    WiseMoneyAPI.apiGet("/anomaly/summary").catch(() => ({})),
    WiseMoneyAPI.apiGet("/anomaly/largest").catch(() => ({})),
  ]);

  const totalEl = document.getElementById("anomTotal");
  const riskEl = document.getElementById("anomRisk");
  const largestSeverityEl = document.getElementById("anomLargestSeverity");
  const largestRiskScoreEl = document.getElementById("anomLargestRiskScore");
  const explainWrap = document.getElementById("anomExplain");
  const explainEmpty = document.getElementById("anomExplainEmpty");
  const largestCardWrap = document.getElementById("anomLargestCard");

  const total = Number(detect?.anomalies_detected ?? 0);
  const riskLevel = summary?.risk_level ?? "—";

  if (totalEl) totalEl.textContent = String(total);
  if (riskEl) riskEl.textContent = String(riskLevel);

  const anomalies = Array.isArray(detect?.anomalies) ? detect.anomalies : [];

  // Largest anomaly card + KPI
  if (largestCardWrap) {
    largestCardWrap.innerHTML = "";
    const isMsg = typeof largest?.message === "string";
    if (isMsg && !largest?.expense_id) {
      largestCardWrap.innerHTML = `
        <div class="col-12">
          <div class="card-glass p-3">${largest.message}</div>
        </div>
      `;
    } else {
      const sev = largest?.message ? undefined : largest?.severity;
      const amt = largest?.amount ?? 0;
      const expId = largest?.expense_id ?? "—";
      const cat = largest?.category ?? "—";
      const msg = largest?.message ?? "";

      const card = document.createElement("div");
      card.className = "col-12";
      card.innerHTML = `
        <div class="card-glass p-3">
          <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:10px;">
            <div>
              <div style="font-weight:900; margin-bottom:6px;">
                <i class="fa-solid fa-badge-percent me-2" style="color:var(--brand)"></i>
                Largest Anomaly
              </div>
              <div class="small-muted">Expense ID: <b>${expId}</b></div>
              <div class="small-muted">Category: <b>${cat}</b></div>
              <div class="small-muted">Amount: <b>${WiseMoneyAPI.formatINR(amt)}</b></div>
            </div>
            <div style="text-align:right;">
              <div class="small-muted">Severity</div>
              <div style="font-weight:900; font-size:18px;">${sev ?? "—"}</div>
            </div>
          </div>
          ${msg ? `<div class="small-muted mt-2">${msg}</div>` : ""}
        </div>
      `;
      largestCardWrap.appendChild(card);
    }
  }

  // KPIs from anomalies array (more reliable than /anomaly/largest)
  const largestAnom = anomalies.slice().sort((a, b) => Number(b.risk_score ?? 0) - Number(a.risk_score ?? 0))[0];
  const largestSev = largestAnom?.severity ?? largest?.severity ?? "—";
  const largestRisk = largestAnom?.risk_score ?? largest?.risk_score ?? "—";

  if (largestSeverityEl) largestSeverityEl.textContent = String(largestSev);
  if (largestRiskScoreEl) largestRiskScoreEl.textContent = String(largestRisk);

  // Explanation list
  if (explainWrap) {
    explainWrap.innerHTML = "";
    const list = anomalies
      .filter((a) => a && a.reason)
      .slice(0, 6);

    if (!list.length) {
      if (explainEmpty) explainEmpty.style.display = "block";
    } else {
      if (explainEmpty) explainEmpty.style.display = "none";
      list.forEach((a) => {
        const el = document.createElement("div");
        el.className = "card-glass p-3";
        el.innerHTML = `
          <div style="font-weight:900; margin-bottom:6px;">
            <i class="fa-solid fa-circle-info me-2" style="color:${severityToColor(a.severity)}"></i>
            ${a.category ?? "Expense"}
          </div>
          <div class="small-muted">Amount: <b>${WiseMoneyAPI.formatINR(a.amount ?? 0)}</b></div>
          <div class="small-muted">Risk Score: <b>${a.risk_score ?? "—"}</b></div>
          <div class="small-muted mt-2">Reason: <b>${a.reason ?? "—"}</b></div>
        `;
        explainWrap.appendChild(el);
      });
    }
  }

  // Severity trend visualization (counts by severity)
  const highCount = anomalies.filter((a) => String(a.severity).toLowerCase().includes("high")).length;
  const medCount = anomalies.filter((a) => String(a.severity).toLowerCase().includes("medium")).length;
  const lowCount = anomalies.filter((a) => String(a.severity).toLowerCase().includes("low")).length;

  const chartEl = document.getElementById("anomRiskChart");
  destroyIfAny("anomRiskChart");
  if (chartEl) {
    __anomCharts.anomRiskChart = buildChart(chartEl, {
      type: "bar",
      data: {
        labels: ["High", "Medium", "Low"],
        datasets: [
          {
            label: "Anomalies",
            data: [highCount, medCount, lowCount],
            backgroundColor: [
              "rgba(255,77,109,.65)",
              "rgba(255,176,32,.55)",
              "rgba(46,229,157,.45)",
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
        scales: {
          x: { ticks: { color: "rgba(255,255,255,.65)" }, grid: { color: "rgba(255,255,255,.06)" } },
          y: { ticks: { color: "rgba(255,255,255,.65)" }, grid: { color: "rgba(255,255,255,.06)" }, beginAtZero: true },
        },
      },
    });
  }
}

window.addEventListener("DOMContentLoaded", initAnomalyPage);

