"use client";

import { X } from "lucide-react";
import Link from "next/link";
import { useState, type FormEvent, type ReactNode } from "react";

import { api, ApiError, firstError, type FieldErrors } from "@/lib/api";
import { TIME_SLOT_LABELS, type Booking, type Diagnosis, type TimeSlot } from "@/lib/types";

interface Props {
  conversationId: string;
  diagnosis: Diagnosis | null;
  onClose: () => void;
  onBooked: (booking: Booking) => void;
}

const inputClass = "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500";

function Field({ label, error, children }: { label: string; error?: string; children: ReactNode }) {
  return (
    <label className="block text-sm font-medium text-slate-700">
      {label}
      {children}
      {error && <span className="mt-1 block text-xs font-normal text-red-600">{error}</span>}
    </label>
  );
}

export default function BookingForm({ conversationId, diagnosis, onClose, onBooked }: Props) {
  const today = new Date().toLocaleDateString("en-CA");
  const [form, setForm] = useState({
    customer_name: "",
    phone: "",
    car_model: "",
    service: diagnosis?.service ?? "",
    address: "",
    preferred_date: today,
    time_slot: "morning" as TimeSlot,
    notes: "",
  });
  const [errors, setErrors] = useState<FieldErrors | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [booking, setBooking] = useState<Booking | null>(null);

  const update = (field: keyof typeof form) => (event: { target: { value: string } }) =>
    setForm((current) => ({ ...current, [field]: event.target.value }));

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setErrors(null);
    setMessage(null);
    try {
      const result = await api.createBooking({ ...form, conversation_id: conversationId, diagnosis_id: diagnosis?.id });
      setBooking(result);
      onBooked(result);
    } catch (err) {
      if (err instanceof ApiError) {
        const hasFieldError = Object.keys(form).some((field) => err.details?.[field]);
        setErrors(err.details);
        setMessage(hasFieldError ? "Please fix the highlighted fields." : err.message);
      } else {
        setMessage("Could not create the booking. Please try again.");
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" role="dialog" aria-modal="true">
      <div className="max-h-[90vh] w-full max-w-md overflow-y-auto bg-white p-5 shadow-xl">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">{booking ? "Booking received" : "Book a mechanic"}</h2>
          <button type="button" onClick={onClose} className="text-slate-400 hover:text-slate-700" aria-label="Close">
            <X className="size-5" />
          </button>
        </div>

        {booking ? (
          <div className="space-y-3 text-sm text-slate-700">
            <p>
              Thanks {booking.customer_name}! Your <b>{booking.service}</b> booking on <b>{booking.preferred_date}</b> is{" "}
              <b>{booking.status}</b>. Our mechanic will call you on {booking.phone}.
            </p>
            <p className="break-all text-xs text-slate-500">Booking ID: {booking.id}</p>
            <Link href={`/booking/${booking.id}`} className="block rounded-xl bg-blue-600 py-2.5 text-center font-medium text-white">
              View booking
            </Link>
          </div>
        ) : (
          <form onSubmit={submit} className="space-y-3" noValidate>
            {message && <p className="rounded-lg bg-red-50 p-2 text-sm text-red-700">{message}</p>}
            <Field label="Your name" error={firstError(errors, "customer_name")}>
              <input className={inputClass} value={form.customer_name} onChange={update("customer_name")} maxLength={100} required />
            </Field>
            <Field label="Phone number" error={firstError(errors, "phone")}>
              <input className={inputClass} value={form.phone} onChange={update("phone")} inputMode="tel" maxLength={20} required />
            </Field>
            <Field label="Car model and year" error={firstError(errors, "car_model")}>
              <input className={inputClass} value={form.car_model} onChange={update("car_model")} placeholder="e.g. Hyundai Creta 2021" maxLength={100} required />
            </Field>
            <Field label="Service" error={firstError(errors, "service")}>
              <input className={inputClass} value={form.service} onChange={update("service")} maxLength={100} />
            </Field>
            <Field label="Address / location" error={firstError(errors, "address")}>
              <input className={inputClass} value={form.address} onChange={update("address")} maxLength={255} required />
            </Field>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Date" error={firstError(errors, "preferred_date")}>
                <input type="date" className={inputClass} value={form.preferred_date} min={today} onChange={update("preferred_date")} required />
              </Field>
              <Field label="Time" error={firstError(errors, "time_slot")}>
                <select className={inputClass} value={form.time_slot} onChange={update("time_slot")}>
                  {Object.entries(TIME_SLOT_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </Field>
            </div>
            <Field label="Notes (optional)" error={firstError(errors, "notes")}>
              <textarea className={inputClass} value={form.notes} onChange={update("notes")} rows={2} maxLength={500} />
            </Field>
            <button type="submit" disabled={saving} className="w-full rounded-xl bg-blue-600 py-2.5 font-medium text-white hover:bg-blue-700 disabled:opacity-50">
              {saving ? "Booking..." : "Confirm booking"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
