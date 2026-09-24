"use client";

import { Plus } from "lucide-react";
import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import type { Conversation } from "@/lib/types";

interface Props {
  activeId: string | null;
  version: number;
  onSelect: (id: string) => void;
  onNewChat: () => void;
}

export default function ChatHistory({ activeId, version, onSelect, onNewChat }: Props) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let active = true;
    api
      .listConversations()
      .then((items) => {
        if (!active) return;
        setConversations(items);
        setFailed(false);
      })
      .catch(() => {
        if (active) setFailed(true);
      });
    return () => {
      active = false;
    };
  }, [version]);

  return (
    <aside className="flex w-full flex-col border-r border-slate-200 bg-slate-50 md:w-72">
      <div className="p-3">
        <button
          type="button"
          onClick={onNewChat}
          className="flex w-full items-center justify-center gap-1.5 rounded-xl bg-blue-600 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          <Plus className="size-4" />
          New chat
        </button>
      </div>
      <p className="px-4 pb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Your chats</p>
      <ul className="flex-1 space-y-1 overflow-y-auto px-2 pb-3">
        {failed && <li className="px-2 text-xs text-red-600">Could not load history.</li>}
        {!failed && conversations.length === 0 && <li className="px-2 text-xs text-slate-500">No chats yet.</li>}
        {conversations.map((c) => (
          <li key={c.id}>
            <button
              type="button"
              onClick={() => onSelect(c.id)}
              className={`w-full rounded-lg px-3 py-2 text-left text-sm hover:bg-white ${
                c.id === activeId ? "bg-white shadow-sm" : ""
              }`}
            >
              <span className="block truncate font-medium text-slate-800">{c.title || "Untitled chat"}</span>
              <span className="block truncate text-xs text-slate-500">
                {c.latest_diagnosis ? c.latest_diagnosis.problem : new Date(c.updated_at).toLocaleString()}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}
