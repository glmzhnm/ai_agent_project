// Единственное место, которое знает про сеть. Компоненты работают с этими
// функциями и не думают про fetch, коды ответов и таймауты.

const REQUEST_TIMEOUT_MS = 60000;

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(path, {
      ...options,
      credentials: "include", // cookie сессии должна уходить и на другой порт (5173 -> 8000)
      signal: controller.signal,
    });
    const body = await response.json().catch(() => null);

    if (!response.ok) {
      const message =
        body?.error ||
        body?.detail?.[0]?.msg ||
        "Сервис недоступен. Проверьте, запущен ли backend.";
      throw new ApiError(message, response.status);
    }
    return body;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (error.name === "AbortError") {
      throw new ApiError("Запрос шёл слишком долго и был прерван.", 504);
    }
    throw new ApiError("Нет связи с сервисом. Проверьте, запущен ли backend.", 0);
  } finally {
    clearTimeout(timer);
  }
}

export function fetchHealth() {
  return request("/api/health");
}

export function askAssistant(question, mode) {
  return request("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, mode }),
  });
}

export function fetchMe() {
  return request("/api/auth/me");
}

export function login(loginValue, password) {
  return request("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ login: loginValue, password }),
  });
}

export function logout() {
  return request("/api/auth/logout", { method: "POST" });
}

export function fetchTickets({ limit = 20, offset = 0, q = "" } = {}) {
  const params = new URLSearchParams({ limit, offset });
  if (q) params.set("q", q);
  return request(`/api/tickets?${params.toString()}`);
}
