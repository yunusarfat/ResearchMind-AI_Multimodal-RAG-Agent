"use client";

import { FileText, Table2, Image as ImageIcon, BarChart3, Globe, GraduationCap } from "lucide-react";
import { Source } from "@/types/source";
import { contentTypeLabel } from "@/lib/utils";
import { TablePreview } from "./TablePreview";
import { ChartPreview } from "./ChartPreview";

const TYPE_ICON: Record<string, React.ComponentType<{ className?: string }>> = {
  text: FileText,
  table: Table2,
  image: ImageIcon,
  chart: BarChart3,
  web: Globe,
  paper: GraduationCap,
};

export function SourceCard({ source }: { source: Source }) {
  const Icon = TYPE_ICON[source.content_type] ?? FileText;

  const location = [
    source.page_number ? `p. ${source.page_number}` : null,
    source.section,
  ]
    .filter(Boolean)
    .join(" · ");

  return (
    <div className="animate-fade-in rounded-md border border-border bg-surface p-3">
      <div className="mb-2 flex items-start justify-between gap-2">
        <div className="flex items-center gap-1.5 text-xs font-medium text-accent">
          <span className="rounded bg-accent/10 px-1.5 py-0.5 font-mono">{source.marker}</span>
          <Icon className="h-3.5 w-3.5 text-muted" />
          <span className="text-muted">{contentTypeLabel(source.content_type)}</span>
        </div>
        {location && <span className="text-xs text-muted">{location}</span>}
      </div>

      {source.content_type === "table" ? (
        <TablePreview snippet={source.snippet} />
      ) : source.content_type === "chart" ? (
        <ChartPreview snippet={source.snippet} />
      ) : (
        <p className="text-sm text-muted">{source.snippet}</p>
      )}

      {source.source_url && (
        <a
          href={source.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-2 inline-block text-xs text-accent hover:underline"
        >
          View source →
        </a>
      )}
    </div>
  );
}
