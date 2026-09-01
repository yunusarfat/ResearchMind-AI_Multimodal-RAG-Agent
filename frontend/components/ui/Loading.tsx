import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export function Loading({ className, label }: { className?: string; label?: string }) {
  return (
    <div className={cn("flex items-center gap-2 text-sm text-muted", className)}>
      <Loader2 className="h-4 w-4 animate-spin" />
      {label && <span>{label}</span>}
    </div>
  );
}

export function LoadingDots() {
  return (
    <span className="inline-flex items-center gap-1" aria-label="Thinking">
      <span className="h-1.5 w-1.5 animate-blink rounded-full bg-muted [animation-delay:0ms]" />
      <span className="h-1.5 w-1.5 animate-blink rounded-full bg-muted [animation-delay:150ms]" />
      <span className="h-1.5 w-1.5 animate-blink rounded-full bg-muted [animation-delay:300ms]" />
    </span>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-md bg-surface2", className)} />;
}
