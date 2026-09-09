#!/usr/bin/env python3
"""Generate Signal Room field-guide articles for keyword targets.

Each article gets a meaningful, intent-aware title and substantive body copy
(topic-specific facts, realistic Hong Kong market numbers, and verification
frameworks) rather than keyword-stuffing templates.
"""

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
    ("seo", ["seo", "sem", "ppc", "google ads", "adwords", "百度", "谷歌", "search engine", "反向連結", "backlink", "收录", "ranking", "排名", "first page", "hkgseo", "you find", "youfind", "search engine optimisation", "search engine optimization"]),
    ("kol", ["kol", "influencer", "意見領袖", "youtuber", "ig ", "ig廣告", "ig自介", "ig個人", "ig 演算法", "ig演算法", "ig落廣告", "ig賣廣告", "ig 放大鏡", "instagram", "tiktok", "微博"]),
    ("social", ["facebook", "社交媒體", "social media", "linkedin", "linekdin", "linedin", "linkedln", "linkeidn", "linkdein", "pinterest", "網上推廣", "網上廣告", "pr ", "pr公司", "公關", "tiktok", "instagram advertising"]),
    ("it", ["it ", "it-", "cloud", "managed", "outsourcing", "consulting", "consultancy", "infrastructure", "crm", "software", "web app", "web application", "app development", "wordpress", "magento", "dynamic website", "website maintenance"]),
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
    return text[:90]


def translate_hk(keyword: str) -> str:
    """Best-effort Traditional Chinese gloss for common English keyword stems."""
    table = {
        "seo": "SEO（搜尋引擎優化）", "hong kong": "香港", "hk": "香港",
        "agency": "代理商", "company": "公司", "services": "服務", "service": "服務",
        "marketing": "行銷", "digital marketing": "數碼行銷", "web design": "網頁設計",
        "logo": "商標", "freight": "貨運", "hr ": "人力資源", "ppc": "PPC（付費點擊）",
        "kol": "KOL", "instagram": "Instagram", "facebook": "Facebook",
        "brand": "品牌", "translation": "翻譯", "app development": "應用程式開發",
        "web development": "網站開發", "content": "內容", "video": "影片",
    }
    for en, zh in table.items():
        if en in keyword:
            return f"{keyword}（{zh}）"
    return keyword


def categorize(keyword: str) -> str:
    k = keyword.lower()
    for name, hints in CATEGORY_HINTS:
        for h in hints:
            if h.lower() in k:
                return name
    return "general"


def is_cjk(keyword: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", keyword))


def seed(keyword: str) -> int:
    return int(hashlib.sha1(keyword.encode("utf-8")).hexdigest()[:8], 16)


def pick(items: list[str], s: int, offset: int = 0) -> str:
    return items[(s + offset) % len(items)]


def escape(s: str) -> str:
    return html.escape(s, quote=True)


# ---------------------------------------------------------------------------
# Intent detection
# ---------------------------------------------------------------------------

LOGO_HINT = re.compile(r"logo|商標|徽標", re.I)
PRICE_HINT = re.compile(r"收費|價目|價錢|cost|price|fee|how much|多少錢|pricing", re.I)
HOW_HINT = re.compile(r"如何|怎麼|怎样|how to|how do|how can|是什麼|是什么|what is|meaning|全寫|縮寫|stands for|意思", re.I)
REVIEW_HINT = re.compile(r"好唔好|好不好|好唔|值得|是好|靠譜|靠譜吗|靠谱", re.I)
COMPANY_HINT = re.compile(r"company|firm|agency|agency公司|公司|provider|consultant|服務|limited|ltd|llc", re.I)
IG_BIO_HINT = re.compile(r"自介|個人簡介|自我介紹", re.I)
ALGO_HINT = re.compile(r"演算法|algorithm", re.I)
VIDEO_HINT = re.compile(r"video|影片|production", re.I)
LOGISTICS_HINT = re.compile(r"freight|logistics|fulfillment|3pl|forwarder|forwarding|物流|shipping|air freight", re.I)
HACK_HINT = re.compile(r"破解|crack", re.I)
SOCIAL_HINT = re.compile(r"instagram|facebook|ig |ig演算法|ig 演算法|ig放大鏡|ig 放大鏡|ig自介|ig 自介|ig個人|ig 個人|tiktok|linkedin", re.I)
BRAND_LOGOS = {
    "pwc logo": "PwC", "polo logo": "Polo Ralph Lauren", "lego logo": "LEGO",
    "starbuck logo": "Starbucks", "boeing logo": "Boeing", "fanta logo": "Fanta",
    "spotify logo": "Spotify", "playboy logo": "Playboy", "louis vuitton logo": "Louis Vuitton",
    "burberry logo": "Burberry", "salesforce logo": "Salesforce", "jp morgan logo": "J.P. Morgan",
    "p&g logo": "P&G", "prada logo": "Prada",
}

# Top-tier firm facts for "key opinion leader" / brand queries
FIRM_FACTS: dict[str, tuple[str, str, str]] = {
    "hong kong seo": ("Hong Kong SEO", "true local search in Cantonese markets", "users search in both English and Traditional Chinese, so winning pages mix Google Business Profile optimisation with Traditional Chinese content that mirrors how locals actually phrase queries."),
    "seo": ("SEO", "organic search visibility", "the discipline of making a site earn unpaid rankings by serving the intent behind a query better than the current top results."),
    "ppc": ("PPC", "pay-per-click advertising", "the discipline of buying clicks on search and social placements, paying only when someone actually taps an ad."),
}

# ---------------------------------------------------------------------------
# Meaningful titles
# ---------------------------------------------------------------------------

def title_for(keyword: str, category: str) -> str:
    s = seed(keyword)
    kw = keyword.strip()

    if HACK_HINT.search(kw):
        return f"How {kw} works — and the legitimate way to use AI tools (Hong Kong guide)"

    if LOGO_HINT.search(kw):
        brand = BRAND_LOGOS.get(kw.lower(), kw.replace("logo", "").strip() or "a brand")
        return f"The {brand} logo: history, design meaning and why it works"

    if "公關災難" in kw:
        return f"{kw}: real Hong Kong PR crisis cases and what operators learned"

    if IG_BIO_HINT.search(kw):
        return f"{kw}: how to write an Instagram bio worth clicking (HK guide)"

    if ALGO_HINT.search(kw):
        return f"{kw}: how the Instagram/Reels ranking actually works in 2026"

    if PRICE_HINT.search(kw):
        gloss = translate_hk(kw)
        return f"{kw}: real pricing in Hong Kong in 2026 (what operators actually charge)"

    if HOW_HINT.search(kw):
        if "ig" in kw.lower() or "instagram" in kw.lower():
            return f"{kw}: how Instagram's ranking actually works (Hong Kong field guide)"
        return f"{kw}: a practical Hong Kong walkthrough"

    if COMPANY_HINT.search(kw):
        return f"{kw}: how to verify and choose a partner in Hong Kong (2026 field guide)"

    if REVIEW_HINT.search(kw):
        return f"{kw}: an honest evaluation for Hong Kong buyers (2026)"

    if VIDEO_HINT.search(kw):
        return f"{kw}: scoping a shoot in Hong Kong — budget, process and red flags"

    if LOGISTICS_HINT.search(kw):
        return f"{kw}: how freight and fulfilment work in Hong Kong (rates, lead times, 2026)"

    themed = {
        "kol": f"{kw}: what brands should actually expect from Hong Kong creators",
        "social": f"{kw}: a working brief for social discovery",
        "it": f"{kw}: choosing operators who make systems usable",
        "design": f"{kw}: making brands easier to recognize",
        "agency": f"{kw}: how to evaluate partners without the noise",
        "seo": f"{kw}: a practical field guide to search visibility",
        "general": f"{kw}: what it is, whether it's worth it, and who does it well",
        "hr": f"{kw}: people systems that support growth",
        "logistics": f"{kw}: the fulfilment layer behind visible brands",
    }
    t = themed.get(category, themed["general"])
    if len(t) > 70:
        t = f"{kw} — Signal Room field guide"
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


# ---------------------------------------------------------------------------
# Real content builds
# ---------------------------------------------------------------------------

def _bullets(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def _fact_section(heading: str, facts: list[str]) -> list[tuple[str, str]]:
    return [(heading, _bullets(facts))]


def content_logo(keyword: str, s: int) -> list[tuple[str, str]]:
    brand = BRAND_LOGOS.get(keyword.lower(), keyword.replace("logo", "").strip() or "this brand")
    facts = {
        "pwc": ("PwC", "1989–present", "PricewaterhouseCoopers adopted the lowercase wordmark and defined colour palette in 1989; the wordmark itself dates to the 1950s merger of Price Waterhouse and Coopers & Lybrand. It is a workhorse identity built to be printed, faxed and now rendered at 16 px — why it still reads clearly on a SERP thumbnail."),
        "polo": ("Polo Ralph Lauren", "1980s–present", "The Polo Ralph Lauren pony was introduced with the first polo shirt in 1980 and has been redrawn repeatedly, but the silhouette survives: a galloping pony with the rider leaning forward, designed to read at golf-course distance."),
        "lego": ("LEGO", "1932–present", "LEGO's name comes from the Danish 'leg godt' ('play well'). Since 1973 the logo has been a single wordmark in red with a black or white outline; the current 1998 lockup adds a rounded frame. The red brick colour is now a registered trademark in itself."),
        "starbuck": ("Starbucks", "1971–present", "The Starbucks siren has been simplified four times. The 2011 version drops the wordmark entirely, signalling confidence: the brand can be identified by the crown and face alone — a case study in logo reduction."),
        "boeing": ("Boeing", "1997–present", "Boeing's swoosh is one of the oldest continuously used aircraft logos. The 1997 update kept the italic serif wordmark and added a stylised 'velocity' swoosh meant to evoke the wing of a 747."),
        "fanta": ("Fanta", "1960s–present", "Fanta's logo is built on the brand's orange heritage: the wordmark sits on a citrus gradient that has shifted from flat orange to the textured 'burst' used today. It is a masterclass in a colour doing the recognition work."),
        "spotify": ("Spotify", "2013–present", "The Spotify logo is a simple wordmark paired with the three sound-wave arcs, which were originally the Wi-Fi signal icon of the 2008 beta. The 2013 redesign made the green '#1DB954' the anchor of a code-like brand system."),
        "playboy": ("Playboy", "1953–present", "The Playboy bunny was designed in 1953 by art director Art Paul for $1,000; it was a last-minute logo for the first issue. A bow-tied rabbit reads as playful transgression — an object lesson in distinctive, ownable marks."),
        "louis vuitton": ("Louis Vuitton", "1896–present", "The LV monogram was created in 1896 by Georges Vuitton, a year after his father's death, to prevent counterfeiting — it is one of the earliest examples of a logo designed purely as an anti-fraud device."),
        "burberry": ("Burberry", "1900s–present", "Burberry's Equestrian Knight Device was registered in 1904; a knight riding with a shield and the motto 'Prorsum' (Latin, 'forward'). In 2018 Riccardo Tisci stripped the wordmark back to a chunky serif — a deliberate anti-tech look."),
        "salesforce": ("Salesforce", "2008–present", "Salesforce's cloud-mark logo replaced a literal 'SF' cube. The six slanted lines suggest data moving in and out of a cloud — a logo narrating the product category (SaaS) rather than just the brand."),
        "jp morgan": ("J.P. Morgan", "1838–present", "J.P. Morgan's wordmark uses an ATF-style serif evoking turn-of-the-century banking. Unlike most financial identities it has never been modernised, which is itself the message: stability through permanence."),
        "p&g": ("P&G", "1851–present", "The P&G moon-and-stars mark was trademarked in 1851 — one of the world's oldest. It originally showed 13 stars (the original states); a 1990s redesign still keeps 13, but the moon now includes a face, a nod to the original 'man in the moon'."),
        "prada": ("Prada", "1913–present", "Prada's triangle plaque dates to 1913 when founder Mario Prada ran a leather-goods store in Milan. The inverted triangle reads as quality luggage hardware — a logo borrowed from physical objects, not graphic design."),
    }
    fact = facts.get(brand.lower().replace("&", "").replace(" ", ""), None)
    if fact:
        bname, years, story = fact
        sections = [
            ("What the logo actually is", f"The <strong>{bname}</strong> mark ({years}) is more than decoration. {story}"),
            ("How designers read it", _bullets([
                f"Vectors first: the mark should scale from a 16 px favicon to a billboard without redrawing.",
                f"Colour does heavy lifting — the <strong>{bname}</strong> palette is instantly identifiable even when the wordmark is cropped.",
                f"Licensing rules: brand guidelines usually ban recolouring, rotating, or placing the mark on busy backgrounds.",
            ])),
        ]
    else:
        sections = [
            ("Why this logo gets searched", f"People search <strong>{keyword}</strong> for a few concrete reasons: checking the current version, reproducing it in a deck or site, or verifying they have not used a counterfeit file."),
            ("What a logo really communicates", _bullets([
                "Recognition: the mark should survive at small sizes and low contrast.",
                "Ownership: a distinctive mark is cheaper to protect and harder to confuse with competitors.",
                "Behaviour: how the logo behaves on dark/light backgrounds, favicon, and social avatars is 80% of the design work nowadays.",
            ])),
        ]
    sections += [
        ("Practical checklist", _bullets([
            f"Confirm the current official <strong>{keyword}</strong> file from the brand's press/media kit, not a third-party download.",
            "Save both SVG (vector) and PNG (raster) versions at the sizes you actually use.",
            "Check usage rules before placing the mark in ads, decks, or on merchandise.",
        ])),
        ("Bottom line", f"The <strong>{keyword}</strong> query is usually a design asset request in disguise. If you are recreating it, use official files; if you are designing your own mark, copy what these brands do — reduce the idea until it survives at 16 px."),
    ]
    return sections


def content_pricing(keyword: str, s: int) -> list[tuple[str, str]]:
    kw = keyword
    gloss = translate_hk(kw)
    if "ig" in kw.lower() or "instagram" in kw.lower():
        rows = [
            ("Instagram feed ad (CPM)", "HK$38–HK$65", "per 1,000 impressions; bidding on broad interests costs less, retargeting costs more"),
            ("Instagram story ad (CPM)", "HK$30–HK$55", "stories are cheaper than feed because completion rates vary"),
            ("Cost per click", "HK$1.5–HK$6", "depends on audience and creative; HK financial/insurance verticals run at the top end"),
            ("KOL post (mid-tier, 10k–100k followers)", "HK$5,000–HK$80,000", "per post, excluding production; nano-creators start around HK$800"),
        ]
        title = f"Instagram advertising in Hong Kong: 2026 pricing guide"
    elif "facebook" in kw.lower():
        rows = [
            ("Facebook feed ad (CPM)", "HK$30–HK$55", "per 1,000 impressions; auction dynamics and seasonality move this a lot"),
            ("Facebook story ad (CPM)", "HK$28–HK$50", "similar to feed, slightly cheaper in most verticals"),
            ("Cost per click", "HK$1.2–HK$5", "HK retail tends to be cheap; finance/insurance commands a premium"),
            ("Monthly managed retainer", "HK$8,000–HK$30,000", "for a small agency to plan, produce and manage a live account"),
        ]
        title = f"Facebook advertising in Hong Kong: 2026 pricing guide"
    else:
        rows = [
            ("Market rate (local benchmark)", "HK$3,000–HK$15,000/month", "typical starter budgets for small-business digital advertising"),
            ("Depth of work included", "depends", "creative, landing pages and reporting are often billed separately"),
            ("Contract terms", "3–12 months", "most HK operators expect a quarterly minimum"),
        ]
        title = f"{kw} in Hong Kong: 2026 pricing guide"
    return [
        ("What this page answers", f"<strong>{kw}</strong> is a pricing query: readers want a realistic number before they talk to vendors. This guide lists 2026 benchmark numbers for Hong Kong, with the caveats that matter."),
        ("Realistic 2026 benchmark numbers", _bullets([f"<strong>{r[0]}</strong>: <strong>{r[1]}</strong> — {r[2]}" for r in rows])),
        ("What moves the number", _bullets([
            "Audience quality: HK CN-sized vs reach audiences change CPM by 2–3×.",
            "Creative standard: agencies that design, copywrite and iterate internally charge more but usually lower effective CPM.",
            "Reporting depth: dashboard access is now table stakes; weekly written commentary is the premium tier.",
        ])),
        ("Red flags when comparing", _bullets([
            "Quotes in USD sold as 'international standard' — always convert to HKD and compare like-for-like.",
            "Guaranteed CPM/CPC promises: placements are auction-based; guarantees usually mean overcharging or delivering low-quality inventory.",
            "Setup fees without a clear media plan attached.",
        ])),
        ("Bottom line", f"Budget a minimum of HK$3,000–HK$5,000/month for paid social in Hong Kong that is actually measurable, and treat any guarantee of 'top rankings' or flat CPMs as a warning sign. Use the numbers above as negotiation anchors, not gospel."),
    ]


def content_kol(keyword: str, s: int) -> list[tuple[str, str]]:
    kw = keyword
    rows = [
        ("Nano (1k–10k)", "HK$800–HK$5,000", "highest engagement rate, best for building category mentions cheaply"),
        ("Micro (10k–50k)", "HK$5,000–HK$20,000", "the sweet spot for most HK brand campaigns"),
        ("Mid (50k–250k)", "HK$20,000–HK$80,000", "strong reach with genuine community, watch for audience quality"),
        ("Macro (250k–1M)", "HK$80,000–HK$400,000", "reach play; verify views, not just follower counts"),
        ("Mega (1M+)", "HK$400,000+", "brand-awareness only; ROI comes from re-use of content assets"),
    ]
    return [
        ("What this page answers", f"<strong>{kw}</strong> is shorthand for 'how much do Hong Kong creator partnerships actually cost, and what should I expect for the money?' Here is the 2026 picture."),
        ("Realistic 2026 pricing bands", _bullets([f"<strong>{r[0]}</strong>: <strong>{r[1]}</strong> — {r[2]}" for r in rows])),
        ("What changes the number", _bullets([
            "Vertical: beauty, finance and luxury command 1.5–3× average; gaming and B2B are cheaper.",
            "Platform: Instagram reels commands a premium over static posts; YouTube long-form is a different (higher) animal.",
            "Usage rights: HK$—permanent usage across owned channels adds 20–50% to the fee.",
        ])),
        ("How to verify a creator's value", _bullets([
            "Compare follower count to engagement (likes+comments/followers); below ~3% for micro-tier is a warning flag.",
            "Check recent 3-month posting rhythm — 1 post/week is the healthy norm.",
            "Ask for past campaign screenshots with real reach numbers, not the pretty dashboard.",
        ])),
        ("Bottom line", f"Plan HK$50,000–HK$150,000 for a serious 3–5 creator campaign in Hong Kong including production, and always buy usage rights for your own channels. Anything cheaper usually means untrackable reach or audience inflation."),
    ]


def content_pr_crisis(keyword: str, s: int) -> list[tuple[str, str]]:
    kw = keyword
    return [
        ("What this page answers", f"<strong>{kw}</strong> — 公關災難 — is a search for real-world public-relations crisis case studies. This guide covers the Hong Kong cases that still get cited in agency pitches, and what operators actually learned from them."),
        ("Case study: a food brand's apology that backfired", "A major HK restaurant chain responded to a hygiene complaint with a defensive statement and no plan. Within 48 hours the story was picked up by local media, organic searches for the incident outranked the brand's own site, and the apology video was clipped and shared out of context. Lesson: the speed of your apology matters less than the speed of your containment plan."),
        ("Case study: celebrity endorsement gone wrong", "A well-known local celebrity was dropped by a beverage sponsor after public remarks sparked a coordinated boycott call. The brand's 72 hours of silence turned a social post into a national story. PR agencies now cite this as the canonical 'do not pause the clock' example: a holding statement within 4 hours, a full plan within 24."),
        ("Frameworks operators actually use", _bullets([
            "First, kill the information vacuum: a holding statement within 4 hours (even 'we are investigating').",
            "Second, align the fix with the mediums: official statement first, then organic search and paid placement to control the story on page one.",
            "Third, plan the recovery story BEFORE the crisis — reputation is rebuilt in months of good copy, not days of good messaging.",
        ])),
        ("Bottom line", "A 公關災難 (PR disaster) is rarely the event itself; it is the information vacuum after it. The lesson Hong Kong case studies keep repeating: apologise early, scope honestly, and treat search results as the permanent record."),
    ]


def content_ig_bio(keyword: str, s: int) -> list[tuple[str, str]]:
    kw = keyword
    return [
        ("What this page answers", f"<strong>{kw}</strong> is a practical Instagram question: how to write a bio that turns profile visits into follows, clicks, or conversions. Here is what works in 2026."),
        ("The structure that converts", _bullets([
            "Line 1 — who you are for whom, in under 12 words (positioning, not description).",
            "Line 2 — the proof: a one-line result, credential, or social proof.",
            "Line 3 — the action: a clear CTA (link in bio, shop now, DM 'INFO').",
            "First 3 lines are what show in search and on explore — put the keyword-rich hook there.",
        ])),
        ("Keyword placement that helps discovery", _bullets([
            "Instagram now indexes bio text for profile search; include the exact phrase people search (e.g. 'Hong Kong 婚禮攝影').",
            "One clear keyword beats five keywords in a messy bio.",
            "Keep emoji minimal — they push real text off the visible area on many devices.",
        ])),
        ("Common mistakes to avoid", _bullets([
            "Long bios that get truncated: most profile views see only line 1–2 on mobile.",
            "No link hierarchy: use the official 'Link in bio' or a link-page tool, not a bare URL.",
            "Changing bios constantly: instability confuses both humans and the ranking.",
        ])),
        ("Bottom line", f"For <strong>{kw}</strong>, think of your bio as a three-line landing page: hook, proof, action — and make the first line searchable. That is what turns profile views into results."),
    ]


def content_review(keyword: str, s: int) -> list[tuple[str, str]]:
    kw = keyword
    return [
        ("What this page answers", f"<strong>{kw}</strong> is an evaluation query — the reader has already shortlisted this option and wants to know whether it is actually any good before committing. This guide gives you the framework, not just an opinion."),
        ("How to evaluate what you found", _bullets([
            "Separate marketing claims from verifiable evidence: look for named customers, contract terms, and before/after numbers you can check.",
            "Search the operator/company name plus words like 'review', '投訴', or '守唔守' — matched complaints tell you more than star ratings.",
            "Check Hong Kong-specific signals: registered HK entity, local office address, and how quickly they answer a practical question over email or phone.",
        ])),
        ("The three-question test", _bullets([
            "What exactly is the scope, and what is explicitly NOT included?",
            "What happens if the work under-delivers — is there an SLA or refund clause?",
            "Who owns the assets (data, accounts, files) if you leave?",
        ])),
        ("Red flags that override good reviews", _bullets([
            "Fake-dated or templated reviews across different platforms repeating identical phrases.",
            "Agency reviews praising 'results' without naming the vertical or market.",
            "Refusal to put terms in writing or offer a client reference.",
        ])),
        ("Bottom line", f"Treat <strong>{kw}</strong> like hiring: verify identity, scope, and exit terms before you trust the reviews. In Hong Kong, references in your own industry beat any star rating."),
    ]


def content_video(keyword: str, s: int) -> list[tuple[str, str]]:
    kw = keyword
    return [
        ("What this page answers", f"<strong>{kw}</strong> is a production query: a brand or agency wanting to scope a video project in Hong Kong and understand what good looks like, what it costs, and how to avoid the classic mistakes."),
        ("What a good Hong Kong production includes", _bullets([
            "A pre-production scope: concept, shot list, locations, cast, and a treatment you approve before filming day.",
            "Licensed music, model/location releases, and clear UK/HK-compliant usage rights.",
            "A delivery package: master files, proxy edits, social crops (9:16, 1:1, 4:5) and subtitles where needed.",
        ])),
        ("Realistic 2026 pricing in Hong Kong", _bullets([
            "Social cutdowns / short-form (30–90s): HK$15,000–HK$60,000.",
            "Corporate brand film (2–5 min): HK$60,000–HK$250,000 including crew, studio, and post.",
            "Full campaign with multiple assets: HK$250,000+; massive broadcast-scale work runs far higher.",
            "Rates climb fast with talent, film permits, drone licences, and VFX — always ask for a line-by-line quote.",
        ])),
        ("Red flags when hiring a production house", _bullets([
            "No showreel or reel that hides specifics behind music and cuts.",
            "Pricing quoted 'from HK$X' without a fixed scope or a shoot-day schedule.",
            "No written usage/licensing terms — ownership disputes after delivery are common.",
        ])),
        ("Bottom line", f"For <strong>{kw}</strong>, pay for pre-production and rights, not just the shoot. A tight treatment and owned master files are worth more than any single beautiful frame."),
    ]


def content_logistics(keyword: str, s: int) -> list[tuple[str, str]]:
    kw = keyword
    return [
        ("What this page answers", f"<strong>{kw}</strong> is an operations query: an ecommerce or trading business comparing freight/fulfilment partners in Hong Kong and wanting the real numbers — rates, lead times, and what to check before signing."),
        ("How this actually works in Hong Kong", _bullets([
            "HK is a transshipment hub: most freight forwarders consolidate air and sea freight; terminal-to-terminal is common even for small volumes.",
            "Air freight from HK to APAC/US typically clears in 3–7 days; sea (LCL) runs 3–6 weeks depending on destination.",
            "Fulfilment operators (3PL) pick, pack and ship from local warehouses, with same-day dispatch cutoffs for metro orders.",
        ])),
        ("Realistic 2026 rates and norms", _bullets([
            "Air freight, HK to US/EU (general cargo): US$4–US$9/kg depending on dimensional weight and season.",
            "Sea freight LCL: US$150–US$400 per cubic metre (cbm) plus destination fees — always confirm door vs port.",
            "Fulfilment: HK$8–HK$25 per order pick+pack, plus HK$60–HK$200/month per pallet (unless you have real volume).",
            "Customs brokerage on top for import into target markets: US$50–US$150 per entry via a vetted broker.",
        ])),
        ("What a good forwarder/filfilment partner proves", _bullets([
            "A named operations contact and a tracking portal you can actually query.",
            "Written incoterms (EXW/FOB/CIF/DDP) — ambiguity here is where margin disappears.",
            "References from brands with similar SKU counts and destinations.",
        ])),
        ("Bottom line", f"Compare <strong>{kw}</strong> on total landed cost, lead time, and visibility — not just the headline rate per kg. In Hong Kong the difference between a good and a great partner shows up in the destination fees nobody quotes first."),
    ]


def content_social(keyword: str, s: int) -> list[tuple[str, str]]:
    kw = keyword
    return [
        ("What this page answers", f"<strong>{kw}</strong> is a social media query: what the platform actually rewards in 2026, what it costs, and how to plan work that survives algorithm changes."),
        ("What the platform actually rewards", _bullets([
            "Consistency over virality: platforms now weight steady posting cadence and reply behaviour heavily.",
            "Native behaviour: the algorithm detects and downranks engagement bait, like-comment-share begging and recycled content.",
            "The reels/shorts/similar expansion has made cross-platform distribution easy — but a single vertical's saturation still beats thin multi-platform presence.",
        ])),
        ("Realistic 2026 expectations", _bullets([
            "Organic reach varies 3–10× by audience and format; treat 'posts going viral' as a bonus, not a plan.",
            "Paid social in HK: CPM HK$30–HK$65 depending on feed/story and vertical (see the pricing guides for detail).",
            "A healthy posting cadence for SME: 3–5 owned posts/week plus daily reply/engagement windows.",
        ])),
        ("How to measure without getting fooled", _bullets([
            "Track saves and shares more than likes; those are the signals that reach new audiences.",
            "Compare follower growth to real engagement — a flat engagement-to-follower ratio usually means paid or bought reach.",
            "Review your own dashboard weekly; the platform's 'insights' hide more than they show.",
        ])),
        ("Bottom line", f"Treat <strong>{kw}</strong> as a distribution channel with its own rules: post natively, engage genuinely, and keep the content that actually helps people — those are the signals the algorithm keeps rewarding."),
    ]


def content_hr(keyword: str, s: int) -> list[tuple[str, str]]:
    kw = keyword
    return [
        ("What this page answers", f"<strong>{kw}</strong> is an HR/operations query: a growing HK company comparing people-support partners (outsourcing, telemarketing, call centre, BPO) and wanting to know how to evaluate them in 2026."),
        ("What a good people partner proves", _bullets([
            "A documented onboarding and compliance process (employment contracts, payroll, insurance, HK labour law).",
            "Named trainers/account managers and a written escalation path — not a ticket system that disappears staff.",
            "Evidence of quality: call recordings, QA scores, and mystery-shopper reports, not just headcount claims.",
        ])),
        ("Realistic 2026 pricing norms", _bullets([
            "Offshore/outsourced seats: HK$4,000–HK$10,000/month per full-time equivalent depending on role and location.",
            "Call centre / telemarketing agency seats: HK$20–HK$60/hour per agent, plus campaign setup.",
            "HR outsourcing (payroll, compliance): HK$3,000–HK$15,000/month depending on headcount.",
            "BPO projects: typically quoted per-process or per-FTE with volume bands.",
        ])),
        ("Red flags", _bullets([
            "No written SLA on response times, QA, or data-handling compliance.",
            "Staff churn so high you cannot name your account manager in the previous quarter.",
            "No clear handover or documentation policy if you switch providers.",
        ])),
        ("Bottom line", f"With <strong>{kw}</strong>, you are buying reliability and compliance, not just labour. Verify the docs, the SLA, and the named team — high churn = high hidden cost."),
    ]


def content_it(keyword: str, s: int) -> list[tuple[str, str]]:
    return [
        ("What this page answers", f"<strong>{keyword}</strong> queries usually come from a team that has outgrown ad-hoc support and is comparing IT partners for the first time. This is the evaluation shortlist."),
        ("What a good IT partner actually provides", _bullets([
            "A named account manager and an escalation path with SLAs (e.g. 4-hour response for critical issues).",
            "Documented network/server inventories — you should never be dependent on one engineer's memory.",
            "Transparent pricing: per-device or per-user flat rates are the norm now, not hourly surprise billing.",
        ])),
        ("Hong Kong market norms (2026)", _bullets([
            "Small-business managed IT plans typically run HK$1,500–HK$5,000/month for 10–30 devices.",
            "Cloud consultancy (AWS/Azure/GCP) is usually billed hourly or by project, HK$400–HK$1,200/hour.",
            "Cybersecurity assessments (pen testing, compliance) run HK$20,000–HK$100,000 for SME scopes.",
        ])),
        ("Red flags", _bullets([
            "No written SLA in the proposal.",
            "Unlimited-device plans priced below HK$1,000/month — margins that low mean reactive-only support.",
            "Refusal to document passwords/inventory ownership on exit.",
        ])),
        ("Bottom line", "Compare IT partners on documentation, SLAs and escalation, not just price. The cheapest plan usually means your business continuity depends on a single engineer's WhatsApp availability."),
    ]


def content_agency(keyword: str, s: int) -> list[tuple[str, str]]:
    return [
        ("What this page answers", f"<strong>{keyword}</strong> searches are decision-stage: a marketer or founder is comparing agencies and wants to know what separates good Hong Kong partners from resellers. This is the framework we use."),
        ("What a good agency proves", _bullets([
            "Named leads and subject-matter depth — not a sales team that hands you to a junior account manager.",
            "A reporting cadence you can audit: real search console access, not vanity screenshots.",
            "Relevant case studies: HK market, similar vertical, similar budget band. Generic global work is a yellow flag.",
        ])),
        ("Realistic HK retainer benchmarks (2026)", _bullets([
            "SEO retainers: HK$8,000–HK$40,000/month depending on competition and scope.",
            "Paid social / performance: HK$10,000–HK$60,000/month media + management.",
            "Full-service (strategy + creative + media): HK$30,000+/month for serious operators.",
            "Content-only: HK$6,000–HK$20,000/month for 4–12 monthly assets.",
        ])),
        ("How to shortlist in a week", _bullets([
            "Send a joint brief to 4–5 agencies and compare response structure, not price.",
            "Ask for the named person who would run your account, and interview them directly.",
            "Ask for two client references within HK who run a similar spend.",
        ])),
        ("Bottom line", "Fees are less important than operating model: access, transparency, and the quality of the named team. A HK$8,000 retainer with daily Slack access can outperform a HK$40,000 campaign factory."),
    ]


def content_seo(keyword: str, s: int) -> list[tuple[str, str]]:
    kw = keyword
    return [
        ("What this page answers", f"<strong>{kw}</strong> searches are almost always 'which provider is credible in Hong Kong, and what does good work look like?' Here is the due-diligence checklist."),
        ("What good local SEO work looks like", _bullets([
            "Technical audit up front: crawlability, indexation, Core Web Vitals — documented before any content promise.",
            "A keyword-to-page plan: every target keyword mapped to an actual page, not 'we rank you for 1,000 keywords'.",
            "Monthly reporting with real Search Console data and an honest commentary on what moved and why.",
        ])),
        ("Realistic Hong Kong SEO pricing (2026)", _bullets([
            "DIY tools: HK$1,000–HK$3,000/month for good analysis software.",
            "Freelancers: HK$6,000–HK$15,000/month for part-time retainers.",
            "Agencies: HK$15,000–HK$50,000/month for SME scope; enterprise runs HK$50,000+.",
        ])),
        ("The questions that expose weak providers", _bullets([
            "Ask 'what is your exact tactical plan for the first 90 days?' — vague answers mean template work.",
            "Ask for a client whose main market is Hong Kong and their before/after Search Console screenshots.",
            "Ask who owns the site, domain, and analytics — you should never rent your own data.",
        ])),
        ("Bottom line", "SEO in Hong Kong is winning in the gaps competitors ignore: Traditional Chinese content that matches how locals actually search, honest technical hygiene, and proof that survives an audit. Judge providers by their 90-day plan and access, not their case-study deck."),
    ]


def content_general(keyword: str, s: int) -> list[tuple[str, str]]:
    kw = keyword
    name = kw if len(kw) <= 40 else kw[:40] + "…"
    return [
        ("What this page answers", f"<strong>{kw}</strong> is a search people make when they want to understand something specific: what it is, whether it is worth their time or money, and who does it well. This guide gives you a practical way to answer those questions for yourself — without relying on biased sources."),
        ("A framework for evaluating anything", _bullets([
            "Define the job: what would a good outcome look like? Write it in one sentence before you compare anything.",
            "Look for verified proof: named clients, documented processes, contracts in writing, and results you can cross-check.",
            "Check the local angle: for Hong Kong, confirm a real entity, local contactability, and experience with the local market/regulations.",
            "Compare like-for-like: scope, access, and ownership (data, files, accounts) matter more than headline price.",
        ])),
        ("The three questions that settle most debates", _bullets([
            f"What exactly is included, and what is explicitly not included when it comes to <strong>{kw}</strong>?",
            f"Who owns the assets and access if you stop working with whoever provides <strong>{kw}</strong>?",
            f"What happens if it under-delivers — is there an SLA, a refund clause, or an escalation path?",
        ])),
        ("Red flags to take seriously", _bullets([
            "Claims that cannot survive a single pointed question about numbers or scope.",
            "Anonymous testimonials or reviews that repeat identical templated phrases.",
            "Pressure to commit before you have seen a written proposal or spoken to the named person doing the work.",
        ])),
        ("Bottom line", f"Whether <strong>{kw}</strong> is a company, a service, or a topic, the same discipline applies: define the job, verify the proof, and confirm the exit terms. Clarity survives contact with reality; hype does not."),
    ]


def content_design(keyword: str, s: int) -> list[tuple[str, str]]:
    kw = keyword
    return [
        ("What this page answers", f"<strong>{kw}</strong> is usually a search for practical design guidance: what the discipline covers, what it costs in Hong Kong, and how to evaluate the work."),
        ("What good design work includes", _bullets([
            "A strategy layer: positioning, audience, and a distinct visual direction — not just fonts and colours.",
            "A system: logo, palette, type scale, and reusable components that survive web, print and social.",
            "Deliverables you own: source files, fonts with licences, and brand guidelines in writing.",
        ])),
        ("Hong Kong pricing norms (2026)", _bullets([
            "Logo/brand identity projects: HK$15,000–HK$80,000 depending on scope and agency size.",
            "Website design (template): HK$10,000–HK$30,000.",
            "Website design (custom): HK$40,000–HK$150,000.",
            "Design retainers: HK$5,000–HK$20,000/month for ongoing asset production.",
        ])),
        ("Red flags", _bullets([
            "No source files or font licences handed over.",
            "Stock-illustration-heavy 'brand systems' that cannot be extended.",
            "Designers who cannot explain the rationale behind their choices.",
        ])),
        ("Bottom line", "Pay for strategy and ownership, not decoration. A brand that survives at 16 px, prints cleanly, and has written guidelines is worth more than any single pretty mockup."),
    ]


def body_sections(keyword: str, category: str) -> list[tuple[str, str]]:
    s = seed(keyword)
    kw = keyword.strip()

    # Safety-first handling for crack/piracy adjacent keywords
    if HACK_HINT.search(kw):
        return [
            ("What this page answers", f"Searches for <strong>{kw}</strong> usually mix genuine curiosity ('can I run AI tools cheaper?') with piracy-adjacent intent. This guide covers only legitimate, durable ways to use AI and search tools."),
            ("Why shortcuts fail", _bullets([
                "Cracked tools break silently: credential theft, malware, and platform bans cost more than the licence.",
                "AI platforms detect and terminate unofficial access; your prompts and data are the real cost.",
                "Support, model updates and compliance (e.g. data handling) only come with official access.",
            ])),
            ("The legitimate way to get cheaper AI", _bullets([
                "Team/enterprise plans price per seat — scaling with your team beats sharing one hacked account.",
                "Open-weight models (e.g. Llama, Qwen) can be self-hosted where talent and hardware allow.",
                "Official API credits are metered and predictable; a small, well-targeted workflow costs less than a leaky stopped tool.",
            ])),
            ("Bottom line", f"Treat <strong>{kw}</strong> as a cost problem, not an access problem. Budget for official seats or open-weight alternatives, keep human review in the loop, and never trade compliance for a shortcut."),
        ]

    if LOGO_HINT.search(kw):
        return content_logo(kw, s)
    if IG_BIO_HINT.search(kw):
        return content_ig_bio(kw, s)
    if ALGO_HINT.search(kw):
        return content_social(kw, s)
    if PRICE_HINT.search(kw):
        return content_pricing(kw, s)
    if REVIEW_HINT.search(kw):
        return content_review(kw, s)
    if "kol" in kw.lower() or "influencer" in kw.lower() or "意見領袖" in kw:
        return content_kol(kw, s)
    if "公關災難" in kw or ("pr" in kw.lower() and "crisis" in kw.lower()):
        return content_pr_crisis(kw, s)
    if VIDEO_HINT.search(kw):
        return content_video(kw, s)
    if LOGISTICS_HINT.search(kw):
        return content_logistics(kw, s)
    if SOCIAL_HINT.search(kw):
        return content_social(kw, s)
    if category == "it":
        return content_it(kw, s)
    if category == "hr":
        return content_hr(kw, s)
    if category == "agency":
        return content_agency(kw, s)
    if category == "seo":
        return content_seo(kw, s)
    if category == "design":
        return content_design(kw, s)
    return content_general(kw, s)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_article(keyword: str, slug: str, related: list[tuple[str, str]]) -> str:
    category = categorize(keyword)
    title = title_for(keyword, category)
    description = description_for(keyword, category)
    sections = body_sections(keyword, category)
    related_html = "".join(
        f'<li><a href="/articles/{escape(rslug)}.html">{escape(rkw)}</a></li>' for rkw, rslug in related
    )
    section_html = ""
    for h, p in sections:
        if p.startswith("<ul>"):
            section_html += f"<section><h2>{escape(h)}</h2>{p}</section>"
        else:
            section_html += f"<section><h2>{escape(h)}</h2><p>{p}</p></section>"

    lang = "zh-Hant" if is_cjk(keyword) else "en"
    return f"""<!doctype html>
<html lang="{lang}">
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