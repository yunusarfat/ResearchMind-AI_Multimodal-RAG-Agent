"use client";

import { FileText, CheckCircle2, XCircle } from "lucide-react";
import { UploadingFile } from "@/types/chat";
import { cn } from "@/lib/utils";

export function UploadCard({ upload }: { upload: UploadingFile }) {
  const isDone = upload.status === "done";
  const isError = upload.status === "error";

  return (
    <div className="w-full max-w-sm animate-slide-up rounded-md border border-border bg-surface p-3">
      <div className="mb-2 flex items-center gap-2">
        {isDone ? (
          <CheckCircle2 className="h-4 w-4 shrink-0 text-accent" />
        ) : isError ? (
          <XCircle className="h-4 w-4 shrink-0 text-danger" />
        ) : (
          <FileText className="h-4 w-4 shrink-0 text-muted" />
        )}
        <span className="truncate text-sm font-medium text-ink">{upload.file.name}</span>
      </div>

      {isError ? (
        <p className="text-xs text-danger">{upload.error ?? "Upload failed."}</p>
      ) : (
        <>
          <p className="mb-1.5 text-xs text-muted">
            {isDone
              ? upload.result?.duplicate
                ? "Already in your library"
                : `Processed`
              : upload.status === "processing"
              ? "Processing… plesse wait"
              : "Uploading…"}
          </p>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface2">
            <div
              className={cn(
                "h-full rounded-full bg-accent transition-all duration-300",
                upload.status === "processing" && "animate-pulse"
              )}
              style={{ width: `${isDone ? 100 : upload.progress}%` }}
            />
          </div>
        </>
      )}
    </div>
  );
}
