import { useState } from 'react';
import { apiGet, apiPostForm } from '../../lib/apiClient';

type Status = 'idle' | 'uploading' | 'polling' | 'complete' | 'error';

export default function AnalysisProgress() {
  const [topic, setTopic] = useState('');
  const [files, setFiles] = useState<FileList | null>(null);
  const [status, setStatus] = useState<Status>('idle');
  const [message, setMessage] = useState('');
  const [sessionId, setSessionId] = useState<number | null>(null);

  async function analyse() {
    if (!topic.trim()) {
      setMessage('Enter a research topic first.');
      return;
    }
    setStatus('uploading');
    setMessage('Submitting topic…');
    setSessionId(null);
    try {
      const form = new FormData();
      form.append('topic', topic.trim());
      if (files) {
        for (const f of Array.from(files)) form.append('files', f);
      }
      const data = await apiPostForm('/api/research/analyse', form);
      const sid = data.session_id as number;
      setSessionId(sid);
      setStatus('polling');
      setMessage(`Session ${sid} created — waiting for gap map…`);
      // Poll the map until gaps appear (analyse is synchronous, so this
      // resolves fast; timeout after ~30s).
      const deadline = Date.now() + 30000;
      while (Date.now() < deadline) {
        await new Promise((r) => setTimeout(r, 2000));
        try {
          const m = await apiGet(`/api/sessions/${sid}/map`);
          if ((m.total as number) > 0) {
            setStatus('complete');
            setMessage(`Complete: ${m.total} gaps found.`);
            return;
          }
        } catch {
          // keep polling until the deadline
        }
      }
      setStatus('complete');
      setMessage('Analysis submitted. The gap map may still be empty — open it to check.');
    } catch (e) {
      setStatus('error');
      setMessage(e instanceof Error ? e.message : 'Analysis failed.');
    }
  }

  return (
    <div className="border border-slate-200 p-4">
      <label className="block text-sm font-bold" htmlFor="topic">Research topic</label>
      <input
        id="topic"
        className="mt-1 w-full border border-slate-300 px-2 py-1"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="e.g. sleep and memory consolidation"
      />
      <label className="mt-4 block text-sm font-bold" htmlFor="files">Papers (optional)</label>
      <input
        id="files"
        type="file"
        multiple
        className="mt-1 block text-sm"
        onChange={(e) => setFiles(e.target.files)}
      />
      <button
        className="mt-4 bg-teal px-4 py-1 text-white hover:bg-teal-dark"
        onClick={analyse}
        disabled={status === 'uploading' || status === 'polling'}
      >
        Analyse
      </button>
      {(status !== 'idle') && <p className="mt-2 text-sm opacity-70">{message}</p>}
      {status === 'complete' && sessionId !== null && (
        <a className="mt-2 inline-block underline" href={`/gap-map?sid=${sessionId}`}>
          Open gap map for session {sessionId}
        </a>
      )}
      {status === 'error' && <p className="mt-2 text-sm text-red-700">{message}</p>}
    </div>
  );
}
