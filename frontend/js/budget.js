// =====================================================
// WiseMoney Budget Module
// Part 1 - Initialization & API
// =====================================================

WiseMoneyAuth.requireAuth();

const $ = (id) => document.getElementById(id);

// -----------------------------------------------------
// Global State
// -----------------------------------------------------

const state = {

    budgets: [],

    summary: null,

    health: null,

    recommendation: null,

    breaches: []

};

// -----------------------------------------------------
// Bootstrap Modal
// -----------------------------------------------------

let editModal;

// -----------------------------------------------------
// Helpers
// -----------------------------------------------------

function formatMoney(value) {

    return WiseMoneyAPI.formatINR(Number(value || 0));

}

function safePercent(value) {

    value = Number(value || 0);

    if (value < 0) return 0;

    if (value > 100) return 100;

    return value;

}

function clearTable() {

    $("budgetTableBody").innerHTML = "";

}

function createCell(text) {

    const td = document.createElement("td");

    td.textContent = text;

    return td;

}

// -----------------------------------------------------
// API Calls
// -----------------------------------------------------

async function fetchBudgets() {

    state.budgets = await WiseMoneyAPI.apiGet("/budget/");

}

async function fetchSummary() {

    state.summary = await WiseMoneyAPI.apiGet("/budget/summary");

}

async function fetchHealth() {

    state.health = await WiseMoneyAPI.apiGet("/budget/health");

}

async function fetchRecommendation() {

    state.recommendation =
        await WiseMoneyAPI.apiGet("/budget/recommendation");

}

async function fetchBreaches() {

    state.breaches =
        await WiseMoneyAPI.apiGet("/budget/breaches");

}

// -----------------------------------------------------
// Load Entire Budget Module
// -----------------------------------------------------

async function loadBudgetModule() {

    try {

        await Promise.all([

            fetchBudgets(),

            fetchSummary(),

            fetchHealth(),

            fetchRecommendation(),

            fetchBreaches()

        ]);

        renderSummary();

        renderHealth();

        renderRecommendations();

        renderBreaches();

        renderBudgetTable();

    }

    catch(err){

        console.error(err);

        alert("Unable to load Budget data.");

    }

}

// -----------------------------------------------------
// Initialize
// -----------------------------------------------------

window.addEventListener("DOMContentLoaded", () => {

    editModal = new bootstrap.Modal(
        document.getElementById("editBudgetModal")
    );

    $("budgetForm").addEventListener(
        "submit",
        createBudget
    );

    $("saveBudgetBtn").addEventListener(
        "click",
        updateBudget
    );

    loadBudgetModule();

});
// =====================================================
// Render Summary Cards
// =====================================================

function renderSummary() {

    if (!state.summary) return;

    $("totalBudget").textContent =
        formatMoney(state.summary.total_budget);

    $("totalSpent").textContent =
        formatMoney(state.summary.total_spent);

    $("remainingBudget").textContent =
        formatMoney(state.summary.remaining_budget);

    $("utilization").textContent =
        `${Number(state.summary.utilization_percentage || 0).toFixed(1)} %`;
}


// =====================================================
// Render Budget Health
// =====================================================

function renderHealth() {

    if (!state.health) return;

    $("healthScore").textContent =
        state.health.budget_health_score;

    $("healthStatus").textContent =
        state.health.status;

    $("totalCategories").textContent =
        state.health.total_categories;

    $("breachedCategories").textContent =
        state.health.breached_categories;

}


// =====================================================
// Render Recommendations
// =====================================================

function renderRecommendations() {

    const container =
        $("recommendationContainer");

    container.innerHTML = "";

    const recommendations =
        state.recommendation.recommended_budget;

    if (!recommendations ||
        Object.keys(recommendations).length === 0) {

        container.innerHTML = `

            <p class="small-muted">

                No recommendations available.

            </p>

        `;

        return;

    }

    Object.entries(recommendations).forEach(([category, item]) => {

        container.innerHTML += `

        <div class="mb-3 p-2 border rounded">

            <strong>${category}</strong>

            <br>

            Current :
            ${formatMoney(item.current_spending)}

            <br>

            Recommended :
            ${formatMoney(item.recommended_budget)}

            <br>

            Risk :

            <span class="badge bg-warning">

                ${item.risk_level}

            </span>

        </div>

        `;

    });

}



// =====================================================
// Render Budget Breaches
// =====================================================

function renderBreaches() {

    const container =
        $("breachContainer");

    container.innerHTML = "";

    if (!state.breaches ||
        state.breaches.length === 0) {

        container.innerHTML = `

        <p class="small-muted">

            No budget breaches 🎉

        </p>

        `;

        return;

    }

    state.breaches.forEach(item => {

        container.innerHTML += `

        <div class="alert alert-danger p-2 mb-2">

            <strong>

                ${item.category}

            </strong>

            exceeded by

            ${formatMoney(item.exceeded_by)}

        </div>

        `;

    });

}
// =====================================================
// Render Budget Table
// =====================================================

function renderBudgetTable() {

    const tbody = $("budgetTableBody");

    tbody.innerHTML = "";

    if (!state.budgets || state.budgets.length === 0) {

        tbody.innerHTML = `

            <tr>

                <td colspan="6" class="text-center text-secondary">

                    No budgets available

                </td>

            </tr>

        `;

        return;

    }

    state.budgets.forEach((budget) => {

        const progress = safePercent(
            budget.utilization_percentage
        );

        const row = document.createElement("tr");

        row.innerHTML = `

            <td>
                <strong>${budget.category}</strong>
            </td>

            <td>
                ${formatMoney(budget.monthly_limit)}
            </td>

            <td>
                ${formatMoney(budget.current_spend)}
            </td>

            <td>
                ${formatMoney(budget.remaining_budget)}
            </td>

            <td style="min-width:180px;">

                <div class="progress" style="height:10px;">

                    <div
                        class="progress-bar bg-success"
                        role="progressbar"
                        style="width:${progress}%"
                        aria-valuenow="${progress}"
                        aria-valuemin="0"
                        aria-valuemax="100">
                    </div>

                </div>

                <small>

                    ${progress.toFixed(1)}%

                </small>

            </td>

            <td>

                <button
                    class="btn btn-sm btn-warning edit-btn me-2"
                    data-id="${budget.id}"
                    data-category="${budget.category}"
                    data-limit="${budget.monthly_limit}">

                    <i class="fa-solid fa-pen"></i>

                </button>

                <button
                    class="btn btn-sm btn-danger delete-btn"
                    data-id="${budget.id}">

                    <i class="fa-solid fa-trash"></i>

                </button>

            </td>

        `;

        tbody.appendChild(row);

    });

    // Activate Edit/Delete buttons
    attachTableEvents();

}

// =====================================================
// Create Budget
// =====================================================

async function createBudget(event) {

    event.preventDefault();

    const category =
        $("category").value.trim();

    const monthlyLimit =
        Number($("monthlyLimit").value);

    if (!category) {

        alert("Please enter budget category.");

        return;

    }

    if (!monthlyLimit || monthlyLimit <= 0) {

        alert("Monthly limit must be greater than 0.");

        return;

    }

    try {

        await WiseMoneyAPI.apiPost(

            "/budget/",

            {

                category: category,

                monthly_limit: monthlyLimit

            }

        );

        // Clear form

        $("category").value = "";

        $("monthlyLimit").value = "";

        // Reload everything

        await loadBudgetModule();

        alert("Budget created successfully.");

    }

    catch(err){

        console.error(err);

        if(err.data && err.data.detail){

            alert(err.data.detail);

        }

        else{

            alert("Unable to create budget.");

        }

    }

}

// =====================================================
// Edit Budget
// =====================================================

function attachTableEvents() {

    // -----------------------------
    // Edit Button
    // -----------------------------

    document.querySelectorAll(".edit-btn").forEach(button => {

        button.onclick = () => {

            $("editBudgetId").value =
                button.dataset.id;

            $("editCategory").value =
                button.dataset.category;

            $("editLimit").value =
                button.dataset.limit;

            editModal.show();

        };

    });

    // -----------------------------
    // Delete Button
    // -----------------------------

    document.querySelectorAll(".delete-btn").forEach(button => {

        button.onclick = async () => {

            if (!confirm("Delete this budget?"))
                return;

            try {

                await WiseMoneyAPI.apiDelete(

                    `/budget/${button.dataset.id}`

                );

                await loadBudgetModule();

                alert("Budget deleted successfully.");

            }

            catch (err) {

                console.error(err);

                alert("Unable to delete budget.");

            }

        };

    });

}


// =====================================================
// Save Edited Budget
// =====================================================

async function updateBudget() {

    const id =
        $("editBudgetId").value;

    const category =
        $("editCategory").value.trim();

    const monthly_limit =
        Number($("editLimit").value);

    if (!category) {

        alert("Category cannot be empty.");

        return;

    }

    if (monthly_limit <= 0) {

        alert("Monthly limit must be greater than zero.");

        return;

    }

    try {

        await WiseMoneyAPI.apiPut(

            `/budget/${id}`,

            {

                category,

                monthly_limit

            }

        );

        editModal.hide();

        await loadBudgetModule();

        alert("Budget updated successfully.");

    }

    catch(err){

        console.error(err);

        if(err.data && err.data.detail){

            alert(err.data.detail);

        }

        else{

            alert("Unable to update budget.");

        }

    }

}