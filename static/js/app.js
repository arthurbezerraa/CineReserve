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
        return "Nao foi possivel concluir a acao.";
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

    return messages.join(" ") || "Nao foi possivel concluir a acao.";
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

            setFeedback("register-feedback", "Conta criada com sucesso. Faca login para continuar.", "success");
            form.reset();
        } catch (error) {
            setFeedback("register-feedback", error.message, "error");
        }
    });
}

function formatDate(dateString) {
    if (!dateString) {
        return "Data indisponivel";
    }

    return new Intl.DateTimeFormat("pt-BR", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    }).format(new Date(dateString));
}

function formatDateTime(dateString) {
    if (!dateString) {
        return "Horario indisponivel";
    }

    return new Intl.DateTimeFormat("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
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
                <button class="movie-card" type="button" data-movie-id="${movie.id}" data-movie-title="${movie.title}">
                    <span class="movie-tag">${movie.genre}</span>
                    <h3>${movie.title}</h3>
                    <div class="movie-meta">
                        <span>Lancamento: ${formatDate(movie.release_date)}</span>
                        <span>ID: ${movie.id}</span>
                    </div>
                    <p class="movie-description">${movie.description}</p>
                </button>
            `
        )
        .join("");
}

function renderSessions(sessions) {
    const grid = document.getElementById("sessions-grid");
    if (!grid) {
        return;
    }

    if (!sessions.length) {
        grid.innerHTML = '<div class="empty-state">Esse filme ainda nao possui sessoes cadastradas.</div>';
        return;
    }

    grid.innerHTML = sessions
        .map(
            (session) => `
                <article class="session-card">
                    <h3>Sala ${session.room_number}</h3>
                    <div class="session-meta">
                        <span>Inicio: ${formatDateTime(session.start_time)}</span>
                        <span>Fim: ${formatDateTime(session.end_time)}</span>
                        <span>Sessao #${session.id}</span>
                    </div>
                </article>
            `
        )
        .join("");
}

function updateSelectedMovie(movieId) {
    document.querySelectorAll(".movie-card").forEach((card) => {
        card.classList.toggle("is-selected", card.dataset.movieId === String(movieId));
    });
}

async function loadSessions(movieId, movieTitle) {
    const title = document.getElementById("sessions-title");
    if (title) {
        title.textContent = `Sessoes de ${movieTitle}`;
    }

    setFeedback("sessions-feedback", "Carregando sessoes...");

    try {
        const payload = await request(`/api/movies/${movieId}/sessions/`);
        const sessions = Array.isArray(payload) ? payload : payload.results || [];
        renderSessions(sessions);
        setFeedback("sessions-feedback", `${sessions.length} sessao(oes) encontrada(s).`, "success");
        updateSelectedMovie(movieId);
    } catch (error) {
        renderSessions([]);
        setFeedback("sessions-feedback", error.message, "error");
    }
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
    const moviesGrid = document.getElementById("movies-grid");

    if (!sessionIndicator) {
        return;
    }

    if (!hasSession()) {
        window.location.href = "/login/";
        return;
    }

    sessionIndicator.textContent = "Sessao JWT armazenada no navegador";
    loadMovies();

    reloadButton?.addEventListener("click", loadMovies);
    moviesGrid?.addEventListener("click", (event) => {
        const trigger = event.target.closest(".movie-card");
        if (!trigger) {
            return;
        }

        loadSessions(trigger.dataset.movieId, trigger.dataset.movieTitle);
    });
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
