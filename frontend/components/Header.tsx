export default function Header() {
  return (
    <header className="sticky top-0 z-20 bg-ash backdrop-blur-md border-b border-[#e6edf4]/60">
      <div className="container flex items-center justify-between py-4">
        <span className="text-xl font-bold tracking-tight text-[#0b1a2a] flex items-center gap-2">
          <span className="bg-[#1a2e4a] text-white text-xs rounded-full px-3 py-0.5 font-semibold tracking-wide">
            AI
          </span>
          ResearchMind
        </span>

        <div className="flex items-center gap-1 sm:gap-3">
          <a href="/login" className="btn-ghost text-sm font-medium">
            Log in
          </a>

          <a href="/register" className="btn-primary text-sm py-2 px-5">
            Sign up
          </a>
        </div>
      </div>
    </header>
  );
}