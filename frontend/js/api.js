// WiseMoney API Layer
// - Centralizes base URL
// - Automatically attaches JWT Authorization header

const API_BASE = "http://127.0.0.1:8000";

function isNumLike(v) {
  return v !== null && v !== undefined && v !== "" && !Number.isNaN(Number(v));
}

function safeProgressPct(pct) {
  if (!isNumLike(pct)) return 0;
  return Math.max(0, Math.min(100, Number(pct)));
}


function getToken() {
  return localStorage.getItem("token");
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handleResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  let data;

  if (contentType.includes("application/json")) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    const detail = data && data.detail ? data.detail : response.statusText;
    const err = new Error(`API Error: ${response.status} - ${detail}`);
    err.status = response.status;
    err.data = data;
    throw err;
  }

  return data;
}

async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;

  const headers = {
    ...authHeaders(),
    ...(options.headers || {}),
  };

  if (options.body !== undefined && options.body !== null) {
    if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }
  }

  const response = await fetch(url, {
    ...options,
    headers,
    body: options.body,
  });

  return handleResponse(response);
}

function buildJsonBody(payload) {
  if (payload === undefined) return undefined;
  return JSON.stringify(payload);
}

function formatINR(value) {
  const num = Number(value || 0);
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(num);
}

window.WiseMoneyAPI = {

  API_BASE,

  apiGet: (endpoint) =>
    apiRequest(endpoint, {
      method: "GET"
    }),

  apiPost: (endpoint, payload) =>
    apiRequest(endpoint, {
      method: "POST",
      body: buildJsonBody(payload)
    }),

  apiPut: (endpoint, payload) =>
    apiRequest(endpoint, {
      method: "PUT",
      body: buildJsonBody(payload)
    }),

  apiDelete: (endpoint) =>
    apiRequest(endpoint, {
      method: "DELETE"
    }),

  formatINR,

  safeProgressPct

};

