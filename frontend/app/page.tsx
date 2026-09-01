// import Link from "next/link";
// import { FileText, Search, BarChart3, ArrowRight } from "lucide-react";
// import { Button } from "@/components/ui/Button";

// const FEATURES = [
//   {
//     icon: FileText,
//     title: "Papers",
//     description: "Upload and analyze research papers — text, structure, and citations included.",
//   },
//   {
//     icon: Search,
//     title: "Hybrid search",
//     description: "Dense vector search and BM25 keyword search, fused and reranked for precision.",
//   },
//   {
//     icon: BarChart3,
//     title: "Tables & charts",
//     description: "Understands visual data — figures and tables are searchable, not just images.",
//   },
// ];

// const PIPELINE_STEPS = [
//   "Upload / Search",
//   "AI Research Agent",
//   "Retrieve Evidence",
//   "Rerank",
//   "Generate Answer",
//   "Citations",
// ];

// export default function HomePage() {
//   return (
//     <div className="min-h-screen bg-bg">
//       {/* Nav */}
//       <header className="border-b border-border">
//         <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
//           <span className="text-sm font-semibold tracking-tight text-ink">ResearchMind</span>
//           <div className="flex items-center gap-2">
//             <Link href="/login">
//               <Button variant="ghost" size="sm">
//                 Log in
//               </Button>
//             </Link>
//             <Link href="/register">
//               <Button variant="primary" size="sm">
//                 Sign up
//               </Button>
//             </Link>
//           </div>
//         </div>
//       </header>

//       {/* Hero */}
//       <section className="mx-auto max-w-3xl px-6 py-24 text-center">
//         <h1 className="text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
//           AI Research Assistant
//         </h1>
//         <p className="mt-3 text-lg text-muted">
//           Research papers. Smarter answers. Evidence-backed research.
//         </p>
//         <p className="mx-auto mt-4 max-w-xl text-sm text-muted">
//           Search papers, analyze documents, tables and charts, and get answers
//           with supporting sources.
//         </p>
//         <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
//           <Link href="/register">
//             <Button size="lg">
//               Start Research
//               <ArrowRight className="h-4 w-4" />
//             </Button>
//           </Link>
//           <a href="#features">
//             <Button variant="secondary" size="lg">
//               Explore Features
//             </Button>
//           </a>
//         </div>
//       </section>

//       {/* Features */}
//       <section id="features" className="mx-auto max-w-5xl px-6 py-16">
//         <div className="grid gap-4 sm:grid-cols-3">
//           {FEATURES.map(({ icon: Icon, title, description }) => (
//             <div
//               key={title}
//               className="rounded-lg border border-border bg-surface p-5"
//             >
//               <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-md bg-accent/10">
//                 <Icon className="h-4.5 w-4.5 text-accent" />
//               </div>
//               <h3 className="text-sm font-semibold text-ink">{title}</h3>
//               <p className="mt-1.5 text-sm text-muted">{description}</p>
//             </div>
//           ))}
//         </div>
//       </section>

//       {/* How it works */}
//       <section className="mx-auto max-w-md px-6 py-16">
//         <h2 className="mb-8 text-center text-sm font-semibold uppercase tracking-wide text-muted">
//           How it works
//         </h2>
//         <div className="flex flex-col items-center">
//           {PIPELINE_STEPS.map((step, i) => (
//             <div key={step} className="flex flex-col items-center">
//               <div className="w-full max-w-xs rounded-md border border-border bg-surface px-4 py-2.5 text-center text-sm font-medium text-ink">
//                 {step}
//               </div>
//               {i < PIPELINE_STEPS.length - 1 && (
//                 <div className="h-6 w-px bg-border" aria-hidden="true" />
//               )}
//             </div>
//           ))}
//         </div>
//       </section>

//       <footer className="border-t border-border py-8 text-center text-xs text-muted">
//         Built with hybrid retrieval, multimodal understanding, and an agentic research pipeline.
//       </footer>
//     </div>
//   );
// }






import React from "react";


export default function HomePage() {
  return (
    <>
      <style>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        body {
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
          background: #f7fafc;
          color: #0b1a2a;
          line-height: 1.5;
        }
        .container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 1.5rem;
        }
        .text-muted {
          color: #4a5b6e;
        }
        .text-ink {
          color: #0b1a2a;
        }

        /* ===== GLASS / 3D TOUCH ===== */
        .glass-card {
          background: rgba(255, 255, 255, 0.7);
          backdrop-filter: blur(4px);
          -webkit-backdrop-filter: blur(4px);
          border: 1px solid rgba(255, 255, 255, 0.5);
          box-shadow: 0 12px 40px rgba(0, 10, 30, 0.06), 0 2px 8px rgba(0, 0, 0, 0.02);
          transition: all 0.25s ease;
        }
        .glass-card:hover {
          transform: translateY(-6px) scale(1.01);
          box-shadow: 0 24px 56px rgba(0, 20, 50, 0.12), 0 6px 16px rgba(0, 0, 0, 0.04);
          border-color: rgba(26, 75, 140, 0.15);
          background: rgba(255, 255, 255, 0.85);
        }

        .btn-primary {
          background: #1a2e4a;
          color: white;
          border: none;
          padding: 0.75rem 2rem;
          border-radius: 60px;
          font-weight: 600;
          font-size: 0.95rem;
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          cursor: pointer;
          transition: 0.2s;
          text-decoration: none;
          box-shadow: 0 8px 20px rgba(26, 46, 74, 0.15);
        }
        .btn-primary:hover {
          background: #0f1f33;
          transform: scale(1.04) translateY(-2px);
          box-shadow: 0 14px 32px rgba(26, 46, 74, 0.25);
        }

        .btn-secondary {
          background: rgba(255, 255, 255, 0.7);
          backdrop-filter: blur(2px);
          color: #1a2e4a;
          border: 1px solid #d0dce8;
          padding: 0.75rem 2rem;
          border-radius: 60px;
          font-weight: 500;
          font-size: 0.95rem;
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          cursor: pointer;
          transition: 0.2s;
          text-decoration: none;
        }
        .btn-secondary:hover {
          background: white;
          border-color: #a0b8cc;
          transform: scale(1.03) translateY(-2px);
          box-shadow: 0 8px 24px rgba(0, 20, 40, 0.08);
        }

        .btn-ghost {
          background: transparent;
          color: #1a2e4a;
          border: none;
          padding: 0.5rem 1rem;
          font-weight: 500;
          font-size: 0.9rem;
          cursor: pointer;
          transition: 0.2s;
          text-decoration: none;
          border-radius: 40px;
        }
        .btn-ghost:hover {
          background: rgba(0, 0, 0, 0.04);
          transform: scale(1.02);
        }

        /* ===== FEATURE ICON 3D ===== */
        .feature-icon {
          width: 3rem;
          height: 3rem;
          background: linear-gradient(135deg, #eef4ff 0%, #dfe9f5 100%);
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #1a4b8c;
          box-shadow: 0 6px 12px rgba(26, 75, 140, 0.08);
          transition: all 0.25s ease;
        }
        .glass-card:hover .feature-icon {
          transform: scale(1.06) rotate(1deg);
          box-shadow: 0 10px 20px rgba(26, 75, 140, 0.15);
        }

        .step-line {
          width: 2px;
          height: 1.8rem;
          background: linear-gradient(to bottom, #d0dce8, #b8c8d8);
          margin: 0.1rem 0;
        }

        .step-item {
          width: 100%;
          max-width: 280px;
          background: rgba(255, 255, 255, 0.75);
          backdrop-filter: blur(2px);
          border: 1px solid rgba(230, 237, 244, 0.8);
          border-radius: 40px;
          padding: 0.7rem 1.8rem;
          text-align: center;
          font-weight: 500;
          font-size: 0.95rem;
          color: #0b1a2a;
          transition: all 0.2s ease;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
        }
        .step-item:hover {
          background: white;
          border-color: #b0c8dd;
          transform: scale(1.04) translateY(-2px);
          box-shadow: 0 12px 28px rgba(0, 20, 40, 0.08);
        }

        footer {
          border-top: 1px solid rgba(230, 237, 244, 0.6);
          padding: 2.5rem 0;
          text-align: center;
          color: #5a6f82;
          font-size: 0.85rem;
          letter-spacing: 0.3px;
          background: rgba(255, 255, 255, 0.3);
          backdrop-filter: blur(2px);
        }

        /* ===== responsive ===== */
        @media (max-width: 640px) {
          .hero-title {
            font-size: 2.1rem !important;
          }
          .feature-grid {
            grid-template-columns: 1fr !important;
          }
          .btn-group {
            flex-direction: column;
            align-items: center;
          }
          .step-item {
            max-width: 220px;
            font-size: 0.85rem;
            padding: 0.6rem 1.2rem;
          }
        }

        /* ===== extra fancy touches ===== */
        .hero-badge {
          background: rgba(238, 244, 255, 0.8);
          backdrop-filter: blur(2px);
          border: 1px solid rgba(255, 255, 255, 0.6);
          box-shadow: 0 4px 12px rgba(26, 75, 140, 0.06);
        }
        .hero-badge:hover {
          background: #eef4ff;
          transform: scale(1.02);
        }

        .hero-glow {
          position: relative;
        }
        .hero-glow::after {
          content: '';
          position: absolute;
          top: -10%;
          left: 50%;
          transform: translateX(-50%);
          width: 70%;
          height: 40%;
          background: radial-gradient(ellipse, rgba(26, 75, 140, 0.05) 0%, transparent 70%);
          pointer-events: none;
          z-index: 0;
        }
        .hero-glow > * {
          position: relative;
          z-index: 1;
        }
      `}</style>

      {/* ===== HEADER ===== */}
      <header className="sticky top-0 z-20 bg-ash backdrop-blur-md border-b border-[#e6edf4]/60">
        <div className="container flex items-center justify-between py-4">
          <span className="text-xl font-bold tracking-tight text-[#0b1a2a] flex items-center gap-2">
            <span className="bg-[#1a2e4a] text-white text-xs rounded-full px-3 py-0.5 font-semibold tracking-wide">RM</span>
            ResearchMind
          </span>
          <div className="flex items-center gap-1 sm:gap-3">
            <a href="/login" className="btn-ghost text-sm font-medium">Log in</a>
            <a href="/register" className="btn-primary text-sm py-2 px-5">Sign up</a>
          </div>
        </div>
      </header>

      {/* ===== HERO ===== */}
      <section className="container py-16 md:py-24 text-center hero-glow">
        <div className="max-w-3xl mx-auto">
          <div className="inline-block hero-badge text-[#1a4b8c] text-sm font-semibold px-5 py-1.5 rounded-full mb-6 tracking-wide transition-all">
            ✦ RAG · hybrid retrieval · multimodal
          </div>
          <h1 className="hero-title text-4xl md:text-5xl font-bold tracking-tight text-[#0b1a2a] leading-tight">
            AI Research Assistant
          </h1>
          <p className="mt-4 text-xl text-[#2d4055] font-medium">
            Research papers. Smarter answers.<br className="sm:hidden" /> Evidence-backed research.
          </p>
          <p className="mt-4 max-w-xl mx-auto text-[#4a5b6e] text-base">
            Search papers, analyze documents, tables and charts, and get answers with supporting sources.
          </p>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4 btn-group">
            <a href="/login" className="btn-primary text-base px-8 py-3.5">
              Start Research
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" /></svg>
            </a>
            <a href="#features" className="btn-secondary text-base px-8 py-3.5">
              Explore Features
            </a>
          </div>
        </div>
      </section>
      <div className="h-16" /> 

      {/* ===== FEATURES ===== */}
     <section id="features" className="container pb-28">
  <div className="max-w-7xl mx-auto">

    {/* Heading */}
    <div className="flex flex-col md:flex-row md:items-end md:justify-between mb-12">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.3em] text-[#4a7db8] mb-4">
          Built for research
        </p>

        <h2 className="text-4xl md:text-5xl font-bold tracking-[-0.04em] text-[#0b1a2a]">
          Everything you need to
          <br />
          <span className="text-[#8aa1b8]">think deeper.</span>
        </h2>
      </div>

      
    </div>

    {/* Bento Grid */}
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">

      {/* Papers */}
      <div className="group relative min-h-[330px] overflow-hidden rounded-[28px] border border-[#e1e9f0] bg-gradient-to-br from-[#eef6ff] via-white to-white p-7 transition-all duration-500 hover:-translate-y-2 hover:shadow-[0_25px_60px_rgba(26,75,140,0.12)]">

        <div className="absolute -right-16 -top-16 w-44 h-44 rounded-full bg-[#4a8ed8]/10 blur-2xl group-hover:scale-125 transition-transform duration-700" />

        <div className="relative z-10 flex h-full flex-col justify-between">
          <div>
            <div className="w-12 h-12 rounded-2xl bg-white border border-[#dce8f3] shadow-sm flex items-center justify-center text-[#1a4b8c] group-hover:rotate-[-6deg] transition-transform">
              📄
            </div>

            <div className="mt-8">
              <p className="text-xs font-semibold uppercase tracking-widest text-[#6d8bab]">
                01 / Documents
              </p>

              <h3 className="mt-2 text-2xl font-bold text-[#0b1a2a]">
                Research papers
              </h3>

              <p className="mt-3 text-sm leading-relaxed text-[#66788b] max-w-sm">
                Upload papers and explore their text, structure,
                citations, tables, and figures.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs font-semibold text-[#1a4b8c]">
            <span className="w-2 h-2 rounded-full bg-[#4a7db8]" />
            Deep document understanding
          </div>
        </div>
      </div>

      {/* Hybrid Search */}
      <div className="group relative min-h-[330px] overflow-hidden rounded-[28px] border border-[#e1e9f0] bg-gradient-to-br from-[#f0efff] via-white to-white p-7 transition-all duration-500 hover:-translate-y-2 hover:shadow-[0_25px_60px_rgba(92,75,180,0.12)]">

        <div className="absolute -right-16 -top-16 w-44 h-44 rounded-full bg-[#8174d9]/10 blur-2xl group-hover:scale-125 transition-transform duration-700" />

        <div className="relative z-10 flex h-full flex-col justify-between">
          <div>
            <div className="w-12 h-12 rounded-2xl bg-white border border-[#e2dff5] shadow-sm flex items-center justify-center text-xl group-hover:rotate-[6deg] transition-transform">
              ◉
            </div>

            <div className="mt-8">
              <p className="text-xs font-semibold uppercase tracking-widest text-[#8174a9]">
                02 / Retrieval
              </p>

              <h3 className="mt-2 text-2xl font-bold text-[#0b1a2a]">
                Hybrid search
              </h3>

              <p className="mt-3 text-sm leading-relaxed text-[#66788b] max-w-sm">
                Dense vectors and BM25 keyword search work together
                to find the most relevant evidence.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs font-semibold text-[#6257a8]">
            <span className="w-2 h-2 rounded-full bg-[#8174d9]" />
            Fusion + intelligent reranking
          </div>
        </div>
      </div>

      {/* Tables & Charts */}
      <div className="group relative min-h-[330px] overflow-hidden rounded-[28px] border border-[#e1e9f0] bg-gradient-to-br from-[#effaf7] via-white to-white p-7 transition-all duration-500 hover:-translate-y-2 hover:shadow-[0_25px_60px_rgba(20,150,125,0.12)]">

        <div className="absolute -right-16 -top-16 w-44 h-44 rounded-full bg-[#27a98e]/10 blur-2xl group-hover:scale-125 transition-transform duration-700" />

        <div className="relative z-10 flex h-full flex-col justify-between">
          <div>
            <div className="w-12 h-12 rounded-2xl bg-white border border-[#d9eee9] shadow-sm flex items-center justify-center text-xl group-hover:rotate-[-6deg] transition-transform">
              ▦
            </div>

            <div className="mt-8">
              <p className="text-xs font-semibold uppercase tracking-widest text-[#4d9587]">
                03 / Multimodal
              </p>

              <h3 className="mt-2 text-2xl font-bold text-[#0b1a2a]">
                Tables & charts
              </h3>

              <p className="mt-3 text-sm leading-relaxed text-[#66788b] max-w-sm">
                Understand figures and structured data — not just
                the text surrounding them.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs font-semibold text-[#218b78]">
            <span className="w-2 h-2 rounded-full bg-[#27a98e]" />
            Multimodal understanding
          </div>
        </div>
      </div>

    </div>
  </div>
</section>

      <div className="h-16" /> 

      {/* ===== HOW IT WORKS ===== */}
      
 <section className="container pb-24 overflow-hidden">
  <div className="max-w-7xl mx-auto">

    {/* Heading */}
    <div className="mb-16">
      <p className="text-xs font-bold uppercase tracking-[0.35em] text-[#4a7db8] mb-4">
        Research pipeline
      </p>

      <h2 className="text-5xl md:text-7xl font-bold tracking-[-0.04em] text-[#0b1a2a]">
        Ask.
        <span className="text-[#4a7db8]"> Explore.</span>
        <br />
        <span className="text-[#9aafc3]">Discover.</span>
      </h2>
    </div>

    {/* Flow */}
    <div className="flex flex-wrap lg:flex-nowrap items-center gap-3">

      {[
        {
          n: "01",
          title: "Upload",
          desc: "Your research",
          gradient: "from-[#dcecff] to-[#f4f8fc]",
          accent: "#3b82f6",
        },
        {
          n: "02",
          title: "Search",
          desc: "Across sources",
          gradient: "from-[#e3e9ff] to-[#f5f7ff]",
          accent: "#6366f1",
        },
        {
          n: "03",
          title: "Agent",
          desc: "Plans the query",
          gradient: "from-[#eee3ff] to-[#faf5ff]",
          accent: "#8b5cf6",
        },
        {
          n: "04",
          title: "Retrieve",
          desc: "Finds evidence",
          gradient: "from-[#e3f8f4] to-[#f3fcfa]",
          accent: "#14b8a6",
        },
        {
          n: "05",
          title: "Rerank",
          desc: "Scores relevance",
          gradient: "from-[#eaf8e3] to-[#f7fcf4]",
          accent: "#65a30d",
        },
        {
          n: "06",
          title: "Generate",
          desc: "Builds answer",
          gradient: "from-[#fff1d9] to-[#fffaf2]",
          accent: "#f59e0b",
        },
        {
          n: "07",
          title: "Citations",
          desc: "Shows evidence",
          gradient: "from-[#ffe4e8] to-[#fff6f7]",
          accent: "#ef4444",
        },
      ].map((step, i) => (
        <React.Fragment key={step.n}>

          {/* Card */}
          <div
            className={`
              group relative flex-1 min-w-[145px]
              h-[190px] rounded-[28px]
              bg-gradient-to-br ${step.gradient}
              border border-white
              shadow-[0_15px_45px_rgba(11,26,42,0.08)]
              overflow-hidden
              transition-all duration-500
              hover:-translate-y-3
              hover:shadow-[0_25px_60px_rgba(11,26,42,0.14)]
            `}
          >

            {/* Giant number */}
            <div
              className="absolute -right-2 -top-7 text-[100px] font-black leading-none opacity-[0.07]"
              style={{ color: step.accent }}
            >
              {step.n}
            </div>

            {/* Accent glow */}
            <div
              className="absolute -top-10 -left-10 w-24 h-24 rounded-full blur-2xl opacity-30"
              style={{ backgroundColor: step.accent }}
            />

            <div className="relative z-10 p-6 h-full flex flex-col justify-between">

              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center text-xs font-bold text-white shadow-lg"
                style={{ backgroundColor: step.accent }}
              >
                {step.n}
              </div>

              <div>
                <h3 className="text-xl font-bold text-[#0b1a2a] tracking-tight">
                  {step.title}
                </h3>

                <p className="text-xs text-[#718196] mt-1">
                  {step.desc}
                </p>
              </div>

            </div>
          </div>

          {/* Flow arrow */}
          {i < 6 && (
            <div className="hidden lg:flex items-center justify-center shrink-0">
              <div className="relative w-8 h-[2px] bg-[#cbd8e5]">
                <div className="absolute right-0 -top-[4px] w-0 h-0 border-t-[5px] border-t-transparent border-b-[5px] border-b-transparent border-l-[7px] border-l-[#7d91a6]" />
              </div>
            </div>
          )}

        </React.Fragment>
      ))}

    </div>

    {/* Bottom statement */}
    <div className="mt-12 flex items-center justify-between border-t border-[#e5ebf1] pt-6">
      {/* <p className="text-sm text-[#718196]">
        One pipeline. <span className="font-semibold text-[#0b1a2a]">
          Evidence-backed answers.
        </span>
      </p> */}

      {/* <div className="hidden sm:flex items-center gap-2 text-xs text-[#718196]">
        <span className="w-2 h-2 rounded-full bg-[#4a7db8] animate-pulse" />
        AI-powered research
      </div> */}
    </div>

  </div>
</section>
      

      {/* ===== FOOTER ===== */}
     <footer className="relative border-t border-[#e5ebf1] bg-[#f8fafc] overflow-hidden">

  {/* subtle glow */}
  <div className="absolute left-1/2 -top-32 -translate-x-1/2 w-[500px] h-[200px] rounded-full bg-[#4a7db8]/5 blur-3xl" />

  <div className="container relative z-10">

    {/* Main footer */}
    <div className="py-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">

      {/* Brand */}
      <div className="lg:col-span-2">
        <div className="flex items-center gap-3">
          {/* <div className="w-9 h-9 rounded-xl bg-[#0b1a2a] text-white flex items-center justify-center font-bold text-sm shadow-lg">
            R
          </div> */}

          {/* <span className="text-lg font-bold tracking-tight text-[#0b1a2a]">
            ResearchMind
          </span> */}
        </div>

        <p className="mt-5 max-w-md text-sm leading-6 text-[#687b8e]">
          An intelligent research workspace for discovering,
          understanding, and connecting knowledge.
        </p>

        {/* <div className="mt-6 flex items-center gap-2 text-xs text-[#718196]">
          <span className="relative flex h-2.5 w-2.5">
            <span className="absolute inline-flex h-full w-full rounded-full bg-[#4a7db8] opacity-40 animate-ping" />
            <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-[#4a7db8]" />
          </span>
        
        </div> */}
      </div>

      {/* Product */}
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#9aaaba]">
          Product
        </p>

        <div className="mt-5 flex flex-col gap-3 text-sm">
          <a href="#features" className="text-[#53677a] hover:text-[#0b1a2a] transition-colors">
            Features
          </a>

          <a href="#how-it-works" className="text-[#53677a] hover:text-[#0b1a2a] transition-colors">
            How it works
          </a>

          
        </div>
      </div>

      {/* Company */}
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#9aaaba]">
          Company
        </p>

        <div className="mt-5 flex flex-col gap-3 text-sm">
          <a href="#" className="text-[#53677a] hover:text-[#0b1a2a] transition-colors">
            About
          </a>

          <a href="#" className="text-[#53677a] hover:text-[#0b1a2a] transition-colors">
            Privacy
          </a>

         
        </div>
      </div>

    </div>

    {/* Bottom */}
    <div className="border-t border-[#e5ebf1] py-6 flex flex-col sm:flex-row items-center justify-between gap-4">

      <p className="text-xs text-[#8998a7]">
        © 2026 ResearchMind. Built for better research.
      </p>

      <div className="flex items-center gap-5 text-xs text-[#8998a7]">
        <span>Hybrid Retrieval</span>
        <span className="w-1 h-1 rounded-full bg-[#b8c4cf]" />
        <span>Multimodal AI</span>
        <span className="w-1 h-1 rounded-full bg-[#b8c4cf]" />
        <span>Agentic Research</span>
      </div>

    </div>

  </div>
</footer>
    </>
  );
}