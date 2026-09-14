import { useState } from "react";
import { RISK_LABELS, answerToMarkdown, copyText } from "../lib/format.js";

function CopyButton({ text, label = "Копировать ответ", className = "button" }) {
  const [state, setState] = useState("idle");

  async function handleCopy() {
    const ok = await copyText(text);
    setState(ok ? "done" : "failed");
    setTimeout(() => setState("idle"), 2000);
  }

  const caption =
    state === "done" ? "Скопировано" : state === "failed" ? "Не удалось" : label;

  return (
    <button type="button" className={className} onClick={handleCopy}>
      {caption}
    </button>
  );
}

export default function AnswerCard({ question, answer, meta }) {
  const markdown = answerToMarkdown(question, answer);

  return (
    <article className="answer">
      <header className="answer__status">
        <span className={`risk risk--${answer.risk}`}>{RISK_LABELS[answer.risk]}</span>
        {answer.tags?.map((tag) => (
          <span key={tag} className="tag">
            {tag}
          </span>
        ))}
        <CopyButton text={markdown} className="button button--ghost answer__copy" />
      </header>

      {answer.out_of_scope && (
        <p className="notice notice--neutral">
          Вопрос вне зоны ответственности ассистента, ответ может быть неточным.
        </p>
      )}

      {answer.escalate && (
        <p className="notice notice--alert">
          Нужна эскалация. {answer.escalate_reason}
        </p>
      )}

      <p className="answer__summary">{answer.answer}</p>

      {answer.steps?.length > 0 && (
        <section className="block">
          <h3 className="block__title">Порядок действий</h3>
          <ol className="steps">
            {answer.steps.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ol>
        </section>
      )}

      {answer.commands?.length > 0 && (
        <section className="block">
          <h3 className="block__title">Команды для проверки</h3>
          <ul className="commands">
            {answer.commands.map((item, index) => (
              <li key={index} className="command">
                <code className="command__code">{item.cmd}</code>
                <CopyButton
                  text={item.cmd}
                  label="Копировать"
                  className="button button--tiny"
                />
                {item.why && <p className="command__why">{item.why}</p>}
              </li>
            ))}
          </ul>
        </section>
      )}

      {answer.questions?.length > 0 && (
        <section className="block">
          <h3 className="block__title">Уточнить у клиента</h3>
          <ul className="bullets">
            {answer.questions.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </section>
      )}

      <footer className="answer__meta">
        <span>
          {meta.provider} / {meta.model}
        </span>
        <span>{(meta.latency_ms / 1000).toFixed(1)} с</span>
        {meta.degraded && (
          <span className="answer__degraded">
            модель ответила текстом, показан упрощённый вид
          </span>
        )}
      </footer>
    </article>
  );
}
