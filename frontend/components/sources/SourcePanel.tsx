"use client";

import { Source } from "@/types/source";
import { SourceCard } from "./SourceCard";
import { FileSearch } from "lucide-react";

export function SourcePanel({ sources }: { sources: Source[] }) {
  return (
    <aside className="flex h-full w-full flex-col border-l border-border bg-surface">
      <div className="border-b border-border px-4 py-3">
        <h2 className="text-sm font-semibold text-ink">Sources</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-3">
        {sources.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-2 px-4 text-center">
            <FileSearch className="h-6 w-6 text-muted" />
            <p className="text-sm text-muted">
              Sources for the current answer will appear here.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-2.5">
            {sources.map((source) => (
              <SourceCard key={source.chunk_id} source={source} />
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}
