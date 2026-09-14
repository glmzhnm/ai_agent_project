export default function StatusBar({ health }) {
  if (!health) {
    return <span className="status status--wait">проверяю подключение</span>;
  }
  if (!health.llm_configured) {
    return <span className="status status--off">модель не подключена</span>;
  }
  return <span className="status status--on">модель на связи, {health.model}</span>;
}
