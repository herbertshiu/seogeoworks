import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ArrowLeft,
  ArrowUpRight,
  Check,
  ChevronRight,
  CircleArrowOutUpRight,
  Clock3,
  Menu,
  Play,
  Search,
  Sparkles,
  Target,
  RotateCcw,
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

const assessmentQuestions = [
  { id: "foundation", label: "Foundations", question: "How consistently does your site earn organic clicks for your priority topics?", options: ["We rarely appear", "Sometimes, but inconsistently", "We have a reliable footprint", "We are a category reference"], seo: [0, 1, 2, 3], geo: [0, 1, 2, 2] },
  { id: "content", label: "Content clarity", question: "Can a reader (or crawler) quickly understand who you help and what you know?", options: ["It is hard to tell", "It depends on the page", "The message is mostly clear", "Our point of view is unmistakable"], seo: [0, 1, 2, 3], geo: [0, 1, 2, 3] },
  { id: "proof", label: "Proof & authority", question: "How visible are your first-hand expertise, sources, and named contributors?", options: ["Mostly anonymous", "Some proof exists", "Proof is part of our process", "Our experts are cited and trusted"], seo: [0, 1, 2, 3], geo: [0, 1, 2, 3] },
  { id: "structure", label: "Machine-readable", question: "How much of your important context is structured for machines to parse and connect?", options: ["We have not considered it", "Basic metadata only", "Structured content is in progress", "Our entities and relationships are explicit"], seo: [0, 1, 2, 3], geo: [0, 1, 2, 3] },
  { id: "distribution", label: "Distributed presence", question: "Does your brand show up in the sources, communities, and conversations your audience trusts?", options: ["Only on our own site", "A few scattered mentions", "We show up in relevant places", "We are part of the wider conversation"], seo: [0, 1, 2, 2], geo: [0, 1, 2, 3] },
  { id: "measurement", label: "Measurement", question: "Can you tell whether search visibility is creating qualified demand, not just traffic?", options: ["We mostly guess", "We track rankings or traffic", "We connect visibility to outcomes", "We measure attention, influence, and action"], seo: [0, 1, 2, 3], geo: [0, 1, 2, 3] },
];

const scoreLabel = (score: number) => score < 40 ? "Signal forming" : score < 70 ? "Signal building" : "Signal leading";

function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [subscribed, setSubscribed] = useState(false);
  const [assessmentStep, setAssessmentStep] = useState(0);
  const [assessmentAnswers, setAssessmentAnswers] = useState<number[]>([]);
  const [assessmentComplete, setAssessmentComplete] = useState(false);

  const handleSubscribe = () => setSubscribed(true);
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
          <button onClick={() => scrollTo("briefings")}>Briefings</button><button onClick={() => scrollTo("voices")}>Voices</button><button onClick={() => scrollTo("field-notes")}>Field notes</button><button onClick={() => scrollTo("about")}>About</button>
        </nav>
        <button className="header-cta" onClick={handleSubscribe}>{subscribed ? "You’re in" : "Get the signal"}<ArrowUpRight size={16} /></button>
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

        <section id="briefings" className="section block-section"><div className="section-heading"><div><div className="eyebrow"><span className="eyebrow-line" /> Featured briefing</div><h2>What’s worth<br /><em>knowing now.</em></h2></div><button className="circle-link" onClick={() => scrollTo("field-notes")}><ArrowUpRight size={19} /></button></div><div className="briefing-card"><div className="briefing-card-art"><div className="art-label">THE NEW<br />DISCOVERABILITY</div><div className="art-ring ring-a" /><div className="art-ring ring-b" /><div className="art-cross">+</div><span className="art-number">01</span></div><div className="briefing-content"><div className="content-meta"><span>Long read</span><span>12 min · By Aisha Khan</span></div><h3>From ranking to resonance: <em>the new job of SEO</em></h3><p>The old playbook was built for a list of blue links. The next one is built for the moment someone asks, “Who should I trust?”</p><button className="read-link">Read the briefing <ArrowUpRight size={17} /></button></div></div></section>

        <section id="voices" className="section voices-section"><div className="section-heading compact"><div><div className="eyebrow"><span className="eyebrow-line" /> The voices</div><h2>Not gurus.<br /><em>Practitioners.</em></h2></div><p className="section-intro">Ideas from people doing the work — in the messy middle between strategy, systems, and story.</p></div><div className="expert-grid">{experts.map((expert) => <article className="expert-card" key={expert.name}><div className={`expert-portrait ${expert.tone}`}><span>{expert.initials}</span><div className="portrait-grid" /></div><div className="expert-info"><div><h3>{expert.name}</h3><p>{expert.role}</p></div><ArrowUpRight size={18} /></div><div className="expert-org">{expert.org}</div></article>)}</div><button className="outline-button" onClick={() => scrollTo("field-notes")}>Browse all voices <ArrowUpRight size={16} /></button></section>

        <section id="field-notes" className="section notes-section"><div className="section-heading compact"><div><div className="eyebrow"><span className="eyebrow-line" /> Dispatches</div><h2>Small notes.<br /><em>Sharp edges.</em></h2></div><button className="filter-button"><span>All topics</span><ChevronRight size={15} /></button></div><div className="notes-list">{notes.map((note, index) => <article className="note-row" key={note.title}><div className={`note-index ${note.color}`}>0{index + 1}</div><div className="note-main"><span className="note-tag">{note.tag}</span><h3>{note.title}</h3></div><div className="note-meta"><span>{note.date}</span><span><Clock3 size={14} /> {note.time}</span></div><button className="note-arrow" aria-label={`Read ${note.title}`}><ArrowUpRight size={18} /></button></article>)}</div></section>

        <section id="assessment" className="assessment-section"><div className="assessment-header"><div><div className="eyebrow"><span className="eyebrow-line" /> Self-assessment</div><h2>Are you ready for<br /><em>the next search?</em></h2></div><div className="assessment-badge"><Target size={17} /> 6 signals · 3 min</div></div>{!assessmentComplete ? <div className="assessment-panel"><div className="assessment-progress"><span>0{assessmentStep + 1} / 0{assessmentQuestions.length}</span><div><i style={{ width: `${((assessmentStep) / assessmentQuestions.length) * 100}%` }} /></div><span>{currentQuestion.label}</span></div><h3>{currentQuestion.question}</h3><div className="answer-grid">{currentQuestion.options.map((option, index) => <button key={option} className="answer-card" onClick={() => answerAssessment(index)}><span>{String.fromCharCode(65 + index)}</span>{option}<ChevronRight size={17} /></button>)}</div><p className="assessment-note">Choose the answer that feels most true today. This is a directional signal, not a grade.</p></div> : <div className="assessment-result"><div className="result-intro"><span className="result-kicker"><Check size={14} /> Assessment complete</span><h3>Your signal is <em>{scoreLabel(Math.max(seoScore, geoScore)).toLowerCase()}</em>.</h3><p>Here’s where your discoverability system is strongest — and where a small, deliberate shift could compound.</p></div><div className="score-grid"><div className="score-card seo-score"><div className="score-ring" style={{ background: `conic-gradient(var(--lime) ${seoScore * 3.6}deg, #2b3025 0deg)` }}><div><strong>{seoScore}</strong><span>/ 100</span></div></div><div><b>SEO readiness</b><small>{scoreLabel(seoScore)}</small></div></div><div className="score-card geo-score"><div className="score-ring" style={{ background: `conic-gradient(var(--coral) ${geoScore * 3.6}deg, #392824 0deg)` }}><div><strong>{geoScore}</strong><span>/ 100</span></div></div><div><b>GEO readiness</b><small>{scoreLabel(geoScore)}</small></div></div></div><div className="result-footer"><span><Sparkles size={15} /> Your next move: make your expertise easier to <strong>recognize, retrieve, and repeat.</strong></span><button className="reset-button" onClick={resetAssessment}><RotateCcw size={15} /> Retake</button></div></div>}</section>

        <section id="about" className="subscribe-section"><div className="subscribe-mark"><CircleArrowOutUpRight size={34} /></div><div><div className="eyebrow"><span className="eyebrow-line" /> The signal, delivered</div><h2>Good thinking,<br /><em>once a week.</em></h2><p>One thoughtful dispatch on SEO, GEO, and building a brand that machines can understand — and people can feel.</p></div><div className="subscribe-form"><div className="fake-input"><span>{subscribed ? "Welcome to the room." : "Your email address"}</span>{subscribed ? <Sparkles size={18} /> : <button aria-label="Subscribe" onClick={handleSubscribe}><ArrowUpRight size={20} /></button>}</div><small>{subscribed ? "Check your inbox for a welcome note." : "No noise. Unsubscribe whenever."}</small></div></section>
      </main>

      <footer className="site-footer"><button className="wordmark footer-mark" onClick={() => scrollTo("top")}><span className="wordmark-dot" />signal<span>room</span></button><span>© 2026 Signal Room. Made for the curious.</span><div className="footer-links"><a href="#about">Instagram</a><a href="#about">LinkedIn</a><a href="#about">RSS</a></div></footer>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
