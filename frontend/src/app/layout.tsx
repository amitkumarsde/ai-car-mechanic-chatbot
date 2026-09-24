import type { Metadata } from "next";

import Footer from "@/components/Footer";
import Header from "@/components/Header";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "AI Car Mechanic", template: "%s | AI Car Mechanic" },
  description: "Chat with a virtual mechanic to diagnose car problems and book a repair.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body className="flex min-h-dvh flex-col bg-slate-100 text-slate-900 antialiased">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
