export default function ErrorBanner({ message, onRetry }) {
  return (
    <div className="error" role="alert">
      <p className="error__text">{message}</p>
      {onRetry && (
        <button type="button" className="button button--tiny" onClick={onRetry}>
          Повторить запрос
        </button>
      )}
    </div>
  );
}
