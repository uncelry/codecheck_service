const API_BASE = "http://localhost:8000"; // внутри docker-compose сети

function saveTokens(access, refresh) {
    localStorage.setItem("access", access);
    localStorage.setItem("refresh", refresh);
}

function getAccess() {
    return localStorage.getItem("access");
}

async function api(path, method = "GET", body = null, isForm = false, needs_token = true) {
    const headers = {};

    if (!isForm) headers["Content-Type"] = "application/json";

    if (needs_token) {
        const token = getAccess();
        if (token) headers["Authorization"] = "Bearer " + token;
    }

    const resp = await fetch(API_BASE + path, {
        method,
        headers,
        body: isForm ? body : body ? JSON.stringify(body) : null
    });

    return resp.json();
}
