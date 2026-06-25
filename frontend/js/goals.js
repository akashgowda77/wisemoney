/* ==========================================================
   WiseMoney Goals Module
   Part 2A
   Initialization + Loading Data
   ========================================================== */

// ----------------------------------------------------------
// Helper
// ----------------------------------------------------------

function qs(id) {
    return document.getElementById(id);
}

// ----------------------------------------------------------
// Global State
// ----------------------------------------------------------

const state = {
    goals: [],
    wallets: [],
    selectedGoal: null
};

// ----------------------------------------------------------
// Bootstrap Modals
// ----------------------------------------------------------

let progressModal;
let fundModal;
let deleteModal;

// ----------------------------------------------------------
// Initialize Page
// ----------------------------------------------------------

async function initializeGoalsPage() {

    // User must be logged in
    WiseMoneyAuth.requireAuth();

    // Bootstrap modals
    progressModal = qs("progressModal")
        ? new bootstrap.Modal(qs("progressModal"))
        : null;

    fundModal = qs("fundGoalModal")
        ? new bootstrap.Modal(qs("fundGoalModal"))
        : null;

    deleteModal = qs("deleteGoalModal")
        ? new bootstrap.Modal(qs("deleteGoalModal"))
        : null;

    // Load initial data
    await loadWallets();

    await loadGoals();

    registerEvents();
}

// ----------------------------------------------------------
// Load Wallets
// ----------------------------------------------------------

async function loadWallets() {

    try {

        state.wallets =
            await WiseMoneyAPI.apiGet("/wallet/") || [];

        const walletDropdown =
            qs("fundWallet");

        walletDropdown.innerHTML = "";

        if (!state.wallets.length) {

            walletDropdown.innerHTML = `
                <option value="">
                    No Wallet Available
                </option>
            `;

            return;
        }

        state.wallets.forEach(wallet => {

            walletDropdown.innerHTML += `

                <option value="${wallet.id}">

                    ${wallet.name}
                    (₹${wallet.balance.toLocaleString()})

                </option>

            `;

        });

    }

    catch (err) {

        console.error(err);

        alert("Unable to load wallets.");

    }

}

// ----------------------------------------------------------
// Load Goals
// ----------------------------------------------------------

async function loadGoals() {

    try {

        state.goals =
            await WiseMoneyAPI.apiGet("/goals/") || [];

        renderGoals();

        updateStatistics();

    }

    catch (err) {

        console.error(err);

        alert("Unable to load goals.");

    }

}

// ----------------------------------------------------------
// Update Dashboard Statistics
// ----------------------------------------------------------

function updateStatistics() {

    const totalGoals =
        state.goals.length;

    const activeGoals =
        state.goals.filter(
            g => g.status === "active"
        ).length;

    const completedGoals =
        state.goals.filter(
            g => g.status === "achieved"
        ).length;

    let progress = 0;

    if (totalGoals > 0) {

        progress =
            state.goals.reduce((sum, goal) => {

                return sum +
                    (
                        goal.current_savings /
                        goal.target_amount
                    ) * 100;

            }, 0) / totalGoals;

    }

    qs("totalGoals").textContent =
        totalGoals;

    qs("activeGoals").textContent =
        activeGoals;

    qs("completedGoals").textContent =
        completedGoals;

    qs("overallProgress").textContent =
        `${progress.toFixed(1)}%`;

    qs("goalCountBadge").textContent =
        `${totalGoals} Goal${totalGoals !== 1 ? "s" : ""}`;

}
// ----------------------------------------------------------
// Render Goals Table
// ----------------------------------------------------------

function renderGoals() {

    const tableBody = qs("goalsTableBody");
    const emptyState = qs("emptyGoals");

    tableBody.innerHTML = "";

    if (state.goals.length === 0) {

        emptyState.style.display = "block";

        return;
    }

    emptyState.style.display = "none";

    state.goals.forEach(goal => {

        // Calculate progress
        const progress =
            Math.min(
                (
                    goal.current_savings /
                    goal.target_amount
                ) * 100,
                100
            );

        // Status badge
        let statusBadge = `
            <span class="badge bg-success">
                Achieved
            </span>
        `;

        if (goal.status === "active") {

            statusBadge = `
                <span class="badge bg-warning text-dark">
                    Active
                </span>
            `;

        }

        // Priority badge
        let priorityBadge = `
            <span class="badge bg-secondary">
                Medium
            </span>
        `;

        if (goal.priority === "high") {

            priorityBadge = `
                <span class="badge bg-danger">
                    High
                </span>
            `;

        }

        else if (goal.priority === "low") {

            priorityBadge = `
                <span class="badge bg-info text-dark">
                    Low
                </span>
            `;

        }

        tableBody.innerHTML += `

        <tr>

            <td>

                <strong>

                    ${goal.goal_name}

                </strong>

            </td>

            <td>

                ${WiseMoneyAPI.formatINR(goal.target_amount)}

            </td>

            <td>

                ${WiseMoneyAPI.formatINR(goal.current_savings)}

            </td>

            <td style="min-width:180px;">

                <div
                    class="progress"
                    style="
                        height:12px;
                        background:#202B3D;
                    ">

                    <div
                        class="progress-bar
                               bg-success"

                        role="progressbar"

                        style="width:${progress}%">

                    </div>

                </div>

                <small>

                    ${progress.toFixed(1)}%

                </small>

            </td>

            <td>

                ${statusBadge}

            </td>

            <td>

                ${priorityBadge}

            </td>

            <td>

                <div class="d-flex gap-2 flex-wrap">

                    <button
                        class="btn btn-sm btn-primary viewGoalBtn"
                        data-id="${goal.id}">

                        <i class="fa-solid fa-chart-line"></i>

                    </button>

                    <button
                        class="btn btn-sm btn-success fundGoalBtn"
                        data-id="${goal.id}">

                        <i class="fa-solid fa-money-bill-wave"></i>

                    </button>

                    <button
                        class="btn btn-sm btn-danger deleteGoalBtn"
                        data-id="${goal.id}">

                        <i class="fa-solid fa-trash"></i>

                    </button>

                </div>

            </td>

        </tr>

        `;

    });

}
// ----------------------------------------------------------
// Create Goal
// ----------------------------------------------------------

async function createGoal(event) {

    event.preventDefault();

    const payload = {

        goal_name: qs("goalName").value.trim(),

        target_amount: Number(
            qs("targetAmount").value
        ),

        current_savings: Number(
            qs("currentSavings").value || 0
        ),

        priority: qs("goalPriority").value,

        notes: qs("goalNotes").value.trim()

    };

    if (!payload.goal_name) {

        alert("Goal name is required.");

        return;

    }

    if (payload.target_amount <= 0) {

        alert("Target amount must be greater than zero.");

        return;

    }

    try {

        await WiseMoneyAPI.apiPost(
            "/goals/",
            payload
        );

        qs("createGoalForm").reset();

        qs("currentSavings").value = 0;

        await loadGoals();

        alert("Goal created successfully.");

    }

    catch (err) {

        console.error(err);

        alert("Unable to create goal.");

    }

}

// ----------------------------------------------------------
// View Goal Progress
// ----------------------------------------------------------

async function viewGoal(goalId) {

    try {

        const goal =
            await WiseMoneyAPI.apiGet(
                `/goals/${goalId}`
            );

        qs("progressTitle").textContent =
            goal.goal_name;

        const remaining =
            goal.target_amount -
            goal.current_savings;

        qs("progressBody").innerHTML = `

            <div class="mb-3">

                <strong>Goal Status</strong>

                <div class="mt-1">

                    ${goal.status}

                </div>

            </div>

            <div class="mb-3">

                <strong>Priority</strong>

                <div class="mt-1">

                    ${goal.priority}

                </div>

            </div>

            <div class="mb-3">

                <strong>Target Amount</strong>

                <div class="mt-1">

                    ${WiseMoneyAPI.formatINR(goal.target_amount)}

                </div>

            </div>

            <div class="mb-3">

                <strong>Current Savings</strong>

                <div class="mt-1">

                    ${WiseMoneyAPI.formatINR(goal.current_savings)}

                </div>

            </div>

            <div class="mb-3">

                <strong>Remaining Amount</strong>

                <div class="mt-1">

                    ${WiseMoneyAPI.formatINR(remaining)}

                </div>

            </div>

            <div class="progress mt-4"
                 style="height:18px;">

                <div
                    class="progress-bar bg-success"
                    style="width:${goal.progress_percentage}%">

                    ${goal.progress_percentage}%

                </div>

            </div>

        `;

        progressModal.show();

    }

    catch (err) {

        console.error(err);

        alert("Unable to load goal progress.");

    }

}

// ----------------------------------------------------------
// Open Fund Goal Modal
// ----------------------------------------------------------

function openFundModal(goalId) {

    qs("fundGoalId").value =
        goalId;

    qs("fundAmount").value = "";

    fundModal.show();

}

// ----------------------------------------------------------
// Fund Goal
// ----------------------------------------------------------

async function fundGoal() {

    const goalId =
        qs("fundGoalId").value;

    const payload = {

        wallet_id: Number(
            qs("fundWallet").value
        ),

        amount: Number(
            qs("fundAmount").value
        )

    };

    if (!payload.wallet_id) {

        alert("Select a wallet.");

        return;

    }

    if (payload.amount <= 0) {

        alert("Enter a valid amount.");

        return;

    }

    try {

        await WiseMoneyAPI.apiPost(

            `/goals/${goalId}/fund`,

            payload

        );

        fundModal.hide();

        await loadWallets();

        await loadGoals();

        alert("Goal funded successfully.");

    }

    catch (err) {

        console.error(err);

        alert("Funding failed.");

    }

}
// ----------------------------------------------------------
// Delete Goal
// ----------------------------------------------------------

function openDeleteModal(goalId) {

    qs("deleteGoalId").value = goalId;

    deleteModal.show();

}

async function deleteGoal() {

    const goalId = qs("deleteGoalId").value;

    if (!goalId) return;

    try {

        await WiseMoneyAPI.apiDelete(
            `/goals/${goalId}`
        );

        deleteModal.hide();

        await loadGoals();

        alert("Goal deleted successfully.");

    }

    catch (err) {

        console.error(err);

        alert("Unable to delete goal.");

    }

}

// ----------------------------------------------------------
// Register Events
// ----------------------------------------------------------

function registerEvents() {

    // ------------------------------------------
    // Create Goal
    // ------------------------------------------

    qs("createGoalForm").addEventListener(
        "submit",
        createGoal
    );

    // ------------------------------------------
    // Fund Goal
    // ------------------------------------------

    qs("confirmFundBtn").addEventListener(
        "click",
        fundGoal
    );

    // ------------------------------------------
    // Delete Goal
    // ------------------------------------------

    qs("confirmDeleteBtn").addEventListener(
        "click",
        deleteGoal
    );

    // ------------------------------------------
    // Table Buttons
    // ------------------------------------------

    qs("goalsTableBody").addEventListener(
        "click",
        async function (event) {

            const button =
                event.target.closest("button");

            if (!button) return;

            const goalId =
                button.dataset.id;

            if (!goalId) return;

            // View Progress
            if (
                button.classList.contains(
                    "viewGoalBtn"
                )
            ) {

                await viewGoal(goalId);

                return;

            }

            // Fund Goal
            if (
                button.classList.contains(
                    "fundGoalBtn"
                )
            ) {

                openFundModal(goalId);

                return;

            }

            // Delete Goal
            if (
                button.classList.contains(
                    "deleteGoalBtn"
                )
            ) {

                openDeleteModal(goalId);

                return;

            }

        }
    );

}

// ----------------------------------------------------------
// Logout Button
// ----------------------------------------------------------

const logoutButton = qs("logoutBtn");

if (logoutButton) {

    logoutButton.addEventListener(

        "click",

        () => {

            localStorage.removeItem("token");

            window.location.href = "login.html";

        }

    );

}

// ----------------------------------------------------------
// Page Initialization
// ----------------------------------------------------------

window.addEventListener(

    "DOMContentLoaded",

    initializeGoalsPage

);
