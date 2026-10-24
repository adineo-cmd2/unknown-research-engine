import { useEffect, useState } from 'react';
import { apiGet } from '../../lib/apiClient';

interface Established {
  statement: string;
  source: string;
}

interface Unknown {
  statement: string;
  category: string;
  why_unknown: string;
}

interface Boundary {
  established: Established[];
  unknown: Unknown[];
  mock: boolean;
}

export default function KnownBoundarySplit() {
  const [sid, setSid] = useState<string | null>(null);
  const [data, setData] = useState<Boundary | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('sid');
    setSid(id);
    if (!id) return;
    apiGet(`/api/research/${id}/known-boundary`)
      .then((b) => setData(b as Boundary))
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load boundary.'));
  }, []);

  if (sid === null) return <p className="text-sm opacity-70">Loading…</p>;
  if (!sid) return <p className="text-sm">No session selected. <a className="underline" href="/sessions">Pick a session</a> first.</p>;
  if (error) return <p className="text-sm text-red-700">{error}</p>;
  if (!data) return <p className="text-sm opacity-70">Loading known/unknown boundary…</p>;

  return (
    <div>
      {data.mock && (
        <div className="mb-4 border border-amber-300 bg-amber-50 p-3 text-sm">
          Mock sources: boundary statements may trace to synthetic sources. Verify this gap against the cited source.
        </div>
      )}
      <div className="grid gap-4 md:grid-cols-2">
        <section className="border border-slate-200 p-4">
          <h2 className="serif-h text-xl">Established</h2>
          <ul className="mt-2 space-y-3">
            {data.established.map((e, i) => (
              <li key={i} className="text-sm">
                <p className="serif-quote">“{e.statement}”</p>
                <p className="mt-1 opacity-70">Source: {e.source}</p>
              </li>
            ))}
            {data.established.length === 0 && <li className="text-sm opacity-70">Nothing established yet.</li>}
          </ul>
        </section>
        <section className="border border-teal bg-teal-bg/30 p-4">
          <h2 className="serif-h text-xl">Unknown</h2>
          <ul className="mt-2 space-y-3">
            {data.unknown.map((u, i) => (
              <li key={i} className="text-sm">
                <p className="mono-n text-xs text-teal">{u.category}</p>
                <p className="serif-quote mt-1">“{u.statement}”</p>
                <p className="mt-1 opacity-70">{u.why_unknown}</p>
              </li>
            ))}
            {data.unknown.length === 0 && <li className="text-sm opacity-70">No open questions found.</li>}
          </ul>
        </section>
      </div>
    </div>
  );
}
