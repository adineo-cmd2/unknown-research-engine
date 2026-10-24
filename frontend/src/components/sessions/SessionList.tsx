import { useEffect, useState } from 'react';
import { apiDelete, apiGet } from '../../lib/apiClient';

interface ResearchSession {
  id: number;
  topic: string;
  date: string | null;
  gap_count: number;
}

export default function SessionList() {
  const [sessions, setSessions] = useState<ResearchSession[] | null>(null);
  const [error, setError] = useState('');

  function load() {
    apiGet('/api/sessions')
      .then((s) => setSessions(s as ResearchSession[]))
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load sessions.'));
  }

  useEffect(() => {
    load();
  }, []);

  async function remove(id: number) {
    if (!window.confirm(`Delete session ${id}?`)) return;
    try {
      await apiDelete(`/api/sessions/${id}`);
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Delete failed.');
    }
  }

  if (error) return <p className="text-sm text-red-700">{error}</p>;
  if (!sessions) return <p className="text-sm opacity-70">Loading sessions…</p>;
  if (sessions.length === 0)
    return <p className="text-sm">No sessions yet. <a className="underline" href="/analyse">Analyse a topic</a> to create one.</p>;

  return (
    <ul className="space-y-2">
      {sessions.map((s) => (
        <li key={s.id} className="flex items-center justify-between border border-slate-200 px-3 py-2">
          <span className="text-sm">
            <span className="font-bold">#{s.id}</span> {s.topic}{' '}
            <span className="opacity-70">({s.gap_count} gaps{s.date ? ` · ${s.date}` : ''})</span>
          </span>
          <span className="flex gap-3 text-sm">
            <a className="underline" href={`/gap-map?sid=${s.id}`}>Open</a>
            <a className="underline" href={`/known-boundary?sid=${s.id}`}>Boundary</a>
            <button className="text-red-700 underline" onClick={() => remove(s.id)}>Delete</button>
          </span>
        </li>
      ))}
    </ul>
  );
}
