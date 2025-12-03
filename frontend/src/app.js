const API_BASE = "http://localhost:8000"; // внутри docker-compose сети

function saveTokens(access, refresh) {
    localStorage.setItem("access", access);
    localStorage.setItem("refresh", refresh);
}

function getAccess() {
    return localStorage.getItem("access");
}

function getRefresh() {
    return localStorage.getItem("refresh");
}

async function refreshToken() {
    const refresh = getRefresh();
    if (!refresh) return false;

    const resp = await fetch(API_BASE + "/api/users/refresh/", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({refresh})
    });

    if (!resp.ok) return false;

    const data = await resp.json();

    if (data.access) {
        saveTokens(data.access, refresh);   // refresh остаётся прежним
        return true;
    }

    return false;
}

async function api(path, method = "GET", body = null, isForm = false, needs_token = true) {
    const headers = {};

    if (!isForm) headers["Content-Type"] = "application/json";

    if (needs_token) {
        const token = getAccess();
        if (token) headers["Authorization"] = "Bearer " + token;
    }

    let resp = await fetch(API_BASE + path, {
        method,
        headers,
        body: isForm ? body : body ? JSON.stringify(body) : null
    });

    // Если токен протух
    if (resp.status === 401 || resp.status === 403) {
        const data = await resp.json().catch(() => null);

        if (!data || !data.code || data.code !== "token_not_valid") {
            window.location = "/login.html";
            return;
        }

        if (data && data.code === "token_not_valid") {
            const ok = await refreshToken();

            if (!ok) {
                window.location = "/login.html";
                return;
            }

            // повторяем запрос с новым токеном
            const newHeaders = {...headers, Authorization: "Bearer " + getAccess()};

            resp = await fetch(API_BASE + path, {
                method,
                headers: newHeaders,
                body: isForm ? body : body ? JSON.stringify(body) : null
            });
        }
    }

    return resp.json();
}
