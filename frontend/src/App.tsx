/**
 * App.tsx — dev landing screen for the Social Influence Task.
 *
 * In production (Prolific), main.tsx routes to PilotApp instead.
 * This screen is for local dev testing only.
 */

import { useState } from "react";
import TimelineRunner from "./components/TimelineRunner";
import { createSession } from "./api";
import type { TaskContext } from "./timeline";

export default function App() {
  const [ctx, setCtx] = useState<TaskContext | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const start = async () => {
    setLoading(true);
    setError(null);
    try {
      const s = await createSession({
        participant_id: "DEV_USER",
        mode: "dev",
      });
      setCtx({
        sessionId: s.session_id,
        token: s.session_token,
        mode: "dev",
        phase1Trials: s.phase1_trials,
        phase2Trials: s.phase2_trials,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  if (ctx) {
    return <TimelineRunner ctx={ctx} onComplete={() => setCtx(null)} />;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="max-w-md w-full p-8 bg-white rounded-lg shadow">
        <h1 className="text-2xl font-semibold text-slate-900 mb-2">
          Social Influence Task — Dev
        </h1>
        <p className="text-sm text-slate-500 mb-6">
          Dev mode: launches full Phase 1 + Phase 2 with test stimuli.
        </p>

        <button
          disabled={loading}
          onClick={start}
          className="w-full px-4 py-2 bg-slate-700 text-white rounded hover:bg-slate-800 disabled:opacity-50"
        >
          Start dev session
        </button>

        {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
      </div>
    </div>
  );
}
