import { useCallback, useEffect, useRef, useState } from "react";
import { fetchTickets } from "../api/client.js";

// Общая на всю команду история тикетов. Живёт в Postgres на сервере, а не в
// localStorage: любой залогиненный видит все тикеты, а не только свои.

const PAGE_SIZE = 20;

export function useTickets(enabled) {
  const [tickets, setTickets] = useState([]);
  const [query, setQuery] = useState("");
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const requestId = useRef(0);

  const load = useCallback(
    async (q, offset) => {
      const id = ++requestId.current;
      setLoading(true);
      try {
        const data = await fetchTickets({ limit: PAGE_SIZE, offset, q });
        if (id !== requestId.current) return; // ответ на устаревший запрос — игнорируем
        setTickets((previous) => (offset === 0 ? data.items : [...previous, ...data.items]));
        setHasMore(data.items.length === PAGE_SIZE);
      } catch {
        // Сессия истекла или сеть недоступна — список тикетов не критичен для
        // работы формы, /api/ask сам вернёт 401 и выкинет на экран логина.
      } finally {
        if (id === requestId.current) setLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    if (!enabled) return;
    load(query, 0);
  }, [enabled, query, load]);

  const loadMore = useCallback(() => {
    if (!hasMore || loading) return;
    load(query, tickets.length);
  }, [hasMore, loading, load, query, tickets.length]);

  const addTicket = useCallback((ticket) => {
    setTickets((previous) => [ticket, ...previous]);
  }, []);

  return { tickets, query, setQuery, hasMore, loading, loadMore, addTicket };
}
