import { useEffect, useRef, useState } from "react";
import { askAssistant, fetchHealth, fetchMe, login as loginRequest, logout as logoutRequest } from "./api/client.js";
import AnswerCard from "./components/AnswerCard.jsx";
import ErrorBanner from "./components/ErrorBanner.jsx";
import HistoryList from "./components/HistoryList.jsx";
import LoginForm from "./components/LoginForm.jsx";
import QuestionForm from "./components/QuestionForm.jsx";
import StatusBar from "./components/StatusBar.jsx";
import { useTickets } from "./hooks/useTickets.js";

export default function App() {
  const [authChecked, setAuthChecked] = useState(false);
  const [user, setUser] = useState(null);

  const [question, setQuestion] = useState("");
  const [mode, setMode] = useState("engineer");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState(null);

  const { tickets, query, setQuery, hasMore, loading: ticketsLoading, loadMore, addTicket } =
    useTickets(Boolean(user));
  const lastRequest = useRef(null);

  useEffect(() => {
    fetchMe()
      .then((me) => setUser(me))
      .catch(() => setUser(null))
      .finally(() => setAuthChecked(true));
  }, []);

  useEffect(() => {
    if (!user) return;
    fetchHealth()
      .then(setHealth)
      .catch(() => setHealth({ llm_configured: false, model: "" }));
  }, [user]);

  async function handleLogin(loginValue, password) {
    const me = await loginRequest(loginValue, password);
    setUser(me);
  }

  async function handleLogout() {
    await logoutRequest().catch(() => {});
    setUser(null);
    setResult(null);
    setError(null);
  }

  async function handleAsk(overrideQuestion, overrideMode) {
    const askedQuestion = (overrideQuestion ?? question).trim();
    const askedMode = overrideMode ?? mode;
    if (!askedQuestion || loading) return;

    lastRequest.current = { question: askedQuestion, mode: askedMode };
    setLoading(true);
    setError(null);

    try {
      const data = await askAssistant(askedQuestion, askedMode);
      setResult({ question: askedQuestion, ...data });
      addTicket({
        id: `pending-${Date.now()}`,
        question: askedQuestion,
        mode: askedMode,
        answer: data.answer,
        meta: data.meta,
        created_at: new Date().toISOString(),
      });
    } catch (apiError) {
      if (apiError.status === 401) {
        setUser(null);
        return;
      }
      setError(apiError.message);
    } finally {
      setLoading(false);
    }
  }

  function handleRetry() {
    if (lastRequest.current) {
      handleAsk(lastRequest.current.question, lastRequest.current.mode);
    }
  }

  function handleSelectTicket(ticket) {
    setQuestion(ticket.question);
    setMode(ticket.mode);
    setError(null);
    setResult({ question: ticket.question, answer: ticket.answer, meta: ticket.meta });
  }

  if (!authChecked) {
    return <div className="page page--centered">Проверяю вход…</div>;
  }

  if (!user) {
    return <LoginForm onLogin={handleLogin} />;
  }

  return (
    <div className="page">
      <header className="page__head">
        <div>
          <h1 className="page__title">Ассистент дежурной смены</h1>
          <p className="page__subtitle">
            Разбирает тикеты хостинга: называет вероятную причину, даёт порядок
            проверки и говорит, когда пора эскалировать.
          </p>
        </div>
        <div className="page__head-actions">
          <StatusBar health={health} />
          <span className="page__user">{user.login}</span>
          <button type="button" className="button button--tiny" onClick={handleLogout}>
            Выйти
          </button>
        </div>
      </header>

      <main className="page__body">
        <div className="column">
          <QuestionForm
            question={question}
            onQuestionChange={setQuestion}
            mode={mode}
            onModeChange={setMode}
            onSubmit={() => handleAsk()}
            loading={loading}
          />

          {error && <ErrorBanner message={error} onRetry={handleRetry} />}

          {loading && (
            <div className="skeleton">
              <span className="skeleton__line" />
              <span className="skeleton__line skeleton__line--short" />
              <span className="skeleton__line" />
            </div>
          )}

          {!loading && result && (
            <AnswerCard
              question={result.question}
              answer={result.answer}
              meta={result.meta}
            />
          )}

          {!loading && !result && !error && (
            <div className="placeholder">
              <p>
                Опишите проблему так же, как её написал клиент. Ассистент разберёт
                её и вернёт разбор одним блоком.
              </p>
            </div>
          )}
        </div>

        <HistoryList
          tickets={tickets}
          query={query}
          onQueryChange={setQuery}
          hasMore={hasMore}
          loading={ticketsLoading}
          onLoadMore={loadMore}
          onSelect={handleSelectTicket}
        />
      </main>
    </div>
  );
}
