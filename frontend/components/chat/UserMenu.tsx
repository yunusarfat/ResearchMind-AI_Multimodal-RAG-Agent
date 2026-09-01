"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { ChevronDown, Settings, LogOut } from "lucide-react";
import { useAuth } from "@/lib/auth";

export function UserMenu() {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  if (!user) return null;

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setIsOpen((v) => !v)}
        className="flex items-center gap-1.5 rounded-md px-2 py-1.5 text-sm text-ink hover:bg-surface2"
      >
        <span className="flex h-6 w-6 items-center justify-center rounded-full bg-accent text-xs font-medium text-accent-ink">
          {user.name.charAt(0).toUpperCase()}
        </span>
        <span className="max-w-[120px] truncate">{user.name}</span>
        <ChevronDown className="h-3.5 w-3.5 text-muted" />
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full z-10 mt-1 w-48 animate-fade-in rounded-md border border-border bg-bg py-1 shadow-panel">
          <div className="border-b border-border px-3 py-2">
            <p className="truncate text-sm font-medium text-ink">{user.name}</p>
            <p className="truncate text-xs text-muted">{user.email}</p>
          </div>
          <Link
            href="/settings"
            className="flex items-center gap-2 px-3 py-2 text-sm text-ink hover:bg-surface"
            onClick={() => setIsOpen(false)}
          >
            <Settings className="h-4 w-4" />
            Settings
          </Link>
          <button
            onClick={logout}
            className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-danger hover:bg-surface"
          >
            <LogOut className="h-4 w-4" />
            Log out
          </button>
        </div>
      )}
    </div>
  );
}
