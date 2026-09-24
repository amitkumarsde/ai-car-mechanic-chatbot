"use client";

import { useState } from "react";

import { api, ApiError } from "@/lib/api";
import { checkFile, MAX_FILES_PER_MESSAGE } from "@/lib/files";
import type { ConversationState, Diagnosis, MediaFile, Message } from "@/lib/types";

export interface PendingFile {
  localId: string;
  file: File;
  previewUrl: string;
  media?: MediaFile;
  error?: string;
}

const WELCOME: Message = {
  id: 0,
  role: "bot",
  source: "rule",
  text: "Hi! I am your virtual car mechanic. Describe your car problem, or upload a photo, engine sound or video.",
  media: [],
  created_at: new Date(0).toISOString(),
};

function errorText(err: unknown, fallback: string) {
  return err instanceof ApiError ? err.message : fallback;
}

export function useChat() {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [state, setState] = useState<ConversationState>("new");
  const [messages, setMessages] = useState<Message[]>([WELCOME]);
  const [diagnosis, setDiagnosis] = useState<Diagnosis | null>(null);
  const [files, setFiles] = useState<PendingFile[]>([]);
  const [previews, setPreviews] = useState<Record<string, string>>({});
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [bookingOpen, setBookingOpen] = useState(false);
  const [historyVersion, setHistoryVersion] = useState(0);

  const uploading = files.some((f) => !f.media && !f.error);

  const refreshHistory = () => setHistoryVersion((v) => v + 1);

  const updateFile = (localId: string, changes: Partial<PendingFile>) =>
    setFiles((current) => current.map((f) => (f.localId === localId ? { ...f, ...changes } : f)));

  // Free browser memory used by previews that will not be shown in the chat
  const discardFiles = (list: PendingFile[]) => list.forEach((f) => URL.revokeObjectURL(f.previewUrl));

  const addFiles = async (selected: File[]) => {
    setError(null);
    const room = MAX_FILES_PER_MESSAGE - files.length;
    if (selected.length > room) setError(`You can attach up to ${MAX_FILES_PER_MESSAGE} files per message.`);

    const accepted: PendingFile[] = selected.slice(0, Math.max(room, 0)).map((file) => ({
      localId: crypto.randomUUID(),
      file,
      previewUrl: URL.createObjectURL(file),
      error: checkFile(file) ?? undefined,
    }));
    setFiles((current) => [...current, ...accepted]);

    await Promise.all(
      accepted
        .filter((item) => !item.error)
        .map(async (item) => {
          try {
            updateFile(item.localId, { media: await api.uploadFile(item.file) });
          } catch (err) {
            updateFile(item.localId, { error: errorText(err, "Upload failed.") });
          }
        }),
    );
  };

  const removeFile = (localId: string) => {
    discardFiles(files.filter((f) => f.localId === localId));
    setFiles((current) => current.filter((f) => f.localId !== localId));
  };

  const send = async (text: string) => {
    const ready = files.filter((f) => f.media);
    if (sending || uploading || (!text.trim() && ready.length === 0)) return false;

    setSending(true);
    setError(null);
    try {
      const response = await api.sendMessage({
        conversation_id: conversationId ?? undefined,
        message: text.trim(),
        media_ids: ready.map((f) => f.media!.id),
      });
      setPreviews((current) => ({ ...current, ...Object.fromEntries(ready.map((f) => [f.media!.id, f.previewUrl])) }));
      discardFiles(files.filter((f) => !f.media));
      setFiles([]);
      setConversationId(response.conversation_id);
      setState(response.state);
      setMessages((current) => [...current, response.user_message, response.reply]);
      if (response.diagnosis) setDiagnosis(response.diagnosis);
      if (response.action === "show_booking_form") setBookingOpen(true);
      refreshHistory();
      return true;
    } catch (err) {
      setError(errorText(err, "Something went wrong. Please try again."));
      return false;
    } finally {
      setSending(false);
    }
  };

  const openConversation = async (id: string, closeBooking = true) => {
    setError(null);
    try {
      const detail = await api.getConversation(id);
      discardFiles(files);
      setFiles([]);
      setConversationId(detail.id);
      setState(detail.state);
      setMessages([WELCOME, ...detail.messages]);
      setDiagnosis(detail.diagnoses[0] ?? null);
      if (closeBooking) setBookingOpen(false);
      refreshHistory();
    } catch (err) {
      setError(errorText(err, "Could not load this chat."));
    }
  };

  const diagnoseNow = async () => {
    if (!conversationId) return;
    setSending(true);
    setError(null);
    try {
      await api.diagnoseNow(conversationId);
      await openConversation(conversationId);
    } catch (err) {
      setError(errorText(err, "Could not create a diagnosis."));
    } finally {
      setSending(false);
    }
  };

  const newChat = () => {
    discardFiles(files);
    setFiles([]);
    setConversationId(null);
    setState("new");
    setMessages([WELCOME]);
    setDiagnosis(null);
    setError(null);
    setBookingOpen(false);
  };

  return {
    conversationId,
    state,
    messages,
    diagnosis,
    files,
    previews,
    sending,
    uploading,
    error,
    bookingOpen,
    historyVersion,
    setBookingOpen,
    addFiles,
    removeFile,
    send,
    diagnoseNow,
    openConversation,
    newChat,
  };
}
