// WiseMoney Auth Logic (JWT + UI behavior)
// - login/register do NOT require auth header
// - protected pages must call requireAuth()

// If api.js already defines API_BASE, reuse it to avoid redeclare errors.
// (Some pages may load api.js before auth.js.)
const AUTH_API_BASE = window.API_BASE || "http://127.0.0.1:8000";


function getToken() {
  return localStorage.getItem("token");
}

function setToken(token) {
  localStorage.setItem("token", token);
}

function clearToken() {
  localStorage.removeItem("token");
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = "login.html";
  }
}

async function loginUser(email, password) {
  // Backend uses OAuth2PasswordRequestForm: fields are `username` + `password`
  // where `username` is treated as the user's email.
  const formData = new FormData();
  formData.append("username", email);
  formData.append("password", password);

  const response = await fetch(`${AUTH_API_BASE}/auth/login`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || `Login failed (${response.status})`);
  }

  if (!data.access_token) throw new Error("Missing access_token in login response");
  setToken(data.access_token);
  return data;
}

async function registerUser(name, email, password) {
  const payload = { name, email, password };

  const response = await fetch(`${AUTH_API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || `Registration failed (${response.status})`);
  }

  return data;
}

// Wire login page
const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const submitBtn = loginForm.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;

    try {
      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;

      // Debug
      console.log("Login attempt", { email });

      const data = await loginUser(email, password);
      console.log("Login success", data);

      window.location.href = "dashboard.html";
    } catch (err) {
      console.error("Login failed", err);
      const loginError = document.getElementById("loginError");
      if (loginError) {
        loginError.style.display = "block";
        loginError.textContent = err.message || String(err);
      }
      alert(err.message || String(err));
    } finally {

      if (submitBtn) submitBtn.disabled = false;
    }
  });
}

// Wire register page
const registerForm = document.getElementById("registerForm");
if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const submitBtn = registerForm.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;

    try {
      const name = document.getElementById("name").value;
      const email = document.getElementById("regEmail").value;
      const password = document.getElementById("regPassword").value;

      await registerUser(name, email, password);
      alert("Registration Successful");
      window.location.href = "login.html";
    } catch (err) {
      alert(err.message || String(err));
    } finally {
      if (submitBtn) submitBtn.disabled = false;
    }
  });
}

// Wire logout button (dashboard/other pages)
const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
  logoutBtn.addEventListener("click", () => {
    clearToken();
    window.location.href = "login.html";
  });
}

window.WiseMoneyAuth = {
  requireAuth,
  getToken,
  clearToken,
};

