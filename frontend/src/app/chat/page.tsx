import type { Metadata } from "next";

import ChatWindow from "@/components/ChatWindow";

export const metadata: Metadata = { title: "Chat with a mechanic" };

export default async function ChatPage({ searchParams }: PageProps<"/chat">) {
  const { q } = await searchParams;
  return <ChatWindow initialMessage={typeof q === "string" ? q.slice(0, 200) : ""} />;
}
