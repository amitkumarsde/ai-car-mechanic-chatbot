"use client";

import { LoaderCircle, Paperclip, SendHorizontal, X } from "lucide-react";
import { useRef, useState, type KeyboardEvent } from "react";

import type { PendingFile } from "@/hooks/useChat";
import { ACCEPT_ATTRIBUTE, formatSize } from "@/lib/files";

interface Props {
  initialText?: string;
  files: PendingFile[];
  disabled: boolean;
  uploading: boolean;
  onSend: (text: string) => Promise<boolean>;
  onAddFiles: (files: File[]) => void;
  onRemoveFile: (localId: string) => void;
}

export default function ChatInput({ initialText = "", files, disabled, uploading, onSend, onAddFiles, onRemoveFile }: Props) {
  const [text, setText] = useState(initialText);
  const fileInput = useRef<HTMLInputElement>(null);
  const hasReadyFile = files.some((f) => f.media);
  const canSend = !disabled && !uploading && (text.trim().length > 0 || hasReadyFile);

  const submit = async () => {
    if (!canSend) return;
    if (await onSend(text)) setText("");
  };

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  };

  return (
    <div className="border-t border-slate-200 bg-white p-3">
      {files.length > 0 && (
        <ul className="mb-2 flex flex-wrap gap-2">
          {files.map((f) => (
            <li
              key={f.localId}
              className={`flex items-center gap-2 rounded-lg border px-2 py-1 text-xs ${
                f.error ? "border-red-300 bg-red-50 text-red-700" : "border-slate-200 bg-slate-50 text-slate-700"
              }`}
            >
              {!f.media && !f.error && <LoaderCircle className="size-3.5 animate-spin" aria-label="Uploading" />}
              <span className="max-w-48 truncate">{f.error ?? `${f.file.name} (${formatSize(f.file.size)})`}</span>
              <button
                type="button"
                onClick={() => onRemoveFile(f.localId)}
                className="text-slate-400 hover:text-slate-700"
                aria-label={`Remove ${f.file.name}`}
              >
                <X className="size-3.5" />
              </button>
            </li>
          ))}
        </ul>
      )}

      <div className="flex items-end gap-2">
        <button
          type="button"
          onClick={() => fileInput.current?.click()}
          disabled={disabled}
          className="rounded-xl border border-slate-300 p-2.5 text-slate-600 hover:bg-slate-50 disabled:opacity-50"
          title="Attach photo, audio or video"
          aria-label="Attach photo, audio or video"
        >
          <Paperclip className="size-5" />
        </button>
        <input
          ref={fileInput}
          type="file"
          multiple
          accept={ACCEPT_ATTRIBUTE}
          className="hidden"
          onChange={(event) => {
            onAddFiles(Array.from(event.target.files ?? []));
            event.target.value = "";
          }}
        />
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={onKeyDown}
          rows={1}
          maxLength={2000}
          placeholder="Describe your car problem..."
          className="max-h-32 min-h-10 flex-1 resize-none rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500"
        />
        <button
          type="button"
          onClick={submit}
          disabled={!canSend}
          className="flex items-center gap-1.5 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {disabled ? <LoaderCircle className="size-4 animate-spin" /> : <SendHorizontal className="size-4" />}
          Send
        </button>
      </div>
    </div>
  );
}
