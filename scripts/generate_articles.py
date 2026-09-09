#!/usr/bin/env python3
"""Generate Signal Room field-guide articles for keyword targets."""

from __future__ import annotations

import hashlib
import html
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYWORDS_FILE = ROOT / "keywords.txt"
ARTICLES_DIR = ROOT / "public" / "articles"
MANIFEST = ROOT / "public" / "articles" / "manifest.json"
SITEMAP = ROOT / "public" / "sitemap.xml"
TODAY = date.today().isoformat()

CATEGORY_HINTS = [
    ("seo", ["seo", "sem", "ppc", "google ads", "adwords", "百度", "谷歌", "search engine", "反向連結", "backlink", "收录", "ranking", "排名", "first page", "hkgseo", "you find", "youfind"]),
    ("kol", ["kol", "influencer", "意見領袖", "youtuber", "ig ", "ig廣告", "ig自介", "ig個人", "ig 演算法", "ig演算法", "ig落廣告", "ig賣廣告", "ig 放大鏡", "instagram", "tiktok", "微博"]),
    ("social", ["facebook", "社交媒體", "social media", "linkedin", "linekdin", "linedin", "linkedln", "linkeidn", "linkdein", "pinterest", "網上推廣", "網上廣告", "pr ", "pr公司", "公關"]),
    ("it", ["it ", "it-", "cloud", "managed", "outsourcing", "consulting", "consultancy", "infrastructure", "crm", "software", "web app", "web application", "app development", "wordpress", "magento", "dynamic website"]),
    ("design", ["graphic", "design", "branding", "brand ", "logo", "ux ", "creative", "web design", "website design"]),
    ("logistics", ["logistics", "logistic", "freight", "shipping", "fulfillment", "3pl", "forwarder", "forwarding", "物流", "air freight"]),
    ("hr", ["hr ", "human", "outsourcing hr", "telemarketing", "call center", "bpo"]),
    ("agency", ["agency", "marketing", "digital", "廣告", "營銷", "行銷", "數碼", "media agency", "advertising"]),
]


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKC", text.strip().lower())
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^\w\u4e00-\u9fff\-]+", "", text, flags=re.UNICODE)
    text = re.sub(r"-+", "-", text).strip("-")
    if not text:
        text = "article-" + hashlib.sha1(text.encode()).hexdigest()[:8]
    # Ensure uniqueness for near-duplicates later via caller
    return text[:90]


def categorize(keyword: str) -> str:
    k = keyword.lower()
    for name, hints in CATEGORY_HINTS:
        for h in hints:
            if h.lower() in k:
                return name
    return "general"


def seed(keyword: str) -> int:
    return int(hashlib.sha1(keyword.encode("utf-8")).hexdigest()[:8], 16)


def pick(items: list[str], s: int, offset: int = 0) -> str:
    return items[(s + offset) % len(items)]


def escape(s: str) -> str:
    return html.escape(s, quote=True)


def title_for(keyword: str, category: str) -> str:
    templates = {
        "seo": f"{keyword}: a practical field guide to search visibility",
        "kol": f"{keyword}: how brands earn attention with creators",
        "social": f"{keyword}: a working brief for social discovery",
        "it": f"{keyword}: choosing operators who make systems usable",
        "design": f"{keyword}: making brands easier to recognize",
        "logistics": f"{keyword}: the fulfillment layer behind visible brands",
        "hr": f"{keyword}: people systems that support growth",
        "agency": f"{keyword}: how to evaluate partners without the noise",
        "general": f"{keyword}: a Signal Room field guide",
    }
    t = templates.get(category, templates["general"])
    if len(t) > 70:
        t = f"{keyword} — Signal Room field guide"
    return t


def description_for(keyword: str, category: str) -> str:
    base = {
        "seo": f"A practical Signal Room guide to {keyword}: what matters for rankings, citations, and qualified demand in Hong Kong and beyond.",
        "kol": f"A Signal Room field note on {keyword}: how creator partnerships become recognizable, citable brand signals.",
        "social": f"A Signal Room briefing on {keyword}: social distribution, proof, and measurement that survive algorithm changes.",
        "it": f"A Signal Room guide to {keyword}: how to choose technical partners that keep search and product systems coherent.",
        "design": f"A Signal Room look at {keyword}: visual systems, brand clarity, and the signals that make a company memorable.",
        "logistics": f"A Signal Room briefing on {keyword}: operations that support ecommerce visibility and customer trust.",
        "hr": f"A Signal Room guide to {keyword}: people infrastructure that keeps growth and brand delivery aligned.",
        "agency": f"A Signal Room field guide to {keyword}: how to brief, compare, and measure marketing partners.",
        "general": f"A Signal Room field guide to {keyword}: context, evaluation criteria, and next steps for operators.",
    }
    d = base.get(category, base["general"])
    if len(d) < 120:
        d += " Written for teams who want clarity over hype."
    return d[:160]


def body_sections(keyword: str, category: str) -> list[tuple[str, str]]:
    s = seed(keyword)
    kw = keyword

    intros = [
        f"Searchers looking up <strong>{escape(kw)}</strong> are rarely hunting for a slogan. They want a usable answer: who is credible, what to compare, and what to do next.",
        f"When someone types <strong>{escape(kw)}</strong>, they are usually mid-decision. The job of a field guide is to reduce ambiguity without pretending every market is identical.",
        f"<strong>{escape(kw)}</strong> sits at the intersection of discovery and trust. This note maps the signals that help a brand get found — and chosen.",
    ]

    why = [
        f"Demand around <strong>{escape(kw)}</strong> grows when categories get noisy. Buyers need a filter: proof, process, and a point of view that machines and people can both parse.",
        f"Teams researching <strong>{escape(kw)}</strong> often compare vendors by surface claims. The durable differentiator is evidence: named expertise, clear scope, and outcomes that can be verified.",
        f"Visibility for <strong>{escape(kw)}</strong> is not only a ranking problem. It is a recognition problem — can an answer engine, a buyer, or a partner explain what you do without guessing?",
    ]

    lenses = {
        "seo": [
            ("What searchers actually need", f"For queries like <strong>{escape(kw)}</strong>, useful pages define the category, show local context when relevant, and make next steps obvious. Thin definition pages lose to sources with examples, criteria, and named operators."),
            ("Signals that compound", f"Treat <strong>{escape(kw)}</strong> as a topic cluster, not a one-off post. Connect definitions, comparisons, case patterns, and FAQs so crawlers and answer engines can retrieve a coherent body of knowledge."),
            ("Measurement beyond vanity", f"Track rankings for <strong>{escape(kw)}</strong>, but also branded searches, assisted conversions, and whether your page is cited in summaries. Traffic without qualified conversations is incomplete proof."),
        ],
        "kol": [
            ("Creator fit over follower count", f"Buying reach for <strong>{escape(kw)}</strong> without audience fit creates empty impressions. Prioritize creators whose content already answers the questions your buyers ask."),
            ("Proof trail", f"Strong <strong>{escape(kw)}</strong> work leaves a trail: briefs, disclosed partnerships, measurable outcomes, and content that still makes sense after the campaign ends."),
            ("From mention to memory", f"A KOL post should make your brand easier to recognize later — in search, in social, and in answer engines. That means consistent naming, clear offers, and reusable proof."),
        ],
        "social": [
            ("Distribution is part of SEO now", f"Pages about <strong>{escape(kw)}</strong> should connect owned content to the channels where your audience already trusts recommendations."),
            ("Creative that can be retrieved", f"Write for humans first, but structure posts and landing pages so machines can extract entities, offers, and claims related to <strong>{escape(kw)}</strong>."),
            ("Budget with a hypothesis", f"Whether you are evaluating fees or formats for <strong>{escape(kw)}</strong>, start with a testable hypothesis: who, where, what proof, and what decision you want to influence."),
        ],
        "it": [
            ("Operators, not buzzwords", f"Buyers comparing <strong>{escape(kw)}</strong> options need clarity on scope, SLAs, security posture, and how work will be documented for the next team."),
            ("Systems that stay legible", f"Good technical partners leave searchable documentation, named owners, and integrations that do not trap your brand data."),
            ("Tie tech to discovery", f"Site speed, structured data, and clean information architecture all affect whether content about <strong>{escape(kw)}</strong> can be found and trusted."),
        ],
        "design": [
            ("Recognition is a search asset", f"Visual systems connected to <strong>{escape(kw)}</strong> should make the brand identifiable in isolation — on a SERP thumbnail, a social card, or an AI citation snippet."),
            ("Consistency beats novelty", f"Teams shopping for <strong>{escape(kw)}</strong> often over-index on aesthetics. Ask how the system scales across web, ads, and documents without dilution."),
            ("Make meaning explicit", f"Pair design with language: clear naming, accessible alt text, and brand guidelines that help both people and machines resolve who you are."),
        ],
        "logistics": [
            ("Trust is operational", f"Ecommerce brands researching <strong>{escape(kw)}</strong> are buying reliability as much as rates. Visibility of process reduces support load and review risk."),
            ("Content that matches reality", f"If you publish claims around <strong>{escape(kw)}</strong>, make SLAs, geographies, and constraints explicit so searchers are not misled."),
            ("Connect ops to marketing", f"Fulfillment quality shows up in reviews and return rates — signals that influence both conversion and long-term search reputation."),
        ],
        "hr": [
            ("People systems as brand infrastructure", f"Queries like <strong>{escape(kw)}</strong> often come from companies scaling faster than their internal capacity. Clarity on compliance, culture fit, and handover matters."),
            ("Evaluate beyond price", f"Compare <strong>{escape(kw)}</strong> providers on documentation quality, escalation paths, and how they protect employer brand."),
            ("Knowledge that stays", f"Outsourced work should leave searchable playbooks so institutional knowledge does not vanish when a contract ends."),
        ],
        "agency": [
            ("Brief before you buy", f"A sharp brief for <strong>{escape(kw)}</strong> forces agencies to respond with method, not moodboards alone."),
            ("Compare like operators", f"Ask for named leads, reporting cadence, and examples relevant to <strong>{escape(kw)}</strong> — not generic case studies from unrelated markets."),
            ("Define the win", f"Agree what success looks like for <strong>{escape(kw)}</strong>: pipeline, citations, creative output, or operational coverage — then instrument it."),
        ],
        "general": [
            ("Start with the decision", f"People searching <strong>{escape(kw)}</strong> usually need a decision framework. Give criteria, trade-offs, and examples before pitching a service."),
            ("Make expertise visible", f"Name the people, process, and proof behind <strong>{escape(kw)}</strong>. Anonymous authority is harder for buyers and answer engines to trust."),
            ("Keep the page useful after the click", f"A field guide on <strong>{escape(kw)}</strong> should still help when the reader returns six months later. Prefer durable principles over recycled hype."),
        ],
    }

    checklist_items = [
        f"Define what a good outcome looks like for <strong>{escape(kw)}</strong> in one sentence.",
        f"List three proof points a skeptical buyer would accept when evaluating <strong>{escape(kw)}</strong>.",
        f"Map the pages, profiles, and partners that should corroborate your story around <strong>{escape(kw)}</strong>.",
        f"Decide which metrics prove progress beyond vanity for <strong>{escape(kw)}</strong>.",
        f"Assign an owner who will refresh the <strong>{escape(kw)}</strong> brief quarterly.",
    ]

    sections = [
        ("Why this query matters", pick(intros, s) + " " + pick(why, s, 1)),
    ]
    for heading, para in lenses.get(category, lenses["general"]):
        sections.append((heading, para))

    # Special handling for crack/piracy-adjacent keywords without enabling abuse
    if "破解" in kw or "crack" in kw.lower():
        sections = [
            ("Why this query matters", f"Searches for <strong>{escape(kw)}</strong> often mix curiosity with risk. This field guide focuses on legitimate, durable ways to use AI and search tools — not unauthorized access, cracked software, or account abuse."),
            ("Prefer official access", f"Paid plans, business seats, and documented APIs keep data, compliance, and support intact. Shortcuts marketed around <strong>{escape(kw)}</strong> frequently expose teams to malware, credential theft, and policy bans."),
            ("Build capability, not dependency on loopholes", f"Train teams to write better prompts, structure content for retrieval, and measure outcomes. That compounds longer than chasing unofficial workarounds tied to <strong>{escape(kw)}</strong>."),
            ("If you are evaluating AI for SEO and GEO", f"Use sanctioned tools, keep human review in the loop, and publish original evidence. Search visibility still rewards clarity and trust — not fragile hacks associated with <strong>{escape(kw)}</strong>."),
        ]

    sections.append(
        (
            "A practical checklist",
            "<ul>" + "".join(f"<li>{checklist_items[(s + i) % len(checklist_items)]}</li>" for i in range(5)) + "</ul>",
        )
    )
    sections.append(
        (
            "Bottom line",
            f"Treat <strong>{escape(kw)}</strong> as a prompt to make your expertise easier to find, verify, and repeat. Signal Room exists to help operators turn noisy categories into clear next moves — not louder claims.",
        )
    )
    return sections


def render_article(keyword: str, slug: str, related: list[tuple[str, str]]) -> str:
    category = categorize(keyword)
    title = title_for(keyword, category)
    description = description_for(keyword, category)
    sections = body_sections(keyword, category)
    related_html = "".join(
        f'<li><a href="/articles/{escape(rslug)}.html">{escape(rkw)}</a></li>' for rkw, rslug in related
    )
    section_html = "".join(
        f"<section><h2>{escape(h) if not h.startswith('A practical') else h}</h2><p>{p}</p></section>"
        if not p.startswith("<ul>")
        else f"<section><h2>{escape(h)}</h2>{p}</section>"
        for h, p in sections
    )
    # fix h2 for checklist - already escaped in loop awkwardly; rebuild cleanly
    section_html = ""
    for h, p in sections:
        if p.startswith("<ul>"):
            section_html += f"<section><h2>{escape(h)}</h2>{p}</section>"
        else:
            section_html += f"<section><h2>{escape(h)}</h2><p>{p}</p></section>"

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#11120f" />
    <title>{escape(title)}</title>
    <meta name="description" content="{escape(description)}" />
    <link rel="canonical" href="https://www.seogeoworks.hk/articles/{escape(slug)}.html" />
    <link rel="sitemap" type="application/xml" title="Sitemap" href="https://www.seogeoworks.hk/sitemap.xml" />
    <meta property="og:type" content="article" />
    <meta property="og:site_name" content="Signal Room" />
    <meta property="og:url" content="https://www.seogeoworks.hk/articles/{escape(slug)}.html" />
    <meta property="og:title" content="{escape(title)}" />
    <meta property="og:description" content="{escape(description)}" />
    <meta property="og:image" content="https://www.seogeoworks.hk/og.png" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{escape(title)}" />
    <meta name="twitter:description" content="{escape(description)}" />
    <meta name="twitter:image" content="https://www.seogeoworks.hk/og.png" />
    <link rel="icon" href="/favicon.ico" sizes="any" />
    <link rel="icon" type="image/png" href="/favicon.png" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap" rel="stylesheet" />
    <script src="https://analytics.ahrefs.com/analytics.js" data-key="uCLpAG8kpc6h2p4Eofk2cg" async></script>
    <style>
      :root {{ --bg:#11120f; --ink:#f4f1ea; --muted:#b0b2a7; --lime:#d5f7ac; --line:#2a2d26; }}
      * {{ box-sizing:border-box; }}
      body {{ margin:0; background:var(--bg); color:var(--ink); font:400 16px/1.6 "DM Sans",sans-serif; }}
      a {{ color:var(--lime); }}
      .wrap {{ max-width:760px; margin:0 auto; padding:28px 6vw 80px; }}
      .top {{ display:flex; justify-content:space-between; gap:16px; align-items:center; margin-bottom:42px; font:12px "DM Mono",monospace; color:var(--muted); }}
      .top a {{ color:var(--muted); text-decoration:none; }}
      .eyebrow {{ color:var(--lime); font:12px "DM Mono",monospace; letter-spacing:.04em; text-transform:uppercase; }}
      h1 {{ margin:14px 0 18px; font:700 clamp(32px,5vw,52px)/1.05 "Playfair Display",serif; letter-spacing:-.03em; }}
      .lede {{ color:var(--muted); font-size:18px; margin:0 0 34px; }}
      section {{ padding:22px 0; border-top:1px solid var(--line); }}
      h2 {{ margin:0 0 12px; font:600 24px/1.2 "Playfair Display",serif; }}
      p, li {{ color:#d7d5cc; }}
      ul {{ padding-left:1.2em; }}
      .related {{ margin-top:40px; padding-top:24px; border-top:1px solid var(--line); }}
      .related h2 {{ font-size:20px; }}
      .related ul {{ list-style:none; padding:0; display:grid; gap:10px; }}
      .related a {{ text-decoration:none; }}
      footer {{ margin-top:48px; color:var(--muted); font-size:13px; }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <div class="top"><a href="/">← Signal Room</a><span>Field guide · {TODAY}</span></div>
      <div class="eyebrow">Signal Room / {escape(category)}</div>
      <h1>{escape(title)}</h1>
      <p class="lede">{escape(description)}</p>
      <article>
        {section_html}
      </article>
      <aside class="related">
        <h2>Related field guides</h2>
        <ul>
          {related_html}
        </ul>
      </aside>
      <footer>
        <p>© {date.today().year} Signal Room. <a href="/">Home</a> · <a href="/articles/">All guides</a> · <a href="/sitemap.xml">Sitemap</a></p>
      </footer>
    </div>
  </body>
</html>
"""


def write_index(entries: list[dict]) -> None:
    items = "\n".join(
        f'<li><a href="/articles/{escape(e["slug"])}.html"><strong>{escape(e["keyword"])}</strong><span>{escape(e["title"])}</span></a></li>'
        for e in entries
    )
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Field guides — Signal Room</title>
  <meta name="description" content="Signal Room field guides on SEO, GEO, KOL, marketing, and the operators reshaping how brands get found." />
  <link rel="canonical" href="https://www.seogeoworks.hk/articles/" />
  <link rel="icon" href="/favicon.ico" />
  <script src="https://analytics.ahrefs.com/analytics.js" data-key="uCLpAG8kpc6h2p4Eofk2cg" async></script>
  <style>
    body{{margin:0;background:#11120f;color:#f4f1ea;font:16px/1.5 "DM Sans",sans-serif}}
    .wrap{{max-width:900px;margin:0 auto;padding:28px 6vw 80px}}
    a{{color:#d5f7ac;text-decoration:none}}
    h1{{font:700 42px/1.1 "Playfair Display",serif}}
    ul{{list-style:none;padding:0;margin:30px 0;display:grid;gap:12px}}
    li a{{display:grid;gap:4px;padding:14px 0;border-bottom:1px solid #2a2d26}}
    span{{color:#b0b2a7;font-size:14px}}
  </style>
</head>
<body>
  <div class="wrap">
    <p><a href="/">← Signal Room</a></p>
    <h1>Field guides</h1>
    <p>{len(entries)} practical notes for search, social, and modern brand discovery.</p>
    <ul>
      {items}
    </ul>
  </div>
</body>
</html>
"""
    (ARTICLES_DIR / "index.html").write_text(html_doc, encoding="utf-8")


def write_sitemap(entries: list[dict]) -> None:
    urls = [
        ("https://www.seogeoworks.hk/", "1.0"),
        ("https://www.seogeoworks.hk/articles/", "0.9"),
    ]
    for e in entries:
        urls.append((f"https://www.seogeoworks.hk/articles/{e['slug']}.html", "0.7"))
    body = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq><priority>{p}</priority></url>"
        for u, p in urls
    )
    SITEMAP.write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n',
        encoding="utf-8",
    )


def main() -> None:
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    keywords = [k.strip() for k in KEYWORDS_FILE.read_text(encoding="utf-8").splitlines() if k.strip()]
    # unique slug map
    slug_map: dict[str, str] = {}
    used: set[str] = set()
    for kw in keywords:
        base = slugify(kw)
        slug = base
        n = 2
        while slug in used:
            slug = f"{base}-{n}"
            n += 1
        used.add(slug)
        slug_map[kw] = slug

    entries: list[dict] = []
    kw_list = list(slug_map.keys())
    for i, kw in enumerate(kw_list):
        slug = slug_map[kw]
        related = []
        for j in range(1, 4):
            rk = kw_list[(i + j * 17) % len(kw_list)]
            if rk != kw:
                related.append((rk, slug_map[rk]))
        html_doc = render_article(kw, slug, related[:3])
        (ARTICLES_DIR / f"{slug}.html").write_text(html_doc, encoding="utf-8")
        entries.append(
            {
                "keyword": kw,
                "slug": slug,
                "title": title_for(kw, categorize(kw)),
                "category": categorize(kw),
            }
        )

    write_index(entries)
    write_sitemap(entries)
    MANIFEST.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"generated {len(entries)} articles")


if __name__ == "__main__":
    main()
