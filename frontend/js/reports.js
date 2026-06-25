function downloadText(filename, text, mime) {
  const blob = new Blob([text], { type: mime || "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function csvEscape(v) {
  const s = String(v ?? "");
  if (s.includes(",") || s.includes("\n") || s.includes('"')) {
    return '"' + s.replace(/"/g, '""') + '"';
  }
  return s;
}

function toCSV(rows, headers) {
  const lines = [];
  lines.push(headers.map(csvEscape).join(","));
  rows.forEach((r) => {
    lines.push(headers.map((h) => csvEscape(r[h])).join(","));
  });
  return lines.join("\n");
}

async function initReportsPage() {
  WiseMoneyAuth.requireAuth();

  let [summary, trend, forecast] = await Promise.all([
    WiseMoneyAPI.apiGet("/report/summary"),
    WiseMoneyAPI.apiGet("/report/trend"),
    WiseMoneyAPI.apiGet("/report/forecast?days=30"),
  ]);

  // Keep backward compatibility with older keys (if any)
  summary = summary || {};


  // Summary
  const incomeEl = document.getElementById("reportIncome");
  const expenseEl = document.getElementById("reportExpense");
  const walletEl = document.getElementById("reportWallet");
  const netEl = document.getElementById("reportNet");
  if (incomeEl) incomeEl.textContent = WiseMoneyAPI.formatINR(summary.total_income || 0);
  if (expenseEl) expenseEl.textContent = WiseMoneyAPI.formatINR(summary.total_expense || 0);
  if (walletEl) walletEl.textContent = WiseMoneyAPI.formatINR(summary.wallet_balance || 0);
  if (netEl) netEl.textContent = WiseMoneyAPI.formatINR(summary.net_savings || 0);


  // Trend chart
  const trendCanvas = document.getElementById("trendChart");
  if (trendCanvas && trend?.length) {
    new Chart(trendCanvas.getContext("2d"), {
      type: "line",
      data: {
        labels: trend.map((x) => x.month),
        datasets: [
          {
            label: "Income",
            data: trend.map((x) => x.income),
            borderColor: "rgba(124,77,255,1)",
            backgroundColor: "rgba(124,77,255,.12)",
            fill: true,
            tension: 0.35,
          },
          {
            label: "Expense",
            data: trend.map((x) => x.expense),
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
        plugins: { legend: { labels: { color: "rgba(255,255,255,.75)" } } },
        scales: {
          x: { ticks: { color: "rgba(255,255,255,.65)" }, grid: { color: "rgba(255,255,255,.06)" } },
          y: { ticks: { color: "rgba(255,255,255,.65)" }, grid: { color: "rgba(255,255,255,.06)" } },
        },
      },
    });
  }

  // Forecast chart
  const forecastCanvas = document.getElementById("forecastChart");
  const forecastData = forecast?.forecast || [];
  if (forecastCanvas && forecastData.length) {
    new Chart(forecastCanvas.getContext("2d"), {
      type: "bar",
      data: {
        labels: forecastData.slice(-14).map((x) => x.date),
        datasets: [
          {
            label: "Forecasted Expense",
            data: forecastData.slice(-14).map((x) => x.predicted_amount),
            backgroundColor: "rgba(124,77,255,.55)",
            borderColor: "rgba(124,77,255,1)",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: "rgba(255,255,255,.75)" } } },
        scales: {
          x: { ticks: { color: "rgba(255,255,255,.65)" }, grid: { color: "rgba(255,255,255,.06)" } },
          y: { ticks: { color: "rgba(255,255,255,.65)" }, grid: { color: "rgba(255,255,255,.06)" } },
        },
      },
    });
  }

  // Export
  const exportBtn = document.getElementById("exportBtn");
  const exportPreview = document.getElementById("exportPreview");
  if (exportBtn) {
    exportBtn.addEventListener("click", async () => {
      const rows = await WiseMoneyAPI.apiGet("/report/export");
      const safeRows = Array.isArray(rows) ? rows : [];

      if (exportPreview) {
        exportPreview.innerHTML = safeRows
          .slice(0, 8)
          .map((r) => `<div class="small-muted">${r.date} — ${r.type}: ${r.category} — ${WiseMoneyAPI.formatINR(r.amount)}</div>`)
          .join("");
      }

      const headers = ["date", "type", "category", "amount"];
      const csv = toCSV(safeRows, headers);
      downloadText("wisemoney_report.csv", csv, "text/csv");
    });
  }
}

window.addEventListener("DOMContentLoaded", initReportsPage);

