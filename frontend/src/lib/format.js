// Форматирование ответа и работа с буфером обмена.

export const MODE_LABELS = {
  engineer: "Для инженера",
  client: "Ответ клиенту",
  escalation: "Эскалация",
};

export const RISK_LABELS = {
  low: "Безопасно",
  medium: "Нужна осторожность",
  high: "Опасные действия",
};

export function answerToMarkdown(question, answer) {
  const parts = [`Вопрос: ${question}`, "", answer.answer];

  if (answer.steps?.length) {
    parts.push("", "Порядок действий:");
    answer.steps.forEach((step, index) => parts.push(`${index + 1}. ${step}`));
  }
  if (answer.commands?.length) {
    parts.push("", "Команды:");
    answer.commands.forEach((item) => {
      parts.push(`  ${item.cmd}`);
      if (item.why) parts.push(`  # ${item.why}`);
    });
  }
  if (answer.questions?.length) {
    parts.push("", "Уточнить:");
    answer.questions.forEach((item) => parts.push(`- ${item}`));
  }
  if (answer.escalate && answer.escalate_reason) {
    parts.push("", `Эскалация: ${answer.escalate_reason}`);
  }
  return parts.join("\n");
}

export async function copyText(text) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    }
    // Запасной путь для http и старых браузеров.
    const area = document.createElement("textarea");
    area.value = text;
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    const ok = document.execCommand("copy");
    document.body.removeChild(area);
    return ok;
  } catch {
    return false;
  }
}

export function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString("ru-RU", {
    hour: "2-digit",
    minute: "2-digit",
  });
}
