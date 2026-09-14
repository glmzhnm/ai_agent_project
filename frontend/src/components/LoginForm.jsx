import { useState } from "react";

export default function LoginForm({ onLogin }) {
  const [loginValue, setLoginValue] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!loginValue.trim() || !password || loading) return;

    setLoading(true);
    setError(null);
    try {
      await onLogin(loginValue.trim(), password);
    } catch (apiError) {
      setError(apiError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login">
      <form className="login__card" onSubmit={handleSubmit}>
        <h1 className="login__title">Ассистент дежурной смены</h1>
        <p className="login__subtitle">Войдите, чтобы продолжить работу</p>

        <label className="login__label" htmlFor="login">
          Логин
        </label>
        <input
          id="login"
          className="login__input"
          value={loginValue}
          onChange={(event) => setLoginValue(event.target.value)}
          autoComplete="username"
          disabled={loading}
          autoFocus
        />

        <label className="login__label" htmlFor="password">
          Пароль
        </label>
        <input
          id="password"
          type="password"
          className="login__input"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
          disabled={loading}
        />

        {error && (
          <p className="login__error" role="alert">
            {error}
          </p>
        )}

        <button
          type="submit"
          className="button button--primary login__submit"
          disabled={!loginValue.trim() || !password || loading}
        >
          {loading ? "Проверяю…" : "Войти"}
        </button>
      </form>
    </div>
  );
}
