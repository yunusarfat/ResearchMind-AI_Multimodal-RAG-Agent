"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { chatsApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function ChatIndexPage() {
  const { token } = useAuth();
  const router = useRouter();
  const [isCreating, setIsCreating] = useState(false);

  async function handleNewChat() {
    if (!token || isCreating) return;
    setIsCreating(true);
    try {
      const chat = await chatsApi.create(token);
      router.push(`/chat/${chat.id}`);
    } finally {
      setIsCreating(false);
    }
  }

  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-accent/10">
        <Sparkles className="h-6 w-6 text-accent" />
      </div>
      <h1 className="text-lg font-semibold text-ink">Start your research</h1>
      <p className="max-w-sm text-sm text-muted">
        Pick a chat from the sidebar, or start a new one to upload a paper or
        ask a question.
      </p>
      <Button onClick={handleNewChat} isLoading={isCreating} className="mt-2">
        New chat
      </Button>
    </div>
  );
}
