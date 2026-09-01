"use client";

import { Search, Globe, GraduationCap, MessageCircle } from "lucide-react";
import { AgentRoute } from "@/types/chat";

const ROUTE_CONFIG: Record<
  NonNullable<AgentRoute>,
  { label: string; icon: React.ComponentType<{ className?: string }> }
> = {
  RETRIEVE: { label: "Searching your documents", icon: Search },
  WEB_SEARCH: { label: "Searching the web", icon: Globe },
  PAPER_SEARCH: { label: "Searching arXiv", icon: GraduationCap },
  DIRECT: { label: "Responding", icon: MessageCircle },
};

export function AgentStatus({ route }: { route: AgentRoute }) {
  if (!route) return null;
  const config = ROUTE_CONFIG[route];
  const Icon = config.icon;

  return (
    <div className="flex w-fit items-center gap-1.5 rounded-md border border-border bg-surface px-2.5 py-1 text-xs text-muted animate-fade-in">
      <Icon className="h-3.5 w-3.5" />
      {config.label}
    </div>
  );
}
