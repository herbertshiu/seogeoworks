import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ArrowLeft,
  ArrowUpRight,
  Calculator,
  ClipboardCheck,
  Copy,
  Download,
  Printer,
  Share2,
  TrendingUp,
  Check,
  ChevronRight,
  CircleArrowOutUpRight,
  Clock3,
  Menu,
  Moon,
  Play,
  Sun,
  Search,
  Sparkles,
  Target,
  RotateCcw,
  Send,
  X,
} from "lucide-react";
import "./styles.css";

const experts = [
  { initials: "SL", name: "Samantha Li", role: "Search strategist", org: "Independent / Hong Kong", tone: "lime" },
  { initials: "OM", name: "Owen McCarthy", role: "AI product lead", org: "Atlas Intelligence", tone: "coral" },
  { initials: "AK", name: "Aisha Khan", role: "Editorial director", org: "Northstar Studio", tone: "violet" },
];

const notes = [
  { tag: "Field note 07", title: "The answer engine is not your enemy. Your blandness is.", date: "Sep 02, 2026", time: "6 min read", color: "blue" },
  { tag: "Playbook 04", title: "How to write a source an AI can confidently cite", date: "Aug 28, 2026", time: "9 min read", color: "yellow" },
  { tag: "Signal check", title: "Brand demand is moving from clicks to context", date: "Aug 19, 2026", time: "4 min read", color: "pink" },
];

const researchPosts = [
  { category: "GEO research", type: "Deep dive", title: "The citation layer: what answer engines need before they trust a brand", excerpt: "A practical field guide to source quality, corroboration, and the signals that turn content into usable context.", date: "Sep 05, 2026", read: "14 min", tone: "research-lime" },
  { category: "Expert insight", type: "Conversation", title: "Samantha Li on the difference between being visible and being useful", excerpt: "A search strategist on why the best GEO work starts with sharper opinions, not more output.", date: "Sep 01, 2026", read: "8 min", tone: "research-coral" },
  { category: "SEO / GEO", type: "Field note", title: "From keyword clusters to context graphs", excerpt: "What changes when the unit of optimization is no longer the page, but the relationship between ideas.", date: "Aug 25, 2026", read: "11 min", tone: "research-blue" },
  { category: "Expert insight", type: "Briefing", title: "Why third-party proof is becoming part of your owned strategy", excerpt: "The distribution moves that help a brand become recognizable beyond its own domain.", date: "Aug 17, 2026", read: "7 min", tone: "research-violet" },
];

const assessmentQuestions = [
  { id: "foundation", label: "Foundations", question: "How consistently does your site earn organic clicks for your priority topics?", options: ["We rarely appear", "Sometimes, but inconsistently", "We have a reliable footprint", "We are a category reference"], seo: [0, 1, 2, 3], geo: [0, 1, 2, 2] },
  { id: "content", label: "Content clarity", question: "Can a reader (or crawler) quickly understand who you help and what you know?", options: ["It is hard to tell", "It depends on the page", "The message is mostly clear", "Our point of view is unmistakable"], seo: [0, 1, 2, 3], geo: [0, 1, 2, 3] },
  { id: "proof", label: "Proof & authority", question: "How visible are your first-hand expertise, sources, and named contributors?", options: ["Mostly anonymous", "Some proof exists", "Proof is part of our process", "Our experts are cited and trusted"], seo: [0, 1, 2, 3], geo: [0, 1, 2, 3] },
  { id: "structure", label: "Machine-readable", question: "How much of your important context is structured for machines to parse and connect?", options: ["We have not considered it", "Basic metadata only", "Structured content is in progress", "Our entities and relationships are explicit"], seo: [0, 1, 2, 3], geo: [0, 1, 2, 3] },
  { id: "distribution", label: "Distributed presence", question: "Does your brand show up in the sources, communities, and conversations your audience trusts?", options: ["Only on our own site", "A few scattered mentions", "We show up in relevant places", "We are part of the wider conversation"], seo: [0, 1, 2, 2], geo: [0, 1, 2, 3] },
  { id: "measurement", label: "Measurement", question: "Can you tell whether search visibility is creating qualified demand, not just traffic?", options: ["We mostly guess", "We track rankings or traffic", "We connect visibility to outcomes", "We measure attention, influence, and action"], seo: [0, 1, 2, 3], geo: [0, 1, 2, 3] },
];

const scoreLabel = (score: number) => score < 40 ? "Signal forming" : score < 70 ? "Signal building" : "Signal leading";

const comparisonRows = [
  { lens: "Primary outcome", seo: "Earn the click", geo: "Earn the inclusion", gap: "A strong ranking can still be invisible when an answer engine summarizes the category without you." },
  { lens: "Core asset", seo: "A page optimized for a query", geo: "A source with a clear point of view", gap: "Keyword coverage without original expertise gives machines little reason to select your brand." },
  { lens: "Authority signal", seo: "Links, relevance, and domain strength", geo: "Named experts, corroboration, and recognizable entities", gap: "Backlinks help establish importance; they do not automatically establish what your brand knows." },
  { lens: "Content shape", seo: "Answer the query efficiently", geo: "Build context across related questions", gap: "A collection of isolated posts is harder to retrieve than a connected body of knowledge." },
  { lens: "Distribution", seo: "Own the search results page", geo: "Show up in the wider information ecosystem", gap: "Your website is only one possible source. Community, press, partners, and reviews fill the gaps." },
  { lens: "Measurement", seo: "Rankings, clicks, and conversions", geo: "Citations, mentions, sentiment, and qualified demand", gap: "Traffic can stay flat while influence grows — so the dashboard needs a wider field of view." },
];

const caseStudyPhases = [
  { number: "01", title: "Map the blind spots", text: "We started with a prompt set, not a keyword list — documenting where Harbor & Co. was missing, miscategorized, or described without its point of view." },
  { number: "02", title: "Build the source layer", text: "We rebuilt the core guides around named experts, original evidence, clear definitions, and connected entity signals that machines could resolve." },
  { number: "03", title: "Distribute the proof", text: "We turned partner conversations, customer language, and third-party mentions into a consistent trail of corroboration beyond the owned site." },
  { number: "04", title: "Measure the echo", text: "The team paired traditional search data with citation checks, answer inclusion, sentiment, and qualified conversations to see what was compounding." },
];

const auditGroups = [
  { name: "Identity & expertise", description: "Can an answer engine tell who you are, what you know, and why you are credible?", checks: [
    { id: "entity", title: "Our organization, people, and offers have consistent names across the web.", recommendation: "Create one canonical naming system for your brand, experts, products, and locations.", priority: "High" },
    { id: "expert", title: "Important pages show a real author with relevant experience.", recommendation: "Add author bios, credentials, editorial ownership, and links to first-hand work.", priority: "High" },
    { id: "about", title: "Our About page clearly explains our point of view and the problems we solve.", recommendation: "Rewrite the About page as a source of context, not only a company timeline.", priority: "Medium" },
  ]},
  { name: "Source quality", description: "Does your content give machines something specific and trustworthy to retrieve?", checks: [
    { id: "evidence", title: "We publish original evidence, examples, or observations — not only summaries.", recommendation: "Turn internal knowledge, customer language, and research into named, quotable proof.", priority: "High" },
    { id: "definitions", title: "Our key terms and category definitions are stated plainly.", recommendation: "Add a glossary or definition layer so important concepts resolve consistently.", priority: "Medium" },
    { id: "freshness", title: "We have a visible process for reviewing and updating important sources.", recommendation: "Give cornerstone pages owners, review dates, and explicit update notes.", priority: "Medium" },
  ]},
  { name: "Reach & measurement", description: "Is your expertise corroborated outside your own domain and measured beyond rankings?", checks: [
    { id: "distribution", title: "Trusted third-party sources mention or reference our expertise.", recommendation: "Build a distribution map across partners, communities, press, reviews, and events.", priority: "High" },
    { id: "prompts", title: "We regularly test how answer engines describe and recommend our brand.", recommendation: "Create a repeatable prompt set and log inclusion, accuracy, and sentiment over time.", priority: "High" },
    { id: "outcomes", title: "We connect visibility signals to qualified conversations or revenue.", recommendation: "Pair citation monitoring with CRM outcomes, assisted demand, and qualitative feedback.", priority: "Medium" },
  ]},
];

function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [subscribed, setSubscribed] = useState(false);
  const [newsletterEmail, setNewsletterEmail] = useState("");
  const [researchFilter, setResearchFilter] = useState("All");
  const [theme, setTheme] = useState<"dark" | "light">(() => (localStorage.getItem("signal-room-theme") as "dark" | "light") || "dark");

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("signal-room-theme", theme);
  }, [theme]);
  const [assessmentStep, setAssessmentStep] = useState(0);
  const [assessmentAnswers, setAssessmentAnswers] = useState<number[]>([]);
  const [assessmentComplete, setAssessmentComplete] = useState(false);
  const [comparisonView, setComparisonView] = useState<"all" | "seo" | "geo">("all");
  const [roiInputs, setRoiInputs] = useState({ sessions: 18000, conversion: 2.4, value: 3200, lift: 28, investment: 4500 });
  const [auditChecks, setAuditChecks] = useState<Record<string, boolean>>({});
  const [auditReport, setAuditReport] = useState(false);
  const [auditCopied, setAuditCopied] = useState(false);

  const handleSubscribe = () => setSubscribed(true);
  const handleNewsletterSubmit = (event: React.FormEvent<HTMLFormElement>) => { event.preventDefault(); if (newsletterEmail.trim()) setSubscribed(true); };
  const filteredResearch = researchFilter === "All" ? researchPosts : researchPosts.filter((post) => post.category === researchFilter);
  const currentQuestion = assessmentQuestions[assessmentStep];
  const seoScore = Math.round((assessmentAnswers.reduce((total, answer, index) => total + (assessmentQuestions[index]?.seo[answer] ?? 0), 0) / (assessmentQuestions.length * 3)) * 100);
  const geoScore = Math.round((assessmentAnswers.reduce((total, answer, index) => total + (assessmentQuestions[index]?.geo[answer] ?? 0), 0) / (assessmentQuestions.length * 3)) * 100);
  const answerAssessment = (answer: number) => {
    const nextAnswers = [...assessmentAnswers];
    nextAnswers[assessmentStep] = answer;
    setAssessmentAnswers(nextAnswers);
    if (assessmentStep === assessmentQuestions.length - 1) setAssessmentComplete(true);
    else setAssessmentStep(assessmentStep + 1);
  };
  const resetAssessment = () => { setAssessmentStep(0); setAssessmentAnswers([]); setAssessmentComplete(false); };
  const roi = {
    currentLeads: Math.round(roiInputs.sessions * (roiInputs.conversion / 100)),
    incrementalLeads: Math.round(roiInputs.sessions * (roiInputs.conversion / 100) * (roiInputs.lift / 100)),
    monthlyImpact: Math.round(roiInputs.sessions * (roiInputs.conversion / 100) * (roiInputs.lift / 100) * roiInputs.value),
  };
  const roiPayback = roi.monthlyImpact > 0 ? Math.max(1, Math.ceil(roiInputs.investment / roi.monthlyImpact)) : 0;
  const formatCurrency = (value: number) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
  const updateRoi = (key: keyof typeof roiInputs, value: number) => setRoiInputs((current) => ({ ...current, [key]: value }));
  const allAuditChecks = auditGroups.flatMap((group) => group.checks);
  const auditComplete = allAuditChecks.filter((check) => auditChecks[check.id]).length;
  const auditScore = Math.round((auditComplete / allAuditChecks.length) * 100);
  const auditLabel = auditScore < 40 ? "Early signal" : auditScore < 75 ? "Building signal" : "Ready to be cited";
  const toggleAuditCheck = (id: string) => setAuditChecks((current) => ({ ...current, [id]: !current[id] }));
  const resetAudit = () => { setAuditChecks({}); setAuditReport(false); setAuditCopied(false); };
  const copyAuditSummary = async () => { await navigator.clipboard?.writeText(`Signal Room GEO audit: ${auditScore}% — ${auditLabel}. ${auditComplete}/${allAuditChecks.length} checks complete.`); setAuditCopied(true); setTimeout(() => setAuditCopied(false), 1800); };

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
    setMenuOpen(false);
  };

  return (
    <div className="site-shell">
      <div className="top-strip"><span>Independent research for the discoverability era</span><span>Issue 01 · September 2026</span></div>
      <header className="site-header">
        <button className="mobile-menu" aria-label="Toggle menu" onClick={() => setMenuOpen(!menuOpen)}>{menuOpen ? <X size={22} /> : <Menu size={22} />}</button>
        <button className="wordmark" onClick={() => scrollTo("top")}><span className="wordmark-dot" />signal<span>room</span></button>
        <nav className={menuOpen ? "nav-links open" : "nav-links"}>
          <button onClick={() => scrollTo("briefings")}>Briefings</button><button onClick={() => scrollTo("compare")}>SEO vs GEO</button><button onClick={() => scrollTo("case-study")}>Case study</button><button onClick={() => scrollTo("roi")}>ROI calculator</button><button onClick={() => scrollTo("audit")}>GEO audit</button><button onClick={() => scrollTo("voices")}>Voices</button><button onClick={() => scrollTo("field-notes")}>Field notes</button><button onClick={() => scrollTo("research-desk")}>Research desk</button><button onClick={() => scrollTo("about")}>About</button>
        </nav>
        <div className="header-actions"><button className="theme-toggle" aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`} onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>{theme === "dark" ? <Sun size={15} /> : <Moon size={15} />}<span>{theme === "dark" ? "Light" : "Dark"}</span></button><button className="header-cta" onClick={handleSubscribe}>{subscribed ? "You’re in" : "Get the signal"}<ArrowUpRight size={16} /></button></div>
      </header>

      <main id="top">
        <section className="hero section-grid">
          <div className="hero-copy">
            <div className="eyebrow"><span className="eyebrow-line" /> The people & patterns behind modern search</div>
            <h1>Be <em>findable.</em><br />Stay human.</h1>
            <p className="hero-lede">Signal Room is an independent field guide to SEO, GEO, and the operators reshaping how brands get found, understood, and remembered.</p>
            <div className="hero-actions"><button className="button-primary" onClick={() => scrollTo("briefings")}>Explore the latest <ChevronRight size={17} /></button><button className="text-button" onClick={() => scrollTo("voices")}>Meet the room <ArrowUpRight size={16} /></button></div>
            <div className="hero-proof"><div className="avatar-stack"><span>SL</span><span>OM</span><span>AK</span><b>+</b></div><span>Conversations with 42 practitioners<br /><strong>across search, content & AI</strong></span></div>
          </div>
          <div className="hero-visual" aria-label="Abstract search signal visualization"><div className="visual-orbit orbit-one" /><div className="visual-orbit orbit-two" /><div className="visual-orbit orbit-three" /><div className="visual-core"><Search size={28} /><span>relevance</span></div><div className="signal signal-a">SEO</div><div className="signal signal-b">GEO</div><div className="signal signal-c">AI</div><div className="visual-caption"><span>LIVE SIGNAL MAP</span><span>22.31° N / 114.17° E</span></div></div>
        </section>

        <section className="ticker"><div className="ticker-label"><Sparkles size={15} /> In the room now</div><div className="ticker-track"><span>Search is a conversation</span><b>✳</b><span>Authority is earned in public</span><b>✳</b><span>Useful beats optimized</span><b>✳</b><span>Search is a conversation</span></div></section>

        <section id="compare" className="comparison-section"><div className="comparison-heading"><div><div className="eyebrow"><span className="eyebrow-line" /> The strategy gap</div><h2>SEO gets you<br /><em>seen. GEO gets you chosen.</em></h2><p>Traditional search optimization and generative engine optimization share a foundation — but they win in different moments. Use this breakdown to spot where your playbook stops short.</p></div><div className="comparison-key"><span><i className="key-dot seo-dot" /> SEO</span><span><i className="key-dot geo-dot" /> GEO</span></div></div><div className="comparison-controls"><span>Compare by signal</span><div><button className={comparisonView === "all" ? "active" : ""} onClick={() => setComparisonView("all")}>All gaps</button><button className={comparisonView === "seo" ? "active" : ""} onClick={() => setComparisonView("seo")}>SEO lens</button><button className={comparisonView === "geo" ? "active" : ""} onClick={() => setComparisonView("geo")}>GEO lens</button></div></div><div className={`comparison-table view-${comparisonView}`}><div className="comparison-table-head"><span>Signal</span><span>Traditional SEO</span><span>Generative / GEO</span><span>Common gap</span></div>{comparisonRows.map((row, index) => <article className="comparison-row" key={row.lens}><div className="comparison-lens"><span>0{index + 1}</span><b>{row.lens}</b></div><div className="comparison-cell seo-cell"><i className="key-dot seo-dot" /><span>{row.seo}</span></div><div className="comparison-cell geo-cell"><i className="key-dot geo-dot" /><span>{row.geo}</span></div><div className="comparison-gap"><span>Watch for</span>{row.gap}</div></article>)}</div><div className="comparison-foot"><span><Target size={16} /> The bridge is not more content. It is <strong>more recognizable expertise.</strong></span><button className="text-button" onClick={() => scrollTo("assessment")}>Check your readiness <ArrowUpRight size={16} /></button></div></section>

        <section id="case-study" className="case-study-section"><div className="case-study-intro"><div><div className="eyebrow"><span className="eyebrow-line" /> Case study / 01</div><h2>From <em>missing</em><br />to mentioned.</h2></div><div className="case-study-context"><span>Illustrative composite</span><p>How a specialist brand rebuilt its search presence to become a more useful, citable source for answer engines.</p></div></div><div className="case-study-layout"><div className="case-study-result"><div className="result-label">Harbor & Co.<br /><span>Specialist advisory firm</span></div><div className="result-quote">“We stopped trying to sound like the category. We started documenting why we see it differently.”</div><div className="case-metrics"><div><strong>+3.4×</strong><span>qualified mentions</span></div><div><strong>+68%</strong><span>answer inclusion</span></div><div><strong>−41%</strong><span>thin-content footprint</span></div></div><div className="result-footnote">Directional results after a 6-month migration program</div></div><div className="case-study-steps">{caseStudyPhases.map((phase) => <article className="case-step" key={phase.number}><span className="case-step-number">{phase.number}</span><div><h3>{phase.title}</h3><p>{phase.text}</p></div><ArrowUpRight size={16} /></article>)}</div></div><div className="case-study-takeaway"><span><Sparkles size={16} /> The optimization principle</span><strong>Make the brand easier to recognize in isolation — and easier to recommend in context.</strong><button className="text-button" onClick={() => scrollTo("assessment")}>Find your gap <ArrowUpRight size={16} /></button></div></section>

        <section id="roi" className="roi-section"><div className="roi-header"><div><div className="eyebrow"><span className="eyebrow-line" /> Impact calculator</div><h2>What could a better<br /><em>answer footprint</em> be worth?</h2><p>Adjust the assumptions to sketch the business case for moving from traffic-first SEO to a more visible, citable GEO presence.</p></div><div className="roi-icon"><Calculator size={28} /></div></div><div className="roi-layout"><div className="roi-inputs"><div className="roi-input-head"><span>Your assumptions</span><small>Move the sliders</small></div>{([ ["sessions", "Monthly organic sessions", roiInputs.sessions, 1000, 100000, 1000, (v: number) => v.toLocaleString()], ["conversion", "Qualified conversion rate", roiInputs.conversion, 0.5, 8, 0.1, (v: number) => `${v.toFixed(1)}%`], ["value", "Average customer value", roiInputs.value, 500, 15000, 100, (v: number) => formatCurrency(v)], ["lift", "Estimated GEO lift", roiInputs.lift, 5, 80, 1, (v: number) => `${v}%`], ["investment", "Monthly GEO investment", roiInputs.investment, 1000, 20000, 500, (v: number) => formatCurrency(v)] ] as const).map(([key, label, value, min, max, step, display]) => <label className="roi-control" key={key}><span><b>{label}</b><strong>{display(value)}</strong></span><input type="range" min={min} max={max} step={step} value={value} onChange={(event) => updateRoi(key, Number(event.target.value))} /></label>)}<small className="roi-disclaimer">Planning estimate only. Replace the assumptions with your own funnel data before making investment decisions.</small></div><div className="roi-output"><div className="roi-output-label"><TrendingUp size={16} /> Estimated monthly impact</div><strong className="roi-value">{formatCurrency(roi.monthlyImpact)}</strong><p>Potential incremental revenue influenced by additional qualified demand.</p><div className="roi-stat-grid"><div><span>Incremental leads</span><b>+{roi.incrementalLeads.toLocaleString()}</b><small>/ month</small></div><div><span>Annualized upside</span><b>{formatCurrency(roi.monthlyImpact * 12)}</b><small>/ year</small></div><div><span>Payback horizon</span><b>{roiPayback} mo</b><small>at this lift</small></div></div><div className="roi-formula"><span>Model logic</span><p>{roi.currentLeads.toLocaleString()} current leads × {roiInputs.lift}% lift × {formatCurrency(roiInputs.value)} value</p></div><button className="button-primary" onClick={() => scrollTo("assessment")}>Pressure-test your readiness <ArrowUpRight size={16} /></button></div></div></section>

        <section id="audit" className="audit-section"><div className="audit-header"><div><div className="eyebrow"><span className="eyebrow-line" /> Audit generator</div><h2>Turn a vague<br /><em>gap into a plan.</em></h2><p>Work through nine practical GEO signals, mark what is already true, and generate a shareable snapshot of where to focus next.</p></div><div className="audit-summary"><div className="audit-score-ring" style={{ background: `conic-gradient(var(--lime) ${auditScore * 3.6}deg, #313a2d 0deg)` }}><div><strong>{auditScore}</strong><span>%</span></div></div><span>{auditLabel}</span></div></div>{!auditReport ? <div className="audit-workspace"><div className="audit-groups">{auditGroups.map((group) => <div className="audit-group" key={group.name}><div className="audit-group-heading"><div><span>{group.name}</span><p>{group.description}</p></div><b>{group.checks.filter((check) => auditChecks[check.id]).length}/{group.checks.length}</b></div><div className="audit-checks">{group.checks.map((check) => <button className={auditChecks[check.id] ? "audit-check checked" : "audit-check"} key={check.id} onClick={() => toggleAuditCheck(check.id)}><span className="check-box">{auditChecks[check.id] && <Check size={13} />}</span><span className="check-copy"><b>{check.title}</b><small><i className={check.priority === "High" ? "priority-high" : "priority-medium"}>{check.priority} priority</i> · {check.recommendation}</small></span></button>)}</div></div>)}</div><div className="audit-sidecard"><ClipboardCheck size={23} /><span>GEO readiness snapshot</span><strong>{auditComplete} <small>of {allAuditChecks.length}</small></strong><p>Complete the checks that are already part of your operating system. Your unfinished items become your action queue.</p><button className="button-primary" disabled={auditComplete === 0} onClick={() => setAuditReport(true)}>Generate audit report <ArrowUpRight size={16} /></button><small className="audit-side-note">Your answers stay in this browser session.</small></div></div> : <div className="audit-report"><div className="report-topline"><span><Check size={14} /> Report generated</span><div><button onClick={copyAuditSummary}><Copy size={14} /> {auditCopied ? "Copied" : "Copy summary"}</button><button onClick={() => window.print()}><Printer size={14} /> Print</button></div></div><div className="report-hero"><div><span className="report-kicker">Signal Room / GEO audit</span><h3>Your operating signal is <em>{auditLabel.toLowerCase()}</em>.</h3><p>You have marked <strong>{auditComplete} of {allAuditChecks.length}</strong> foundational signals as in place. The next gains are likely to come from the unchecked items below.</p></div><div className="report-score"><strong>{auditScore}</strong><span>/ 100</span></div></div><div className="report-breakdown">{auditGroups.map((group) => <div key={group.name}><span>{group.name}</span><b>{Math.round((group.checks.filter((check) => auditChecks[check.id]).length / group.checks.length) * 100)}%</b><i><em style={{ width: `${(group.checks.filter((check) => auditChecks[check.id]).length / group.checks.length) * 100}%` }} /></i></div>)}</div><div className="report-priority"><div><span>Recommended next focus</span><h4>{allAuditChecks.find((check) => !auditChecks[check.id])?.title ?? "Keep testing and refreshing your signal set."}</h4><p>{allAuditChecks.find((check) => !auditChecks[check.id])?.recommendation ?? "Build a regular review loop so the system stays legible as your market evolves."}</p></div><button className="reset-button" onClick={resetAudit}><RotateCcw size={15} /> Re-run audit</button></div></div>}</section>

        <section id="briefings" className="section block-section"><div className="section-heading"><div><div className="eyebrow"><span className="eyebrow-line" /> Featured briefing</div><h2>What’s worth<br /><em>knowing now.</em></h2></div><button className="circle-link" onClick={() => scrollTo("field-notes")}><ArrowUpRight size={19} /></button></div><div className="briefing-card"><div className="briefing-card-art"><div className="art-label">THE NEW<br />DISCOVERABILITY</div><div className="art-ring ring-a" /><div className="art-ring ring-b" /><div className="art-cross">+</div><span className="art-number">01</span></div><div className="briefing-content"><div className="content-meta"><span>Long read</span><span>12 min · By Aisha Khan</span></div><h3>From ranking to resonance: <em>the new job of SEO</em></h3><p>The old playbook was built for a list of blue links. The next one is built for the moment someone asks, “Who should I trust?”</p><button className="read-link">Read the briefing <ArrowUpRight size={17} /></button></div></div></section>

        <section id="voices" className="section voices-section"><div className="section-heading compact"><div><div className="eyebrow"><span className="eyebrow-line" /> The voices</div><h2>Not gurus.<br /><em>Practitioners.</em></h2></div><p className="section-intro">Ideas from people doing the work — in the messy middle between strategy, systems, and story.</p></div><div className="expert-grid">{experts.map((expert) => <article className="expert-card" key={expert.name}><div className={`expert-portrait ${expert.tone}`}><span>{expert.initials}</span><div className="portrait-grid" /></div><div className="expert-info"><div><h3>{expert.name}</h3><p>{expert.role}</p></div><ArrowUpRight size={18} /></div><div className="expert-org">{expert.org}</div></article>)}</div><button className="outline-button" onClick={() => scrollTo("field-notes")}>Browse all voices <ArrowUpRight size={16} /></button></section>

        <section id="field-notes" className="section notes-section"><div className="section-heading compact"><div><div className="eyebrow"><span className="eyebrow-line" /> Dispatches</div><h2>Small notes.<br /><em>Sharp edges.</em></h2></div><button className="filter-button"><span>All topics</span><ChevronRight size={15} /></button></div><div className="notes-list">{notes.map((note, index) => <article className="note-row" key={note.title}><div className={`note-index ${note.color}`}>0{index + 1}</div><div className="note-main"><span className="note-tag">{note.tag}</span><h3>{note.title}</h3></div><div className="note-meta"><span>{note.date}</span><span><Clock3 size={14} /> {note.time}</span></div><button className="note-arrow" aria-label={`Read ${note.title}`}><ArrowUpRight size={18} /></button></article>)}</div></section>

        <section id="research-desk" className="research-section"><div className="section-heading compact"><div><div className="eyebrow"><span className="eyebrow-line" /> Research desk</div><h2>Latest thinking.<br /><em>Sharper signals.</em></h2></div><p className="section-intro">A living library for GEO research, operator conversations, and the patterns worth carrying into your next brief.</p></div><div className="research-toolbar"><span>Browse the desk</span><div>{["All", "GEO research", "Expert insight", "SEO / GEO"].map((filter) => <button key={filter} className={researchFilter === filter ? "active" : ""} onClick={() => setResearchFilter(filter)}>{filter}</button>)}</div></div><div className="research-grid">{filteredResearch.map((post, index) => <article className={`research-card ${post.tone}`} key={post.title}><div className="research-card-top"><span>{post.type}</span><b>0{index + 1}</b></div><div className="research-card-art"><div className="research-art-line line-a" /><div className="research-art-line line-b" /><div className="research-art-dot" /></div><div className="research-card-copy"><span>{post.category} · {post.date}</span><h3>{post.title}</h3><p>{post.excerpt}</p><button className="read-link">Open piece <ArrowUpRight size={16} /></button></div></article>)}</div><div className="research-footer"><span><Send size={15} /> New: the research desk is updated with every issue.</span><button className="text-button" onClick={() => scrollTo("about")}>Get the weekly signal <ArrowUpRight size={16} /></button></div></section>

        <section id="assessment" className="assessment-section"><div className="assessment-header"><div><div className="eyebrow"><span className="eyebrow-line" /> Self-assessment</div><h2>Are you ready for<br /><em>the next search?</em></h2></div><div className="assessment-badge"><Target size={17} /> 6 signals · 3 min</div></div>{!assessmentComplete ? <div className="assessment-panel"><div className="assessment-progress"><span>0{assessmentStep + 1} / 0{assessmentQuestions.length}</span><div><i style={{ width: `${((assessmentStep) / assessmentQuestions.length) * 100}%` }} /></div><span>{currentQuestion.label}</span></div><h3>{currentQuestion.question}</h3><div className="answer-grid">{currentQuestion.options.map((option, index) => <button key={option} className="answer-card" onClick={() => answerAssessment(index)}><span>{String.fromCharCode(65 + index)}</span>{option}<ChevronRight size={17} /></button>)}</div><p className="assessment-note">Choose the answer that feels most true today. This is a directional signal, not a grade.</p></div> : <div className="assessment-result"><div className="result-intro"><span className="result-kicker"><Check size={14} /> Assessment complete</span><h3>Your signal is <em>{scoreLabel(Math.max(seoScore, geoScore)).toLowerCase()}</em>.</h3><p>Here’s where your discoverability system is strongest — and where a small, deliberate shift could compound.</p></div><div className="score-grid"><div className="score-card seo-score"><div className="score-ring" style={{ background: `conic-gradient(var(--lime) ${seoScore * 3.6}deg, #2b3025 0deg)` }}><div><strong>{seoScore}</strong><span>/ 100</span></div></div><div><b>SEO readiness</b><small>{scoreLabel(seoScore)}</small></div></div><div className="score-card geo-score"><div className="score-ring" style={{ background: `conic-gradient(var(--coral) ${geoScore * 3.6}deg, #392824 0deg)` }}><div><strong>{geoScore}</strong><span>/ 100</span></div></div><div><b>GEO readiness</b><small>{scoreLabel(geoScore)}</small></div></div></div><div className="result-footer"><span><Sparkles size={15} /> Your next move: make your expertise easier to <strong>recognize, retrieve, and repeat.</strong></span><button className="reset-button" onClick={resetAssessment}><RotateCcw size={15} /> Retake</button></div></div>}</section>

        <section id="about" className="subscribe-section"><div className="subscribe-mark"><CircleArrowOutUpRight size={34} /></div><div><div className="eyebrow"><span className="eyebrow-line" /> The signal, delivered</div><h2>Good thinking,<br /><em>once a week.</em></h2><p>One thoughtful dispatch on SEO, GEO, and building a brand that machines can understand — and people can feel.</p></div><form className="subscribe-form" onSubmit={handleNewsletterSubmit}><div className="fake-input"><input aria-label="Email address" type="email" required placeholder="Your email address" value={newsletterEmail} onChange={(event) => setNewsletterEmail(event.target.value)} />{subscribed ? <Sparkles size={18} /> : <button type="submit" aria-label="Subscribe"><ArrowUpRight size={20} /></button>}</div><small>{subscribed ? "Welcome to the room. Check your inbox for a welcome note." : "No noise. Unsubscribe whenever."}</small></form></section>
      </main>

      <footer className="site-footer"><button className="wordmark footer-mark" onClick={() => scrollTo("top")}><span className="wordmark-dot" />signal<span>room</span></button><span>© 2026 Signal Room. Made for the curious.</span><div className="footer-links"><a href="#about">Instagram</a><a href="#about">LinkedIn</a><a href="#about">RSS</a></div></footer>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
