import { useEffect, useState } from 'react';
import { apiGet, apiPatch } from '../../lib/apiClient';

interface Gap {
  id: number;
  category: string;
  claim: string;
  sources: Array<{ title?: string; ref?: string; mock?: boolean } | string>;
  confidence: number;
  why_unknown: string;
  flagged: boolean;
}

interface MapData {
  topic: string;
  by_category: Record<string, Gap[]>;
  total: number;
  mock: boolean;
}

function sourceLabel(s: Gap['sources'][number]): string {
  if (typeof s === 'string') return s;
  return s.title || s.ref || 'unknown source';
}

export default function GapMapGrid() {
  const [sid, setSid] = useState<string | null>(null);
  const [data, setData] = useState<MapData | null>(null);
  const [filter, setFilter] = useState<string>('ALL');
  const [error, setError] = useState('');
  const [flagging, setFlagging] = useState<number | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('sid');
    setSid(id);
    if (!id) return;
    apiGet(`/api/sessions/${id}/map`)
      .then((m) => setData(m as MapData))
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load gap map.'));
  }, []);

  async function flag(gap: Gap) {
    setFlagging(gap.id);
    try {
      await apiPatch(`/api/gaps/${gap.id}/flag`, { flagged: true });
      setData((d) => {
        if (!d) return d;
        const by_category: Record<string, Gap[]> = {};
        for (const [cat, gaps] of Object.entries(d.by_category)) {
          by_category[cat] = gaps.map((g) => (g.id === gap.id ? { ...g, flagged: true } : g));
        }
        return { ...d, by_category };
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Flag failed.');
    } finally {
      setFlagging(null);
    }
  }

  if (sid === null) return <p className="text-sm opacity-70">Loading…</p>;
  if (!sid) return <p className="text-sm">No session selected. <a className="underline" href="/sessions">Pick a session</a> or <a className="underline" href="/analyse">analyse a topic</a>.</p>;
  if (error) return <p className="text-sm text-red-700">{error}</p>;
  if (!data) return <p className="text-sm opacity-70">Loading gap map for session {sid}…</p>;

  const categories = Object.keys(data.by_category);
  const visible: Gap[] =
    filter === 'ALL' ? categories.flatMap((c) => data.by_category[c]) : (data.by_category[filter] ?? []);

  return (
    <div>
      {data.mock && (
        <div className="mb-4 border border-amber-300 bg-amber-50 p-3 text-sm">
          Mock sources: some gaps trace to synthetic, clearly-labelled sources — not real papers. Verify every gap before citing it.
        </div>
      )}
      <div className="flex flex-wrap gap-2">
        <button
          className={`mono-n border px-2 py-1 text-xs ${filter === 'ALL' ? 'bg-teal text-white' : 'border-slate-300'}`}
          onClick={() => setFilter('ALL')}
        >
          ALL ({data.total})
        </button>
        {categories.map((c) => (
          <button
            key={c}
            className={`mono-n border px-2 py-1 text-xs ${filter === c ? 'bg-teal text-white' : 'border-slate-300'}`}
            onClick={() => setFilter(c)}
          >
            {c} ({data.by_category[c].length})
          </button>
        ))}
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {visible.map((g) => (
          <article key={g.id} className="border border-slate-200 p-4">
            <p className="mono-n text-xs text-teal">{g.category}</p>
            <blockquote className="serif-quote mt-2">“{g.claim}”</blockquote>
            <p className="mt-2 text-sm"><span className="font-bold">Why unknown: </span>{g.why_unknown}</p>
            <ul className="mt-1 space-y-1 text-sm opacity-70">
              {g.sources.map((s, i) => (
                <li key={i}>
                  {sourceLabel(s)}
                  {typeof s !== 'string' && s.mock && (
                    <span className="mono-n ml-2 border border-amber-300 bg-amber-50 px-1 text-xs">MOCK</span>
                  )}
                </li>
              ))}
              {g.sources.length === 0 && <li>—</li>}
            </ul>
            <p className="mono-n mt-1 text-xs opacity-70">confidence {g.confidence}</p>
            <div className="mt-2 flex items-center gap-3">
              <button
                className="text-xs underline disabled:opacity-50"
                disabled={g.flagged || flagging === g.id}
                onClick={() => flag(g)}
              >
                {g.flagged ? 'Flagged as inaccurate' : 'Flag as inaccurate'}
              </button>
              <a className="text-xs underline" href={`/known-boundary?sid=${sid}`}>Boundary</a>
            </div>
          </article>
        ))}
      </div>
      {visible.length === 0 && <p className="mt-4 text-sm opacity-70">No gaps in this category.</p>}
    </div>
  );
}
