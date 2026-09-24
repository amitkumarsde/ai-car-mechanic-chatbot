export type MediaKind = "image" | "audio" | "video";

export interface MediaFile {
  id: string;
  kind: MediaKind;
  original_name: string;
  size: number;
}

export interface Message {
  id: number;
  role: "user" | "bot";
  source: "user" | "rule" | "ai";
  text: string;
  media: MediaFile[];
  created_at: string;
}

export interface Diagnosis {
  id: number;
  conversation_id: string;
  problem: string;
  details: string;
  recommendation: string;
  service: string;
  urgency: "low" | "medium" | "high";
  estimated_cost: string;
  source: "rule" | "ai";
  booking_id: string | null;
  created_at: string;
}

export type ConversationState = "new" | "asking" | "ai_chat" | "diagnosed";

export interface Conversation {
  id: string;
  title: string;
  state: ConversationState;
  latest_diagnosis: Diagnosis | null;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
  diagnoses: Diagnosis[];
}

export interface ChatResponse {
  conversation_id: string;
  state: ConversationState;
  user_message: Message;
  reply: Message;
  diagnosis: Diagnosis | null;
  action: "show_booking_form" | null;
}

export type TimeSlot = "morning" | "afternoon" | "evening";

export const TIME_SLOT_LABELS: Record<TimeSlot, string> = {
  morning: "Morning (9 AM - 12 PM)",
  afternoon: "Afternoon (12 PM - 4 PM)",
  evening: "Evening (4 PM - 7 PM)",
};

export interface BookingInput {
  conversation_id: string;
  diagnosis_id?: number | null;
  customer_name: string;
  phone: string;
  car_model: string;
  service: string;
  address: string;
  preferred_date: string;
  time_slot: TimeSlot;
  notes: string;
}

export interface Booking extends Omit<BookingInput, "conversation_id" | "diagnosis_id"> {
  id: string;
  diagnosis: Diagnosis | null;
  status: "pending" | "confirmed" | "cancelled";
  created_at: string;
}
