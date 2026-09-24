const STORAGE_KEY = "car-mechanic-client-id";
let memoryId: string | null = null;

// A random id per browser so the backend only returns this user's chats and bookings
export function getClientId(): string {
  try {
    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (saved) return saved;
    const id = crypto.randomUUID();
    window.localStorage.setItem(STORAGE_KEY, id);
    return id;
  } catch {
    memoryId ??= crypto.randomUUID();
    return memoryId;
  }
}
