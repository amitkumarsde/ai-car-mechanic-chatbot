import { Car } from "lucide-react";
import Link from "next/link";

export default function Header() {
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-slate-200 bg-white px-4">
      <Link href="/" className="flex items-center gap-2 text-lg font-bold text-blue-700">
        AI Car Mechanic
        <Car className="size-6" />
      </Link>
      <nav className="flex gap-4 text-sm font-medium text-slate-600">
        <Link href="/chat" className="hover:text-blue-700">
          Chat
        </Link>
        <Link href="/history" className="hover:text-blue-700">
          History
        </Link>
      </nav>
    </header>
  );
}
