import { getClientId } from "./clientId";
import type {
  Booking,
  BookingInput,
  ChatResponse,
  Conversation,
  ConversationDetail,
  Diagnosis,
  MediaFile,
} from "./types";

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api").replace(/\/$/, "");

export type FieldErrors = Record<string, string[] | string>;

export class ApiError extends Error {
  constructor(
    message: string,
    public details: FieldErrors | null = null,
  ) {
    super(message);
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("X-Client-Id", getClientId());
  if (options.body && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...options, headers });
  } catch {
    throw new ApiError("Cannot reach the server. Please check your internet and try again.");
  }

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiError(data?.error?.message ?? `Request failed (${response.status}).`, data?.error?.details ?? null);
  }
  return data as T;
}

export const api = {
  sendMessage: (body: { conversation_id?: string; message: string; media_ids: string[] }) =>
    request<ChatResponse>("/chat/", { method: "POST", body: JSON.stringify(body) }),

  uploadFile: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<MediaFile>("/upload/", { method: "POST", body: form });
  },

  diagnoseNow: (conversationId: string) =>
    request<Diagnosis>("/diagnosis/", { method: "POST", body: JSON.stringify({ conversation_id: conversationId }) }),

  listDiagnoses: () => request<Diagnosis[]>("/diagnosis/"),

  createBooking: (body: BookingInput) =>
    request<Booking>("/booking/", { method: "POST", body: JSON.stringify(body) }),

  getBooking: (id: string) => request<Booking>(`/booking/${encodeURIComponent(id)}/`),

  listConversations: () => request<Conversation[]>("/conversations/"),

  getConversation: (id: string) => request<ConversationDetail>(`/conversations/${encodeURIComponent(id)}/`),
};

export function firstError(details: FieldErrors | null, field: string): string | undefined {
  const value = details?.[field];
  return Array.isArray(value) ? value[0] : value;
}
