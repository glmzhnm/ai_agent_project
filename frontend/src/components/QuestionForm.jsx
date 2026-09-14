import { MODE_LABELS } from "../lib/format.js";

const MODES = ["engineer", "client", "escalation"];

const EXAMPLES = [
  "Клиент говорит, что сайт открывается через раз, в остальное время 502",
  "Домен переделегировали вчера, почта перестала приходить",
  "Сертификат Let's Encrypt не продлился, в панели ошибка валидации",
];

export default function QuestionForm({
  question,
  onQuestionChange,
  mode,
  onModeChange,
  onSubmit,
  loading,
  maxChars = 1500,
}) {
  const tooLong = question.length > maxChars;
  const canSubmit = question.trim().length > 0 && !tooLong && !loading;

  function handleKeyDown(event) {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter" && canSubmit) {
      onSubmit();
    }
  }

  return (
    <section className="ask">
      <div className="ask__modes" role="group" aria-label="Формат ответа">
        {MODES.map((value) => (
          <button
            key={value}
            type="button"
            className={`chip chip--${value} ${mode === value ? "chip--active" : ""}`}
            aria-pressed={mode === value}
            onClick={() => onModeChange(value)}
            disabled={loading}
          >
            {MODE_LABELS[value]}
          </button>
        ))}
      </div>

      <label className="ask__label" htmlFor="question">
        Опишите ситуацию из тикета
      </label>
      <textarea
        id="question"
        className="ask__input"
        value={question}
        rows={3}
        placeholder="Например: клиент перенёс сайт, после переноса отдаётся старая версия"
        onChange={(event) => onQuestionChange(event.target.value)}
        onKeyDown={handleKeyDown}
        disabled={loading}
      />

      <div className="ask__footer">
        <div className="ask__hint">
          <span className={tooLong ? "counter counter--over" : "counter"}>
            {question.length} из {maxChars}
          </span>
          <span className="ask__shortcut">Ctrl или Cmd и Enter отправляют вопрос</span>
        </div>
        <button
          type="button"
          className="button button--primary"
          onClick={onSubmit}
          disabled={!canSubmit}
        >
          {loading ? "Ассистент думает" : "Спросить AI"}
        </button>
      </div>

      <div className="ask__examples">
        {EXAMPLES.map((example) => (
          <button
            key={example}
            type="button"
            className="example"
            onClick={() => onQuestionChange(example)}
            disabled={loading}
          >
            {example}
          </button>
        ))}
      </div>
    </section>
  );
}
