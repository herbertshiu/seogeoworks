#!/usr/bin/env python3
"""Write citeable authority pages that support Domain Rating growth.

These pages do not create backlinks by themselves. They give sister sites,
partners, and journalists stable URLs worth linking to — and strengthen
entity clarity for crawlers and answer engines.
"""

from __future__ import annotations

import html
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
TODAY = date.today().isoformat()


def escape(s: str) -> str:
    return html.escape(s, quote=True)


SHELL_CSS = """
:root { --bg:#11120f; --ink:#f4f1ea; --muted:#b0b2a7; --lime:#d5f7ac; --line:#2a2d26; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font:400 16px/1.65 "DM Sans",sans-serif; }
a { color:var(--lime); }
.wrap { max-width:760px; margin:0 auto; padding:28px 6vw 80px; }
.top { display:flex; justify-content:space-between; gap:16px; align-items:center; margin-bottom:42px; font:12px "DM Mono",monospace; color:var(--muted); }
.top a { color:var(--muted); text-decoration:none; }
.eyebrow { color:var(--lime); font:12px "DM Mono",monospace; letter-spacing:.04em; text-transform:uppercase; }
h1 { margin:14px 0 18px; font:700 clamp(32px,5vw,52px)/1.05 "Playfair Display",serif; letter-spacing:-.03em; }
h2 { margin:36px 0 12px; font:600 24px/1.2 "Playfair Display",serif; }
.lede { color:var(--muted); font-size:18px; margin:0 0 28px; }
p, li { color:#d7d5cc; }
ul { padding-left:1.2em; }
.card-grid { display:grid; gap:14px; margin:28px 0; }
.card-grid a { display:block; padding:18px 0; border-bottom:1px solid var(--line); text-decoration:none; }
.card-grid strong { display:block; color:var(--ink); margin-bottom:4px; }
.card-grid span { color:var(--muted); font-size:14px; }
.check li { margin:0 0 10px; }
footer { margin-top:48px; color:var(--muted); font-size:13px; }
"""


def page(
    *,
    path: Path,
    title: str,
    description: str,
    canonical: str,
    eyebrow: str,
    h1: str,
    lede: str,
    body: str,
    schema: str | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema_block = f"\n    <script type=\"application/ld+json\">\n{schema}\n    </script>" if schema else ""
    path.write_text(
        f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#11120f" />
    <title>{escape(title)}</title>
    <meta name="description" content="{escape(description)}" />
    <link rel="canonical" href="{escape(canonical)}" />
    <link rel="alternate" hreflang="en" href="{escape(canonical)}" />
    <link rel="alternate" hreflang="x-default" href="{escape(canonical)}" />
    <meta property="og:type" content="article" />
    <meta property="og:site_name" content="seogeoworks" />
    <meta property="og:url" content="{escape(canonical)}" />
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
    <style>{SHELL_CSS}</style>{schema_block}
  </head>
  <body>
    <div class="wrap">
      <div class="top"><a href="/">← seogeoworks</a><span>Updated {TODAY}</span></div>
      <div class="eyebrow">{escape(eyebrow)}</div>
      <h1>{escape(h1)}</h1>
      <p class="lede">{escape(lede)}</p>
      {body}
      <footer>
        <p>© {date.today().year} seogeoworks.
          <a href="/">Home</a> ·
          <a href="/about/">About</a> ·
          <a href="/resources/">Resources</a> ·
          <a href="/articles/">Field guides</a> ·
          <a href="/contact/">Contact</a>
        </p>
      </footer>
    </div>
  </body>
</html>
""",
        encoding="utf-8",
    )


def write_all(topic_links: list[tuple[str, str, str]] | None = None) -> list[tuple[str, str]]:
    """Write authority pages. Returns (url, priority) pairs for sitemap."""
    urls: list[tuple[str, str]] = []

    about_schema = """      {
        "@context": "https://schema.org",
        "@type": "AboutPage",
        "@id": "https://www.seogeoworks.hk/about/#page",
        "url": "https://www.seogeoworks.hk/about/",
        "name": "About seogeoworks",
        "description": "What seogeoworks is, who it is for, and how it connects to SEO and GEO practice in Hong Kong.",
        "isPartOf": { "@id": "https://www.seogeoworks.hk/#website" },
        "about": { "@id": "https://www.seogeoworks.hk/#organization" },
        "dateModified": "%s"
      }""" % TODAY

    page(
        path=PUBLIC / "about" / "index.html",
        title="About seogeoworks — independent SEO & GEO field guide",
        description="seogeoworks is an independent Hong Kong field guide to SEO, GEO, and modern discoverability — practical criteria, not marketing fluff.",
        canonical="https://www.seogeoworks.hk/about/",
        eyebrow="seogeoworks / about",
        h1="A field guide, not a brochure.",
        lede="seogeoworks documents how brands become findable, understandable, and memorable in search and answer engines — with practical criteria operators can verify.",
        schema=about_schema,
        body="""
      <h2>What we publish</h2>
      <p>Bilingual field guides, comparison frameworks, and readiness checklists for SEO and generative engine optimization (GEO). The focus is Hong Kong and regional operators who need clear evaluation criteria — not generic agency copy.</p>
      <h2>How to use this site</h2>
      <ul>
        <li>Start with <a href="/resources/seo-vs-geo.html">SEO vs GEO</a> if you need a shared vocabulary with your team.</li>
        <li>Run the <a href="/resources/geo-readiness-checklist.html">GEO readiness checklist</a> before a redesign or content program.</li>
        <li>Browse <a href="/articles/">field guides</a> when you are comparing partners, pricing models, or category terms.</li>
      </ul>
      <h2>Related practice</h2>
      <p>seogeoworks is editorially independent. For hands-on SEO / GEO consulting, see <a href="https://www.seogeoconsulting.hk/" rel="noopener">seogeoconsulting.hk</a>. For full-service digital marketing and IT delivery in Hong Kong and the Greater Bay Area, see <a href="https://itehk.com.hk/" rel="noopener">itehk.com.hk</a>.</p>
      <h2>Editorial standard</h2>
      <p>We prefer named definitions, verifiable checks, and explicit limits. Illustrative composites are labelled as such. When a page is updated, the date appears in the header.</p>
""",
    )
    urls.append(("https://www.seogeoworks.hk/about/", "0.8"))

    page(
        path=PUBLIC / "contact" / "index.html",
        title="Contact seogeoworks",
        description="Contact the seogeoworks editorial desk for corrections, collaborations, and resource licensing questions.",
        canonical="https://www.seogeoworks.hk/contact/",
        eyebrow="seogeoworks / contact",
        h1="Write to the desk.",
        lede="Use these channels for corrections, citation requests, partnership notes, and questions about the field guides.",
        schema="""      {
        "@context": "https://schema.org",
        "@type": "ContactPage",
        "url": "https://www.seogeoworks.hk/contact/",
        "name": "Contact seogeoworks",
        "isPartOf": { "@id": "https://www.seogeoworks.hk/#website" },
        "dateModified": "%s"
      }""" % TODAY,
        body="""
      <h2>Editorial contact</h2>
      <p>Email <a href="mailto:hello@seogeoconsulting.hk">hello@seogeoconsulting.hk</a> with the subject line <strong>seogeoworks</strong>. Include the page URL if you are reporting an error or requesting a correction.</p>
      <h2>Consulting &amp; delivery</h2>
      <ul>
        <li>SEO / GEO consulting: <a href="https://www.seogeoconsulting.hk/" rel="noopener">seogeoconsulting.hk</a></li>
        <li>Digital marketing &amp; IT: <a href="https://itehk.com.hk/" rel="noopener">itehk.com.hk</a> · <a href="mailto:info@itehk.com.hk">info@itehk.com.hk</a></li>
      </ul>
      <h2>Linking &amp; citation</h2>
      <p>You are welcome to link to any public page on seogeoworks.hk. Preferred citation targets are listed on the <a href="/resources/">resources</a> hub.</p>
""",
    )
    urls.append(("https://www.seogeoworks.hk/contact/", "0.7"))

    topic_html = ""
    if topic_links:
        items = "".join(
            f'<a href="{escape(href)}"><strong>{escape(label)}</strong><span>{escape(blurb)}</span></a>'
            for label, href, blurb in topic_links
        )
        topic_html = f'<h2>Topic hubs</h2><div class="card-grid">{items}</div>'

    page(
        path=PUBLIC / "resources" / "index.html",
        title="Resources — linkable SEO & GEO references | seogeoworks",
        description="Stable, citeable seogeoworks resources: SEO vs GEO, GEO readiness checklist, citation playbook, and bilingual field guides.",
        canonical="https://www.seogeoworks.hk/resources/",
        eyebrow="seogeoworks / resources",
        h1="Resources worth citing.",
        lede="Stable URLs for definitions, checklists, and field guides. Use these when you need a reference that stays useful after the news cycle moves on.",
        schema="""      {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "url": "https://www.seogeoworks.hk/resources/",
        "name": "seogeoworks resources",
        "description": "Citeable SEO and GEO resources for Hong Kong operators.",
        "isPartOf": { "@id": "https://www.seogeoworks.hk/#website" },
        "dateModified": "%s"
      }""" % TODAY,
        body=f"""
      <div class="card-grid">
        <a href="/resources/seo-vs-geo.html"><strong>SEO vs GEO</strong><span>Where ranking and answer inclusion diverge — and what to fix first.</span></a>
        <a href="/resources/geo-readiness-checklist.html"><strong>GEO readiness checklist</strong><span>Nine practical signals you can audit in one working session.</span></a>
        <a href="/resources/how-to-earn-citations.html"><strong>How to earn citations</strong><span>A playbook for becoming a source answer engines can trust.</span></a>
        <a href="/articles/"><strong>All field guides</strong><span>Bilingual Eng/繁 library for marketing, SEO, KOL, and discovery queries.</span></a>
      </div>
      {topic_html}
""",
    )
    urls.append(("https://www.seogeoworks.hk/resources/", "0.9"))

    page(
        path=PUBLIC / "resources" / "seo-vs-geo.html",
        title="SEO vs GEO: the strategy gap explained | seogeoworks",
        description="A clear comparison of traditional SEO and generative engine optimization (GEO): outcomes, assets, authority signals, content shape, distribution, and measurement.",
        canonical="https://www.seogeoworks.hk/resources/seo-vs-geo.html",
        eyebrow="seogeoworks / resources",
        h1="SEO gets you seen. GEO gets you chosen.",
        lede="Traditional search optimization and generative engine optimization share a foundation — but they win in different moments. Use this as a shared vocabulary with your team.",
        schema="""      {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "SEO vs GEO: the strategy gap explained",
        "description": "A clear comparison of traditional SEO and generative engine optimization.",
        "datePublished": "2026-09-10",
        "dateModified": "%s",
        "author": { "@id": "https://www.seogeoworks.hk/#organization" },
        "publisher": { "@id": "https://www.seogeoworks.hk/#organization" },
        "mainEntityOfPage": "https://www.seogeoworks.hk/resources/seo-vs-geo.html",
        "inLanguage": "en"
      }""" % TODAY,
        body="""
      <h2>Primary outcome</h2>
      <p><strong>SEO:</strong> earn the click. <strong>GEO:</strong> earn the inclusion. A strong ranking can still be invisible when an answer engine summarizes the category without you.</p>
      <h2>Core asset</h2>
      <p><strong>SEO:</strong> a page optimized for a query. <strong>GEO:</strong> a source with a clear point of view. Keyword coverage without original expertise gives machines little reason to select your brand.</p>
      <h2>Authority signal</h2>
      <p><strong>SEO:</strong> links, relevance, and domain strength. <strong>GEO:</strong> named experts, corroboration, and recognizable entities. Backlinks help establish importance; they do not automatically establish what your brand knows.</p>
      <h2>Content shape</h2>
      <p><strong>SEO:</strong> answer the query efficiently. <strong>GEO:</strong> build context across related questions. Isolated posts are harder to retrieve than a connected body of knowledge.</p>
      <h2>Distribution</h2>
      <p><strong>SEO:</strong> own the search results page. <strong>GEO:</strong> show up in the wider information ecosystem — partners, press, communities, and reviews fill gaps your site alone cannot.</p>
      <h2>Measurement</h2>
      <p><strong>SEO:</strong> rankings, clicks, conversions. <strong>GEO:</strong> citations, mentions, sentiment, and qualified demand. Traffic can stay flat while influence grows.</p>
      <h2>Next step</h2>
      <p>Run the <a href="/resources/geo-readiness-checklist.html">GEO readiness checklist</a>, then browse relevant <a href="/articles/">field guides</a>.</p>
""",
    )
    urls.append(("https://www.seogeoworks.hk/resources/seo-vs-geo.html", "0.85"))

    page(
        path=PUBLIC / "resources" / "geo-readiness-checklist.html",
        title="GEO readiness checklist (9 signals) | seogeoworks",
        description="A practical nine-point GEO readiness checklist covering identity, source quality, distribution, and measurement for Hong Kong brands.",
        canonical="https://www.seogeoworks.hk/resources/geo-readiness-checklist.html",
        eyebrow="seogeoworks / resources",
        h1="GEO readiness checklist",
        lede="Nine practical signals. Mark what is already true, then treat unchecked items as your action queue.",
        schema="""      {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "GEO readiness checklist (9 signals)",
        "datePublished": "2026-09-10",
        "dateModified": "%s",
        "author": { "@id": "https://www.seogeoworks.hk/#organization" },
        "publisher": { "@id": "https://www.seogeoworks.hk/#organization" },
        "mainEntityOfPage": "https://www.seogeoworks.hk/resources/geo-readiness-checklist.html"
      }""" % TODAY,
        body="""
      <h2>Identity &amp; expertise</h2>
      <ul class="check">
        <li>Our organization, people, and offers have consistent names across the web.</li>
        <li>Important pages show a real author with relevant experience.</li>
        <li>Our About page clearly explains our point of view and the problems we solve.</li>
      </ul>
      <h2>Source quality</h2>
      <ul class="check">
        <li>We publish original evidence, examples, or observations — not only summaries.</li>
        <li>Our key terms and category definitions are stated plainly.</li>
        <li>We have a visible process for reviewing and updating important sources.</li>
      </ul>
      <h2>Reach &amp; measurement</h2>
      <ul class="check">
        <li>Trusted third-party sources mention or reference our expertise.</li>
        <li>We regularly test how answer engines describe and recommend our brand.</li>
        <li>We connect visibility signals to qualified conversations or revenue.</li>
      </ul>
      <p>Prefer an interactive version? Use the on-site <a href="/#audit">GEO audit</a> on the homepage, then return here to share a stable URL.</p>
""",
    )
    urls.append(("https://www.seogeoworks.hk/resources/geo-readiness-checklist.html", "0.85"))

    page(
        path=PUBLIC / "resources" / "how-to-earn-citations.html",
        title="How to earn citations in answer engines | seogeoworks",
        description="A practical playbook for earning citations: entity clarity, quotable passages, corroboration, and measurement beyond rankings.",
        canonical="https://www.seogeoworks.hk/resources/how-to-earn-citations.html",
        eyebrow="seogeoworks / resources",
        h1="How to earn citations",
        lede="Answer engines prefer sources they can resolve, quote, and corroborate. This playbook turns that preference into an operating checklist.",
        schema="""      {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "How to earn citations in answer engines",
        "datePublished": "2026-09-10",
        "dateModified": "%s",
        "author": { "@id": "https://www.seogeoworks.hk/#organization" },
        "publisher": { "@id": "https://www.seogeoworks.hk/#organization" },
        "mainEntityOfPage": "https://www.seogeoworks.hk/resources/how-to-earn-citations.html"
      }""" % TODAY,
        body="""
      <h2>1. Make the entity unambiguous</h2>
      <p>Use one canonical name for the organization, products, and experts. Repeat that identity on the About page, profiles, and service pages so retrieval systems can connect mentions.</p>
      <h2>2. Write quotable passages</h2>
      <p>Put a clear definition or answer near the top of cornerstone pages. Support it with examples, limits, and next steps. Thin intros that only tease the answer are hard to cite.</p>
      <h2>3. Show proof in public</h2>
      <p>Named authors, first-hand observations, primary sources, and dated updates give systems something specific to trust. Anonymous summaries of the same ten results do not.</p>
      <h2>4. Earn corroboration off-site</h2>
      <p>Domain Rating and answer inclusion both improve when independent sites reference your expertise. Prioritize relevant partners, industry directories, and media that your buyers already trust — starting with accurate listings and helpful, linkable resources.</p>
      <h2>5. Measure beyond rankings</h2>
      <p>Track citations, brand mentions, assisted demand, and how answer engines describe you. Pair that with classic SEO crawl and ranking health so the system stays complete.</p>
      <p>Related: <a href="/resources/seo-vs-geo.html">SEO vs GEO</a> · <a href="/resources/geo-readiness-checklist.html">GEO checklist</a></p>
""",
    )
    urls.append(("https://www.seogeoworks.hk/resources/how-to-earn-citations.html", "0.85"))

    return urls


if __name__ == "__main__":
    for u, _ in write_all():
        print(u)
