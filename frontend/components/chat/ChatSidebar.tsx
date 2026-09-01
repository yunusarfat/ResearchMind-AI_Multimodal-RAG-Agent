"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { Plus, MessageSquare, Trash2, Loader2 } from "lucide-react";
import { ChatSummary } from "@/types/chat";
import { cn, formatRelativeTime } from "@/lib/utils";
import { chatsApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";

interface ChatSidebarProps {
  chats: ChatSummary[];
  onDelete: (chatId: string) => void;
}

export function ChatSidebar({ chats, onDelete }: ChatSidebarProps) {
  const { token } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [isCreating, setIsCreating] = useState(false);

  async function handleNewChat() {
    if (!token || isCreating) return;
    setIsCreating(true);
    try {
      // The chat row must exist in Postgres BEFORE /chat/query will accept
      // a message for it (see backend app/api/chat.py's ownership check) —
      // so create it here rather than fabricating a client-side id.
      const chat = await chatsApi.create(token);
      router.push(`/chat/${chat.id}`);
    } finally {
      setIsCreating(false);
    }
  }

  return (
    <nav className="flex h-full w-full flex-col border-r border-border bg-surface">
      <div className="border-b border-border p-3">
        <button
          onClick={handleNewChat}
          disabled={isCreating}
          className="flex w-full items-center justify-center gap-2 rounded-md bg-accent px-3 py-2 text-sm font-medium text-accent-ink hover:opacity-90 disabled:opacity-60"
        >
          {isCreating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
          New chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        {chats.length === 0 ? (
          <p className="px-2 py-4 text-center text-sm text-muted">
            No chats yet. Start one above.
          </p>
        ) : (
          <ul className="flex flex-col gap-0.5">
            {chats.map((chat) => {
              const isActive = pathname === `/chat/${chat.id}`;
              return (
                <li key={chat.id} className="group relative">
                  <Link
                    href={`/chat/${chat.id}`}
                    className={cn(
                      "flex flex-col gap-0.5 rounded-md px-3 py-2 pr-8 text-sm transition-colors",
                      isActive ? "bg-surface2 text-ink" : "text-muted hover:bg-surface2 hover:text-ink"
                    )}
                  >
                    <span className="flex items-center gap-1.5 truncate font-medium">
                      <MessageSquare className="h-3.5 w-3.5 shrink-0" />
                      <span className="truncate">{chat.title}</span>
                    </span>
                    <span className="pl-5 text-xs text-muted">
                      {formatRelativeTime(chat.updated_at)}
                    </span>
                  </Link>
                  <button
                    onClick={() => onDelete(chat.id)}
                    aria-label={`Delete chat: ${chat.title}`}
                    className="absolute right-2 top-2 hidden rounded p-1 text-muted hover:bg-surface hover:text-danger group-hover:block"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </nav>
  );
}
