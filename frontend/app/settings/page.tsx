"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, LogOut, Trash2 } from "lucide-react";
import { RequireAuth } from "@/components/auth/RequireAuth";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { useAuth } from "@/lib/auth";
import { authApi, ApiError } from "@/lib/api";

const CONFIRM_PHRASE = "delete my account";

function SettingsContent() {
  const { user, token, logout } = useAuth();
  const router = useRouter();

  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [confirmText, setConfirmText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!user || !token) return null;

  async function handleDelete() {
    setError(null);
    setIsDeleting(true);
    try {
      await authApi.deleteAccount(token as string);
      logout();
      router.push("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't delete your account. Try again.");
      setIsDeleting(false);
    }
  }

  function closeModal() {
    setIsConfirmOpen(false);
    setConfirmText("");
    setError(null);
  }

  return (
    <div className="mx-auto max-w-lg px-4 py-10">
      <Link
        href="/chat"
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted hover:text-ink"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to chat
      </Link>

      <h1 className="mb-6 text-xl font-semibold text-ink">Settings</h1>

      <div className="rounded-lg border border-border bg-surface p-5">
        <h2 className="mb-4 text-sm font-semibold text-ink">Account</h2>

        <dl className="flex flex-col gap-3 text-sm">
          <div className="flex items-center justify-between">
            <dt className="text-muted">Name</dt>
            <dd className="text-ink">{user.name}</dd>
          </div>
          <div className="flex items-center justify-between">
            <dt className="text-muted">Email</dt>
            <dd className="text-ink">{user.email}</dd>
          </div>
          <div className="flex items-center justify-between">
            <dt className="text-muted">Sign-in method</dt>
            <dd className="capitalize text-ink">{user.auth_provider}</dd>
          </div>
        </dl>
      </div>

      <div className="mt-4 rounded-lg border border-border bg-surface p-5">
        <h2 className="mb-1 text-sm font-semibold text-ink">Log out</h2>
        <p className="mb-4 text-sm text-muted">
          You&apos;ll need to log back in to access your documents and chats.
        </p>
        <Button variant="secondary" size="sm" onClick={logout}>
          <LogOut className="h-4 w-4" />
          Log out
        </Button>
      </div>

      <div className="mt-4 rounded-lg border border-danger/30 bg-surface p-5">
        <h2 className="mb-1 text-sm font-semibold text-danger">Danger zone</h2>
        <p className="mb-4 text-sm text-muted">
          Permanently deletes your account, all uploaded documents, and all
          chat history. This cannot be undone.
        </p>
        <Button variant="danger" size="sm" onClick={() => setIsConfirmOpen(true)}>
          <Trash2 className="h-4 w-4" />
          Delete account
        </Button>
      </div>

      <Modal isOpen={isConfirmOpen} onClose={closeModal} title="Delete your account?">
        <p className="mb-4 text-sm text-muted">
          This permanently deletes your account, every document you&apos;ve
          uploaded, and all chat history. Type{" "}
          <span className="font-mono font-medium text-ink">{CONFIRM_PHRASE}</span>{" "}
          to confirm.
        </p>

        <input
          type="text"
          value={confirmText}
          onChange={(e) => setConfirmText(e.target.value)}
          placeholder={CONFIRM_PHRASE}
          className="mb-3 w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-ink placeholder:text-muted focus:outline-none focus-visible:outline-2 focus-visible:outline-accent"
        />

        {error && <p className="mb-3 text-sm text-danger">{error}</p>}

        <div className="flex justify-end gap-2">
          <Button variant="secondary" size="sm" onClick={closeModal} disabled={isDeleting}>
            Cancel
          </Button>
          <Button
            variant="danger"
            size="sm"
            onClick={handleDelete}
            disabled={confirmText !== CONFIRM_PHRASE}
            isLoading={isDeleting}
          >
            Delete permanently
          </Button>
        </div>
      </Modal>
    </div>
  );
}

export default function SettingsPage() {
  return (
    <RequireAuth>
      <SettingsContent />
    </RequireAuth>
  );
}
