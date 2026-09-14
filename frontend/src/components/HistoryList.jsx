import { MODE_LABELS, formatTime } from "../lib/format.js";

export default function HistoryList({
  tickets,
  query,
  onQueryChange,
  hasMore,
  loading,
  onLoadMore,
  onSelect,
}) {
  return (
    <aside className="history">
      <div className="history__head">
        <h2 className="history__title">Тикеты команды</h2>
      </div>

      <input
        type="search"
        className="history__search"
        placeholder="Поиск по вопросу…"
        value={query}
        onChange={(event) => onQueryChange(event.target.value)}
      />

      {tickets.length === 0 && !loading ? (
        <p className="history__empty">
          {query ? "Ничего не найдено." : "Здесь появятся тикеты всей команды."}
        </p>
      ) : (
        <ul className="history__list">
          {tickets.map((ticket) => (
            <li key={ticket.id}>
              <button
                type="button"
                className={`history__item ${ticket.answer.escalate ? "history__item--escalate" : ""}`}
                onClick={() => onSelect(ticket)}
              >
                <span className="history__question">{ticket.question}</span>
                <span className={`history__meta history__meta--${ticket.mode}`}>
                  {MODE_LABELS[ticket.mode]}, {formatTime(ticket.created_at)}
                  {ticket.answer.escalate && <span className="badge badge--escalate">эскалация</span>}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}

      {hasMore && (
        <button
          type="button"
          className="button button--tiny history__more"
          onClick={onLoadMore}
          disabled={loading}
        >
          {loading ? "Загружаю…" : "Показать ещё"}
        </button>
      )}
    </aside>
  );
}
