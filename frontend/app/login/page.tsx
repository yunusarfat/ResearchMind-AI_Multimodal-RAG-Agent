import Link from "next/link";
import { LoginForm } from "@/components/auth/LoginForm";
import { GoogleButton } from "@/components/auth/GoogleButton";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-bg px-4">
      <div className="w-full max-w-sm">
        <Link href="/" className="mb-8 block text-center text-sm font-semibold text-ink">
          ResearchMind
        </Link>

        <div className="rounded-lg border border-border bg-surface p-6 shadow-subtle">
          <h1 className="text-center text-xl font-semibold text-ink">Welcome back</h1>
          <p className="mt-1 text-center text-sm text-muted">Continue your research</p>

          <div className="mt-6">
            <GoogleButton />
          </div>

          <div className="my-5 flex items-center gap-3">
            <div className="h-px flex-1 bg-border" />
            <span className="text-xs text-muted">OR</span>
            <div className="h-px flex-1 bg-border" />
          </div>

          <LoginForm />
        </div>
      </div>
    </div>
  );
}
