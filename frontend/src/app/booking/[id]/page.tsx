"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import DiagnosisCard from "@/components/DiagnosisCard";
import { api, ApiError } from "@/lib/api";
import { TIME_SLOT_LABELS, type Booking } from "@/lib/types";

export default function BookingPage() {
  const { id } = useParams<{ id: string }>();
  const [booking, setBooking] = useState<Booking | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getBooking(id)
      .then(setBooking)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Could not load booking."));
  }, [id]);

  return (
    <div className="mx-auto max-w-xl space-y-4 p-4">
      <h1 className="text-xl font-semibold">Booking details</h1>
      {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {!error && !booking && <p className="text-sm text-slate-500">Loading...</p>}
      {booking && (
        <>
          <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 rounded-2xl bg-white p-4 text-sm shadow-sm">
            <dt className="font-medium">Status</dt>
            <dd className="capitalize">{booking.status}</dd>
            <dt className="font-medium">Service</dt>
            <dd>{booking.service}</dd>
            <dt className="font-medium">Name</dt>
            <dd>{booking.customer_name}</dd>
            <dt className="font-medium">Phone</dt>
            <dd>{booking.phone}</dd>
            <dt className="font-medium">Car</dt>
            <dd>{booking.car_model}</dd>
            <dt className="font-medium">Address</dt>
            <dd>{booking.address}</dd>
            <dt className="font-medium">Date</dt>
            <dd>
              {booking.preferred_date}, {TIME_SLOT_LABELS[booking.time_slot]}
            </dd>
            <dt className="font-medium">Booking ID</dt>
            <dd className="break-all text-slate-500">{booking.id}</dd>
          </dl>
          {booking.diagnosis && <DiagnosisCard diagnosis={booking.diagnosis} />}
        </>
      )}
      <Link href="/chat" className="inline-block text-sm font-medium text-blue-600 hover:underline">
        Back to chat
      </Link>
    </div>
  );
}
