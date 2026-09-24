import { CalendarCheck, Camera, IndianRupee, ListChecks, MessageCircle, MessageSquareText, Zap } from "lucide-react";
import Link from "next/link";

const COMMON_PROBLEMS = [
  "My car is not starting",
  "My engine is overheating",
  "My brakes are squeaking",
  "Check engine light is on",
  "My car AC is not cooling",
  "There is a strange engine noise",
];

const STEPS = [
  { icon: MessageSquareText, title: "Describe", text: "Tell us the problem or upload a photo, sound or video." },
  { icon: ListChecks, title: "Answer", text: "Reply to a few quick questions, like with a real mechanic." },
  { icon: CalendarCheck, title: "Book", text: "Get the likely cause and cost, then book a mechanic." },
];

const HIGHLIGHTS = [
  { icon: Zap, text: "Instant answers for common problems" },
  { icon: Camera, text: "Photo, audio and video analysis" },
  { icon: IndianRupee, text: "Repair cost estimate in ₹" },
];

export default function HomePage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-14">
      <section className="flex flex-col items-center text-center">
        <h1 className="text-3xl font-bold text-slate-900 md:text-4xl">Your virtual car mechanic</h1>
        <p className="mt-3 max-w-xl text-slate-600">
          Describe your car problem or upload a photo, engine sound or video. Get a diagnosis and book a mechanic.
        </p>
        <Link
          href="/chat"
          className="mt-8 flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3 font-medium text-white hover:bg-blue-700"
        >
          <MessageCircle className="size-5" />
          Start chat
        </Link>
        <ul className="mt-6 flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm text-slate-600">
          {HIGHLIGHTS.map(({ icon: Icon, text }) => (
            <li key={text} className="flex items-center gap-1.5">
              <Icon className="size-4 text-blue-600" />
              {text}
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-14 text-center">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Pick a common problem</h2>
        <div className="mt-4 flex flex-wrap justify-center gap-2">
          {COMMON_PROBLEMS.map((problem) => (
            <Link
              key={problem}
              href={`/chat?q=${encodeURIComponent(problem)}`}
              className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm text-slate-700 hover:border-blue-400 hover:text-blue-700"
            >
              {problem}
            </Link>
          ))}
        </div>
      </section>

      <section className="mt-14">
        <h2 className="text-center text-sm font-semibold uppercase tracking-wide text-slate-500">How it works</h2>
        <ol className="mt-4 grid gap-4 sm:grid-cols-3">
          {STEPS.map(({ icon: Icon, title, text }) => (
            <li key={title} className="rounded-xl border border-slate-200 bg-white p-5 text-center">
              <Icon className="mx-auto size-7 text-blue-600" />
              <h3 className="mt-3 font-semibold text-slate-900">{title}</h3>
              <p className="mt-1 text-sm text-slate-600">{text}</p>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
