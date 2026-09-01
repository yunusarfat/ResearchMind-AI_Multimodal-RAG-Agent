"use client";

import { BarChart3 } from "lucide-react";

/**
 * Charts are stored as text descriptions extracted via vision (see
 * backend app/multimodal/charts/chart_processor.py) — there's no image
 * bytes in the citation payload, only the description. This renders that
 * description with a visual frame so it still reads as "chart evidence"
 * rather than a plain text snippet.
 */
export function ChartPreview({ snippet }: { snippet: string }) {
  return (
    <div className="rounded-md border border-border bg-surface2 p-3">
      <div className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-muted">
        <BarChart3 className="h-3.5 w-3.5" />
        Extracted from chart
      </div>
      <p className="text-sm text-ink">{snippet}</p>
    </div>
  );
}
