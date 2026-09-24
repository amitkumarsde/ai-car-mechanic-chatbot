"use client";

import { useEffect, useState } from "react";

import DiagnosisCard from "@/components/DiagnosisCard";
import { api, ApiError } from "@/lib/api";
import type { Diagnosis } from "@/lib/types";

export default function HistoryPage() {
  const [diagnoses, setDiagnoses] = useState<Diagnosis[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listDiagnoses()
      .then(setDiagnoses)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Could not load history."));
  }, []);

  return (
    <div className="mx-auto max-w-2xl space-y-4 p-4">
      <h1 className="text-xl font-semibold">Diagnosis history</h1>
      {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {!error && diagnoses === null && <p className="text-sm text-slate-500">Loading...</p>}
      {diagnoses?.length === 0 && <p className="text-sm text-slate-500">No diagnosis yet. Start a chat to get one.</p>}
      {diagnoses?.map((diagnosis) => (
        <div key={diagnosis.id}>
          <p className="mb-1 text-xs text-slate-500">
            {new Date(diagnosis.created_at).toLocaleString()} · {diagnosis.source === "ai" ? "AI diagnosis" : "Rule-based diagnosis"}
          </p>
          <DiagnosisCard diagnosis={diagnosis} />
        </div>
      ))}
    </div>
  );
}
