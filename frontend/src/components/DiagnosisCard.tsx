import Link from "next/link";

import type { Diagnosis } from "@/lib/types";

const URGENCY_STYLE: Record<Diagnosis["urgency"], string> = {
  low: "bg-green-100 text-green-800",
  medium: "bg-amber-100 text-amber-800",
  high: "bg-red-100 text-red-800",
};

interface Props {
  diagnosis: Diagnosis;
  onBook?: () => void;
}

export default function DiagnosisCard({ diagnosis, onBook }: Props) {
  return (
    <div className="rounded-2xl border border-blue-200 bg-blue-50 p-4 text-sm text-slate-800">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-base font-semibold">{diagnosis.problem}</h3>
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${URGENCY_STYLE[diagnosis.urgency]}`}>
          {diagnosis.urgency} urgency
        </span>
      </div>
      {diagnosis.details && <p className="mt-2 text-slate-600">{diagnosis.details}</p>}
      <dl className="mt-3 grid gap-1">
        <div>
          <dt className="inline font-medium">Service: </dt>
          <dd className="inline">{diagnosis.service}</dd>
        </div>
        <div>
          <dt className="inline font-medium">What to do: </dt>
          <dd className="inline">{diagnosis.recommendation}</dd>
        </div>
        {diagnosis.estimated_cost && (
          <div>
            <dt className="inline font-medium">Estimated cost: </dt>
            <dd className="inline">{diagnosis.estimated_cost}</dd>
          </div>
        )}
      </dl>
      {onBook && diagnosis.booking_id && (
        <Link
          href={`/booking/${diagnosis.booking_id}`}
          className="mt-4 block rounded-xl border border-blue-600 py-2.5 text-center font-medium text-blue-700 hover:bg-blue-100"
        >
          Mechanic booked - view booking
        </Link>
      )}
      {onBook && !diagnosis.booking_id && (
        <button
          type="button"
          onClick={onBook}
          className="mt-4 w-full rounded-xl bg-blue-600 py-2.5 font-medium text-white hover:bg-blue-700"
        >
          Book Mechanic
        </button>
      )}
    </div>
  );
}
