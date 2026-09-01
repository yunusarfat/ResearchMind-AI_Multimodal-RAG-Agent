"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/lib/auth";
import { chatsApi, documentsApi, streamChatQuery } from "@/lib/api";
import { generateId } from "@/lib/utils";
import { AgentRoute, ChatMessage, UploadingFile } from "@/types/chat";
import { Source } from "@/types/source";

export function useChatSession(chatId: string) {
  const { user, token } = useAuth();

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [currentRoute, setCurrentRoute] = useState<AgentRoute>(null);
  const [uploads, setUploads] = useState<UploadingFile[]>([]);

  const abortRef = useRef<AbortController | null>(null);

  // Load this chat's history from the backend (Postgres-persisted —
  // see backend app/api/chats.py) whenever the chatId or user changes.
  useEffect(() => {
    if (!user || !token) return;

    let cancelled = false;
    setIsLoadingHistory(true);

    chatsApi
      .get(token, chatId)
      .then((detail) => {
        if (cancelled) return;
        setMessages(detail.messages);
        const lastWithSources = [...detail.messages].reverse().find((m) => m.sources?.length);
        setSources(lastWithSources?.sources ?? []);
      })
      .catch(() => {
        // Chat not found / not owned — leave messages empty; the page
        // shell still renders and a fresh message will 404 loudly if
        // the id is genuinely invalid.
        if (!cancelled) setMessages([]);
      })
      .finally(() => {
        if (!cancelled) setIsLoadingHistory(false);
      });

    return () => {
      cancelled = true;
    };
  }, [chatId, user, token]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!token || isStreaming) return;

      // Optimistic local append — the backend persists the real row
      // during the stream (see backend app/api/chat.py), so there's no
      // separate "save" call needed here; this is purely UI state.
      const userMessage: ChatMessage = {
        id: generateId(),
        role: "user",
        content,
        createdAt: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsStreaming(true);
      setStreamingContent("");
      setCurrentRoute(null);
      setSources([]);

      const controller = new AbortController();
      abortRef.current = controller;

      let finalContent = "";
      let finalSources: Source[] = [];

      await streamChatQuery(
        content,
        chatId,
        token,
        {
          onRoute: (route) => {
            setCurrentRoute(route as AgentRoute);
          },
          onToken: (token) => {
            finalContent += token;
            setStreamingContent((prev) => prev + token);
          },
          onCitations: (newSources) => {
            finalSources = newSources;
            setSources(newSources);
          },
          onError: (message) => {
            finalContent = finalContent || `Something went wrong: ${message}`;
          },
          onDone: () => {
            const assistantMessage: ChatMessage = {
              id: generateId(),
              role: "assistant",
              content: finalContent,
              sources: finalSources,
              createdAt: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, assistantMessage]);
            setStreamingContent("");
            setIsStreaming(false);
          },
        },
        controller.signal
      );
    },
    [chatId, token, isStreaming]
  );

  const uploadFile = useCallback(
    async (file: File) => {
      if (!token) return;

      const uploadId = generateId();
      setUploads((prev) => [
        ...prev,
        { id: uploadId, file, progress: 0, status: "uploading" },
      ]);

      try {
        const result = await documentsApi.upload(file, token, (progress) => {
          setUploads((prev) =>
            prev.map((u) =>
              u.id === uploadId
                ? { ...u, progress, status: progress >= 100 ? "processing" : "uploading" }
                : u
            )
          );
        });

        setUploads((prev) =>
          prev.map((u) => (u.id === uploadId ? { ...u, status: "done", result } : u))
        );
      } catch (err) {
        setUploads((prev) =>
          prev.map((u) =>
            u.id === uploadId
              ? {
                  ...u,
                  status: "error",
                  error: err instanceof Error ? err.message : "Upload failed.",
                }
              : u
          )
        );
      }
    },
    [token]
  );

  const stopStreaming = useCallback(() => {
    abortRef.current?.abort();
    setIsStreaming(false);
  }, []);

  return {
    messages,
    sources,
    isLoadingHistory,
    isStreaming,
    streamingContent,
    currentRoute,
    uploads,
    sendMessage,
    uploadFile,
    stopStreaming,
  };
}
