import { ImageIcon, Music, Video } from "lucide-react";

import type { MediaFile, Message } from "@/lib/types";

const KIND_ICONS = { image: ImageIcon, audio: Music, video: Video };

function MediaPreview({ media, previewUrl }: { media: MediaFile; previewUrl?: string }) {
  if (!previewUrl) {
    const Icon = KIND_ICONS[media.kind];
    return (
      <span className="inline-flex items-center gap-1.5 rounded-md bg-black/10 px-2 py-1 text-xs">
        <Icon className="size-3.5" aria-label={media.kind} />
        {media.original_name}
      </span>
    );
  }
  if (media.kind === "image") {
    // eslint-disable-next-line @next/next/no-img-element
    return <img src={previewUrl} alt={media.original_name} className="max-h-48 rounded-lg" />;
  }
  if (media.kind === "audio") return <audio src={previewUrl} controls className="w-64 max-w-full" />;
  return <video src={previewUrl} controls className="max-h-56 rounded-lg" />;
}

export default function MessageBubble({ message, previews }: { message: Message; previews: Record<string, string> }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
          isUser ? "rounded-br-sm bg-blue-600 text-white" : "rounded-bl-sm border border-slate-200 bg-white text-slate-800"
        }`}
      >
        {message.media.length > 0 && (
          <div className="mb-2 flex flex-wrap gap-2">
            {message.media.map((media) => (
              <MediaPreview key={media.id} media={media} previewUrl={previews[media.id]} />
            ))}
          </div>
        )}
        {message.text && <p className="whitespace-pre-wrap break-words">{message.text}</p>}
        {!isUser && message.id !== 0 && (
          <p className="mt-2 text-[11px] text-slate-400">{message.source === "ai" ? "AI answer" : "Instant answer"}</p>
        )}
      </div>
    </div>
  );
}
