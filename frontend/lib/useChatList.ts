"use client";

import { useEffect, useState, useCallback } from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { chatsApi } from "@/lib/api";
import { ChatSummary } from "@/types/chat";

/**
 * Fetches the chat list from the backend (Postgres-persisted, see
 * backend app/api/chats.py) whenever the route changes — sufficient for
 * a single-tab app. Re-fetching on route change (rather than a global
 * store) keeps this simple and correct: opening/creating a chat always
 * shows the latest server state.
 */
export function useChatList() {
  const { user, token } = useAuth();
  const pathname = usePathname();
  const [chats, setChats] = useState<ChatSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!user || !token) {
      setChats([]);
      setIsLoading(false);
      return;
    }
    try {
      const result = await chatsApi.list(token);
      setChats(result);
    } catch {
      // Leave the previous list in place rather than clearing it on a
      // transient network error.
    } finally {
      setIsLoading(false);
    }
  }, [user, token]);

  useEffect(() => {
    refresh();
  }, [refresh, pathname]);

  const removeChat = useCallback(
    async (chatId: string) => {
      if (!token) return;
      await chatsApi.delete(token, chatId);
      await refresh();
    },
    [token, refresh]
  );

  return { chats, isLoading, removeChat, refresh };
}
