"use client";

import { ReactNode } from "react";
import Link from "next/link";
import { RequireAuth } from "@/components/auth/RequireAuth";
import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { UserMenu } from "@/components/chat/UserMenu";
import { useChatList } from "@/lib/useChatList";

export default function ChatLayout({ children }: { children: ReactNode }) {
  return (
    <RequireAuth>
      <ChatShell>{children}</ChatShell>
    </RequireAuth>
  );
}

function ChatShell({ children }: { children: ReactNode }) {
  const { chats, removeChat } = useChatList();

  return (
    <div className="flex h-screen flex-col bg-bg">
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-border px-4">
        <Link href="/" className="text-sm font-semibold text-ink">
          ResearchMind
        </Link>
        <UserMenu />
      </header>

      <div className="flex flex-1 overflow-hidden">
        <div className="hidden w-64 shrink-0 md:block">
          <ChatSidebar chats={chats} onDelete={removeChat} />
        </div>
        <main className="flex flex-1 overflow-hidden">{children}</main>
      </div>
    </div>
  );
}
