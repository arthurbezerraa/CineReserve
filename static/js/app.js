const ACCESS_TOKEN_KEY = "cine_reserve_access";
const REFRESH_TOKEN_KEY = "cine_reserve_refresh";

function getPage() {
    return document.body.dataset.page;
}

function setFeedback(elementId, message, type = "") {
    const element = document.getElementById(elementId);
    if (!element) {
        return;
    }

    element.textContent = message || "";
    element.className = "feedback";

    if (type) {
        element.classList.add(`is-${type}`);
    }
}

function normalizeErrors(payload) {
    if (!payload) {
        return "Não foi possível concluir a ação.";
    }

    if (typeof payload.detail === "string") {
        return payload.detail;
    }

    const messages = [];

    Object.entries(payload).forEach(([field, value]) => {
        if (Array.isArray(value)) {
            messages.push(`${field}: ${value.join(" ")}`);
        } else if (typeof value === "string") {
            messages.push(`${field}: ${value}`);
        }
    });

    return messages.join(" ") || "Não foi possível concluir a ação.";
}

function saveTokens(access, refresh) {
    localStorage.setItem(ACCESS_TOKEN_KEY, access);
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
}

function clearTokens() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
}

function getAccessToken() {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
}

function hasSession() {
    return Boolean(getAccessToken());
}

async function request(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    });

    let payload = null;

    try {
        payload = await response.json();
    } catch (error) {
        payload = null;
    }

    if (!response.ok) {
        throw new Error(normalizeErrors(payload));
    }

    return payload;
}

function bindLoginForm() {
    const form = document.getElementById("login-form");
    if (!form) {
        return;
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        setFeedback("login-feedback", "Autenticando...");

        const formData = new FormData(form);
        const body = JSON.stringify({
            username: formData.get("username"),
            password: formData.get("password"),
        });

        try {
            const payload = await request("/api/auth/login/", {
                method: "POST",
                body,
            });

            saveTokens(payload.access, payload.refresh);
            setFeedback("login-feedback", "Login realizado com sucesso. Redirecionando...", "success");
            window.location.href = "/movies/";
        } catch (error) {
            setFeedback("login-feedback", error.message, "error");
        }
    });
}

function bindRegisterForm() {
    const form = document.getElementById("register-form");
    if (!form) {
        return;
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        setFeedback("register-feedback", "Criando conta...");

        const formData = new FormData(form);
        const body = JSON.stringify({
            username: formData.get("username"),
            email: formData.get("email"),
            password: formData.get("password"),
        });

        try {
            await request("/api/auth/register/", {
                method: "POST",
                body,
            });

            setFeedback("register-feedback", "Conta criada com sucesso. Faça login para continuar.", "success");
            form.reset();
        } catch (error) {
            setFeedback("register-feedback", error.message, "error");
        }
    });
}

function formatDate(dateString) {
    if (!dateString) {
        return "Data indisponível";
    }

    return new Intl.DateTimeFormat("pt-BR", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    }).format(new Date(dateString));
}

function renderMovies(movies) {
    const grid = document.getElementById("movies-grid");
    if (!grid) {
        return;
    }

    if (!movies.length) {
        grid.innerHTML = '<div class="empty-state">Nenhum filme ativo foi encontrado no momento.</div>';
        return;
    }

    grid.innerHTML = movies
        .map(
            (movie) => `
                <article class="movie-card">
                    <span class="movie-tag">${movie.genre}</span>
                    <h3>${movie.title}</h3>
                    <div class="movie-meta">
                        <span>Lançamento: ${formatDate(movie.release_date)}</span>
                        <span>ID: ${movie.id}</span>
                    </div>
                    <p class="movie-description">${movie.description}</p>
                </article>
            `
        )
        .join("");
}

async function loadMovies() {
    setFeedback("movies-feedback", "Carregando filmes...");

    try {
        const payload = await request("/api/movies/");
        const movies = Array.isArray(payload) ? payload : payload.results || [];
        renderMovies(movies);
        setFeedback("movies-feedback", `${movies.length} filme(s) carregado(s).`, "success");
    } catch (error) {
        setFeedback("movies-feedback", error.message, "error");
    }
}

function bindMoviesPage() {
    const sessionIndicator = document.getElementById("session-indicator");
    const reloadButton = document.getElementById("reload-movies");
    const logoutButton = document.getElementById("logout-button");

    if (!sessionIndicator) {
        return;
    }

    if (!hasSession()) {
        window.location.href = "/login/";
        return;
    }

    sessionIndicator.textContent = "Sessão JWT armazenada no navegador";
    loadMovies();

    reloadButton?.addEventListener("click", loadMovies);
    logoutButton?.addEventListener("click", () => {
        clearTokens();
        window.location.href = "/login/";
    });
}

function init() {
    const page = getPage();

    if (page === "login") {
        bindLoginForm();
    }

    if (page === "register") {
        bindRegisterForm();
    }

    if (page === "movies") {
        bindMoviesPage();
    }
}

document.addEventListener("DOMContentLoaded", init);
