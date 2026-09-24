"use client";

import { Menu, Plus, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import BookingForm from "@/components/BookingForm";
import ChatHistory from "@/components/ChatHistory";
import ChatInput from "@/components/ChatInput";
import DiagnosisCard from "@/components/DiagnosisCard";
import MessageBubble from "@/components/MessageBubble";
import { useChat } from "@/hooks/useChat";

export default function ChatWindow({ initialMessage = "" }: { initialMessage?: string }) {
  const chat = useChat();
  const [showHistory, setShowHistory] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const canDiagnoseNow = chat.state === "asking" || chat.state === "ai_chat";

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat.messages, chat.diagnosis]);

  const selectConversation = (id: string) => {
    chat.openConversation(id);
    setShowHistory(false);
  };

  return (
    <div className="flex h-[calc(100dvh-6.5rem)]">
      <div className={`${showHistory ? "flex" : "hidden"} absolute inset-x-0 top-14 bottom-12 z-40 md:static md:flex`}>
        <ChatHistory
          activeId={chat.conversationId}
          version={chat.historyVersion}
          onSelect={selectConversation}
          onNewChat={() => {
            chat.newChat();
            setShowHistory(false);
          }}
        />
      </div>

      <section className="flex min-w-0 flex-1 flex-col bg-slate-100">
        <div className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-2 md:hidden">
          <button
            type="button"
            onClick={() => setShowHistory((v) => !v)}
            className="flex items-center gap-1.5 text-sm font-medium text-blue-600"
          >
            {showHistory ? <X className="size-4" /> : <Menu className="size-4" />}
            {showHistory ? "Close chats" : "My chats"}
          </button>
          <button type="button" onClick={chat.newChat} className="flex items-center gap-1.5 text-sm text-slate-600">
            <Plus className="size-4" />
            New chat
          </button>
        </div>

        <div className="flex-1 space-y-3 overflow-y-auto p-4">
          {chat.messages.map((message) => (
            <MessageBubble key={message.id} message={message} previews={chat.previews} />
          ))}
          {chat.sending && <p className="text-sm text-slate-500">Mechanic is typing...</p>}
          {chat.diagnosis && chat.state === "diagnosed" && (
            <div className="mx-auto max-w-xl">
              <DiagnosisCard diagnosis={chat.diagnosis} onBook={() => chat.setBookingOpen(true)} />
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {chat.error && (
          <p role="alert" className="mx-4 mb-2 rounded-lg bg-red-50 p-2 text-sm text-red-700">
            {chat.error}
          </p>
        )}
        {canDiagnoseNow && !chat.sending && (
          <div className="px-4 pb-2">
            <button type="button" onClick={chat.diagnoseNow} className="text-sm font-medium text-blue-600 hover:underline">
              Skip questions and diagnose now
            </button>
          </div>
        )}

        <ChatInput
          initialText={initialMessage}
          files={chat.files}
          disabled={chat.sending}
          uploading={chat.uploading}
          onSend={chat.send}
          onAddFiles={chat.addFiles}
          onRemoveFile={chat.removeFile}
        />
      </section>

      {chat.bookingOpen && chat.conversationId && (
        <BookingForm
          conversationId={chat.conversationId}
          diagnosis={chat.diagnosis}
          onClose={() => chat.setBookingOpen(false)}
          onBooked={() => chat.openConversation(chat.conversationId!, false)}
        />
      )}
    </div>
  );
}
