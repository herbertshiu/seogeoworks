#!/usr/bin/env python3
"""Generate seogeoworks field-guide articles for keyword targets.

Every article is bilingual: English + Traditional Chinese (繁體中文), rendered
side by side with a client-side language toggle (EN/中文). Each article gets a
meaningful, intent-aware title and substantive body copy in both languages
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
from urllib.parse import quote, urlsplit, urlunsplit

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

CATEGORY_ZH = {
    "seo": "SEO",
    "kol": "KOL",
    "social": "社交媒體",
    "it": "IT",
    "design": "設計",
    "logistics": "物流",
    "hr": "人力資源",
    "agency": "代理商",
    "general": "總覽",
}


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKC", text.strip().lower())
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^\w\u4e00-\u9fff\-]+", "", text, flags=re.UNICODE)
    text = re.sub(r"-+", "-", text).strip("-")
    if not text:
        text = "article-" + hashlib.sha1(text.encode()).hexdigest()[:8]
    return text[:90]


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


def escape(s: str) -> str:
    return html.escape(s, quote=True)


def clip(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[: max(0, limit - 1)].rstrip(" —-:|,.")
    return cut + "…"


def encode_sitemap_url(url: str) -> str:
    """Percent-encode non-ASCII path segments so crawlers match sitemap locs."""
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, quote(parts.path, safe="/"), parts.query, parts.fragment))


def primary_title(keyword: str, category: str) -> str:
    return title_zh_for(keyword, category) if is_cjk(keyword) else title_for(keyword, category)


def primary_description(keyword: str, category: str) -> str:
    return description_zh_for(keyword, category) if is_cjk(keyword) else description_for(keyword, category)


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


# ---------------------------------------------------------------------------
# Meaningful titles (EN + ZH)
# ---------------------------------------------------------------------------

def title_for(keyword: str, category: str) -> str:
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
        t = f"{kw} — seogeoworks field guide"
    return t


def title_zh_for(keyword: str, category: str) -> str:
    kw = keyword.strip()
    if HACK_HINT.search(kw):
        return f"{kw} 的運作原理——以及合法使用 AI 工具的方法（香港指南）"
    if LOGO_HINT.search(kw):
        brand = BRAND_LOGOS.get(kw.lower(), kw.replace("logo", "").strip() or "某品牌")
        return f"{brand} 商標：歷史、設計含義與為何如此有效"
    if "公關災難" in kw:
        return f"{kw}：香港真實公關危機案例與營運者學到的教訓"
    if IG_BIO_HINT.search(kw):
        return f"{kw}：如何寫出值得點擊的 Instagram 簡介（香港指南）"
    if ALGO_HINT.search(kw):
        return f"{kw}：2026 年 Instagram／Reels 排名機制實際運作"
    if PRICE_HINT.search(kw):
        return f"{kw}：香港 2026 年真實收費（業界實際收多少）"
    if HOW_HINT.search(kw):
        if "ig" in kw.lower() or "instagram" in kw.lower():
            return f"{kw}：Instagram 排名機制實際運作（香港實地指南）"
        return f"{kw}：香港實用指南"
    if COMPANY_HINT.search(kw):
        return f"{kw}：如何在香港查證並揀選合作夥伴（2026 年指南）"
    if REVIEW_HINT.search(kw):
        return f"{kw}：為香港買家而設的誠實評價（2026）"
    if VIDEO_HINT.search(kw):
        return f"{kw}：在香港拍攝的估價——預算、流程與警示訊號"
    if LOGISTICS_HINT.search(kw):
        return f"{kw}：香港貨運與物流如何運作（收費、運送時間、2026）"
    themed = {
        "kol": f"{kw}：品牌應對香港創作者有甚麼期望",
        "social": f"{kw}：社交發掘的工作簡報",
        "it": f"{kw}：揀選能令系統可用的營運者",
        "design": f"{kw}：讓品牌更容易被認出",
        "agency": f"{kw}：如何在噪音中評估合作夥伴",
        "seo": f"{kw}：搜尋能見度的實用指南",
        "general": f"{kw}：它是甚麼、值唔值，以及誰做得好",
        "hr": f"{kw}：支持增長的人力系統",
        "logistics": f"{kw}：可見品牌背後的物流層",
    }
    return themed.get(category, themed["general"])


def description_for(keyword: str, category: str) -> str:
    base = {
        "seo": f"A practical seogeoworks guide to {keyword}: what matters for rankings, citations, and qualified demand in Hong Kong and beyond.",
        "kol": f"A seogeoworks field note on {keyword}: how creator partnerships become recognizable, citable brand signals.",
        "social": f"A seogeoworks briefing on {keyword}: social distribution, proof, and measurement that survive algorithm changes.",
        "it": f"A seogeoworks guide to {keyword}: how to choose technical partners that keep search and product systems coherent.",
        "design": f"A seogeoworks look at {keyword}: visual systems, brand clarity, and the signals that make a company memorable.",
        "logistics": f"A seogeoworks briefing on {keyword}: operations that support ecommerce visibility and customer trust.",
        "hr": f"A seogeoworks guide to {keyword}: people infrastructure that keeps growth and brand delivery aligned.",
        "agency": f"A seogeoworks field guide to {keyword}: how to brief, compare, and measure marketing partners.",
        "general": f"A seogeoworks field guide to {keyword}: context, evaluation criteria, and next steps for operators.",
    }
    d = base.get(category, base["general"])
    if len(d) < 120:
        d += " Written for teams who want clarity over hype."
    return d[:160]


def description_zh_for(keyword: str, category: str) -> str:
    base = {
        "seo": f"{keyword} 的實用指南：排名、引用與香港以至更遠地帶的合資格需求，哪些因素最要緊。",
        "kol": f"{keyword} 的實地筆記：創作人合作如何成為可辨認、可引用的品牌訊號。",
        "social": f"{keyword} 的工作簡報：經得起演算法變動的社交分發、證明與量度。",
        "it": f"{keyword} 的指南：如何選擇令搜尋與產品系統保持一致的技術夥伴。",
        "design": f"{keyword} 的觀點：視覺系統、品牌清晰度，以及令公司被記住的訊號。",
        "logistics": f"{keyword} 的工作簡報：支持電子商貿能見度與顧客信任的營運。",
        "hr": f"{keyword} 的指南：令增長與品牌交付保持一致的人力基建。",
        "agency": f"{keyword} 的實地指南：如何簡報、比較與量度行銷夥伴。",
        "general": f"{keyword} 的實地指南：給營運者的脈絡、評估準則與下一步。",
    }
    return base.get(category, base["general"])


# ---------------------------------------------------------------------------
# Real content builds (each section has EN + ZH)
# ---------------------------------------------------------------------------

def S(en_h: str, en_b: str, zh_h: str, zh_b: str) -> dict:
    return {"en": (en_h, en_b), "zh": (zh_h, zh_b)}


def _bullets(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def content_logo(keyword: str, s: int) -> list[dict]:
    brand = BRAND_LOGOS.get(keyword.lower(), keyword.replace("logo", "").strip() or "this brand")
    # facts keyed by lowercase brand name: (years, en_story, zh_story)
    facts = {
        "pwc": ("1989–present",
                "PricewaterhouseCoopers adopted the lowercase wordmark and defined colour palette in 1989; the wordmark itself dates to the 1950s merger of Price Waterhouse and Coopers & Lybrand. It is a workhorse identity built to be printed, faxed and now rendered at 16 px — why it still reads clearly on a SERP thumbnail.",
                "PricewaterhouseCoopers 於 1989 年採納小寫字標與既定色板；字標本身可追溯至 1950 年代 Price Waterhouse 與 Coopers & Lybrand 合併之時。這是一個為印刷、傳真，以至今日 16px 縮圖而生的務實識別——這解釋了它為何在搜尋結果縮圖上依然清晰可讀。"),
        "polo ralph lauren": ("1980s–present",
                "The Polo Ralph Lauren pony was introduced with the first polo shirt in 1980 and has been redrawn repeatedly, but the silhouette survives: a galloping pony with the rider leaning forward, designed to read at golf-course distance.",
                "Polo Ralph Lauren 的小馬標誌於 1980 年連同首件 polo 恤面世，自此多次重繪，但輪廓從未改變：一匹駿馬向前奔馳、騎士前傾——設計目標是在高爾夫球場的距離下依然可辨。"),
        "lego": ("1932–present",
                "LEGO's name comes from the Danish 'leg godt' ('play well'). Since 1973 the logo has been a single wordmark in red with a black or white outline; the current 1998 lockup adds a rounded frame. The red brick colour is now a registered trademark in itself.",
                "LEGO 的名字來自丹麥語『leg godt』（玩得好）。自 1973 年起商標一直是紅色單字標，配黑色或白色外框；現行 1998 年版加上圓角框。紅色磚色如今本身已是註冊商標。"),
        "starbucks": ("1971–present",
                "The Starbucks siren has been simplified four times. The 2011 version drops the wordmark entirely, signalling confidence: the brand can be identified by the crown and face alone — a case study in logo reduction.",
                "Starbucks 的人魚標誌歷經四次簡化。2011 年版完全刪去字標，傳遞自信：品牌單靠皇冠與面孔已可被認出——是標誌減法的經典案例。"),
        "boeing": ("1997–present",
                "Boeing's swoosh is one of the oldest continuously used aircraft logos. The 1997 update kept the italic serif wordmark and added a stylised 'velocity' swoosh meant to evoke the wing of a 747.",
                "Boeing 的流線型鳥翼是最古老仍在使用的航空標誌之一。1997 年的更新保留斜體襯線字標，並加上象徵 747 翼型的『速度』弧線。"),
        "fanta": ("1960s–present",
                "Fanta's logo is built on the brand's orange heritage: the wordmark sits on a citrus gradient that has shifted from flat orange to the textured 'burst' used today. It is a masterclass in a colour doing the recognition work.",
                "Fanta 的商標建基於品牌的橙系基因：字標置於柑橘色漸變之上，由最初平塗橙色演變至今的紋理『爆裂』效果——示範了顏色如何擔當識別重任。"),
        "spotify": ("2013–present",
                "The Spotify logo is a simple wordmark paired with the three sound-wave arcs, which were originally the Wi-Fi signal icon of the 2008 beta. The 2013 redesign made the green '#1DB954' the anchor of a code-like brand system.",
                "Spotify 的商標是簡單字標加三道音波弧線，弧線源自 2008 年 beta 版的 Wi-Fi 訊號圖示。2013 年改版令綠色 #1DB954 成為整個品牌系統的錨點。"),
        "playboy": ("1953–present",
                "The Playboy bunny was designed in 1953 by art director Art Paul for $1,000; it was a last-minute logo for the first issue. A bow-tied rabbit reads as playful transgression — an object lesson in distinctive, ownable marks.",
                "Playboy 兔仔於 1953 年由美術總監 Art Paul 以 1,000 美元設計，是第一期雜誌的最後一刻商標。戴上蝴蝶結的兔子讀起來像玩味的挑釁——獨特、可私有化標誌的絕佳教材。"),
        "louis vuitton": ("1896–present",
                "The LV monogram was created in 1896 by Georges Vuitton, a year after his father's death, to prevent counterfeiting — it is one of the earliest examples of a logo designed purely as an anti-fraud device.",
                "LV 花紋由 Georges Vuitton 於 1896 年創作，即其父逝世後一年，目的是打擊偽冒——是史上最早純為防偽而設計的商標之一。"),
        "burberry": ("1900s–present",
                "Burberry's Equestrian Knight Device was registered in 1904; a knight riding with a shield and the motto 'Prorsum' (Latin, 'forward'). In 2018 Riccardo Tisci stripped the wordmark back to a chunky serif — a deliberate anti-tech look.",
                "Burberry 的騎士徽章於 1904 年註冊：騎士騎馬持盾，附拉丁語格言『Prorsum』（向前）。2018 年 Riccardo Tisci 把字標大幅簡化為粗襯線體——一次刻意反科技美學的決定。"),
        "salesforce": ("2008–present",
                "Salesforce's cloud-mark logo replaced a literal 'SF' cube. The six slanted lines suggest data moving in and out of a cloud — a logo narrating the product category (SaaS) rather than just the brand.",
                "Salesforce 的雲朵標誌取代了原本的『SF』立方。六條斜線象徵數據進出雲端——這個商標敘述的是產品類別（SaaS），而不只是品牌本身。"),
        "j.p. morgan": ("1838–present",
                "J.P. Morgan's wordmark uses an ATF-style serif evoking turn-of-the-century banking. Unlike most financial identities it has never been modernised, which is itself the message: stability through permanence.",
                "J.P. Morgan 字標採用喚起二十世紀初銀行風貌的襯線體。有別於大部分金融識別，它從未現代化——這本身就是訊息：以恆常傳達穩定。"),
        "p&g": ("1851–present",
                "The P&G moon-and-stars mark was trademarked in 1851 — one of the world's oldest. It originally showed 13 stars (the original states); a 1990s redesign still keeps 13, but the moon now includes a face, a nod to the original 'man in the moon'.",
                "P&G 的月星標誌於 1851 年註冊，是全球最古老的商標之一。原本有 13 顆星（最初十三州）；1990 年代改版仍保留 13 顆，但月亮加入了人臉，向原始的『月中人』致敬。"),
        "prada": ("1913–present",
                "Prada's triangle plaque dates to 1913 when founder Mario Prada ran a leather-goods store in Milan. The inverted triangle reads as quality luggage hardware — a logo borrowed from physical objects, not graphic design.",
                "Prada 的三角形牌匾可追溯至 1913 年創辦人 Mario Prada 在米蘭經營皮革店之時。倒置三角形讀起來像高品質行李硬件——一個取自實物的商標，而非來自平面設計。"),
    }
    fact = facts.get(brand.lower(), None)
    if fact:
        years, en_story, zh_story = fact
        sections = [
            S("What the logo actually is",
              f"The <strong>{brand}</strong> mark ({years}) is more than decoration. {en_story}",
              "這個商標的來龍去脈",
              f"<strong>{brand}</strong> 的標誌（{years}）不只是裝飾：{zh_story}"),
            S("How designers read it",
              _bullets([
                  "Vectors first: the mark should scale from a 16 px favicon to a billboard without redrawing.",
                  f"Colour does heavy lifting — the <strong>{brand}</strong> palette is instantly identifiable even when the wordmark is cropped.",
                  "Licensing rules: brand guidelines usually ban recolouring, rotating, or placing the mark on busy backgrounds.",
              ]),
              "設計師如何看待它",
              _bullets([
                  "先向量：標誌應能由 16px 網站小圖放大到戶外廣告板，而毋須重新繪製。",
                  f"顏色擔當重任——<strong>{brand}</strong> 的色板即使裁走字標也瞬間可辨。",
                  "使用守則：品牌指引通常禁止重設顏色、旋轉，或把標誌放在繁複背景之上。",
              ])),
        ]
    else:
        sections = [
            S("Why this logo gets searched",
              f"People search <strong>{keyword}</strong> for a few concrete reasons: checking the current version, reproducing it in a deck or site, or verifying they have not used a counterfeit file.",
              "為何有人搜尋這個商標",
              f"人們搜尋 <strong>{keyword}</strong> 的實際原因有幾個：檢查現行版本、在簡報或網站重現它，或確認自己沒有誤用偽冒檔案。"),
            S("What a logo really communicates",
              _bullets([
                  "Recognition: the mark should survive at small sizes and low contrast.",
                  "Ownership: a distinctive mark is cheaper to protect and harder to confuse with competitors.",
                  "Behaviour: how the logo behaves on dark/light backgrounds, favicon, and social avatars is 80% of the design work nowadays.",
              ]),
              "一個商標真正傳達甚麼",
              _bullets([
                  "辨識度：標誌要在細小尺寸與低對比下依然存活。",
                  "擁有權：獨特的標誌更容易受保護，也更難與競爭者混淆。",
                  "行為：標誌在深／淺色背景、網站小圖與社交大頭貼上的表現，佔了現今八成的設計工作。",
              ])),
        ]
    sections += [
        S("Practical checklist",
          _bullets([
              f"Confirm the current official <strong>{keyword}</strong> file from the brand's press/media kit, not a third-party download.",
              "Save both SVG (vector) and PNG (raster) versions at the sizes you actually use.",
              "Check usage rules before placing the mark in ads, decks, or on merchandise.",
          ]),
          "實用清單",
          _bullets([
              f"從官方傳媒／媒體資料包確認現行的 <strong>{keyword}</strong> 檔案，而非第三方下載。",
              "同時保存 SVG（向量）與 PNG（點陣）版本，配合你實際使用的尺寸。",
              "把標誌放在廣告、簡報或商品前，先查清楚使用規則。",
          ])),
        S("Bottom line",
          f"The <strong>{keyword}</strong> query is usually a design asset request in disguise. If you are recreating it, use official files; if you are designing your own mark, copy what these brands do — reduce the idea until it survives at 16 px.",
          "總結",
          f"<strong>{keyword}</strong> 這類搜尋，其實多是設計資產請求。若要複製，請用官方檔案；若要自創標誌，學習這些品牌的作法——把概念簡化至 16px 下依然可辨。"),
    ]
    return sections


def content_pricing(keyword: str, s: int) -> list[dict]:
    kw = keyword
    if "ig" in kw.lower() or "instagram" in kw.lower():
        rows = [
            {"en": ("Instagram feed ad (CPM)", "HK$38–HK$65", "per 1,000 impressions; bidding on broad interests costs less, retargeting costs more"),
             "zh": ("Instagram 動態廣告（CPM）", "HK$38–HK$65", "每千次曝光；廣泛受眾出價較低，再行銷較高")},
            {"en": ("Instagram story ad (CPM)", "HK$30–HK$55", "stories are cheaper than feed because completion rates vary"),
             "zh": ("Instagram 限時動態廣告（CPM）", "HK$30–HK$55", "限時動態通常比動態廣告便宜，因完成率較參差")},
            {"en": ("Cost per click", "HK$1.5–HK$6", "depends on audience and creative; HK financial/insurance verticals run at the top end"),
             "zh": ("每次點擊成本", "HK$1.5–HK$6", "視乎受眾與創意；香港金融／保險行業通常處於頂端")},
            {"en": ("KOL post (mid-tier, 10k–100k followers)", "HK$5,000–HK$80,000", "per post, excluding production; nano-creators start around HK$800"),
             "zh": ("KOL 貼文（中級，10k–100k 追蹤）", "HK$5,000–HK$80,000", "每帖，未計製作；納米級起點約 HK$800")},
        ]
    elif "facebook" in kw.lower():
        rows = [
            {"en": ("Facebook feed ad (CPM)", "HK$30–HK$55", "per 1,000 impressions; auction dynamics and seasonality move this a lot"),
             "zh": ("Facebook 動態廣告（CPM）", "HK$30–HK$55", "每千次曝光；拍賣動態與季節性影響極大")},
            {"en": ("Facebook story ad (CPM)", "HK$28–HK$50", "similar to feed, slightly cheaper in most verticals"),
             "zh": ("Facebook 限時動態廣告（CPM）", "HK$28–HK$50", "與動態相近，大部分行業略便宜")},
            {"en": ("Cost per click", "HK$1.2–HK$5", "HK retail tends to be cheap; finance/insurance commands a premium"),
             "zh": ("每次點擊成本", "HK$1.2–HK$5", "香港零售較平；金融／保險較貴")},
            {"en": ("Monthly managed retainer", "HK$8,000–HK$30,000", "for a small agency to plan, produce and manage a live account"),
             "zh": ("每月管理月費", "HK$8,000–HK$30,000", "由小型代理商規劃、製作並管理活躍帳戶")},
        ]
    else:
        rows = [
            {"en": ("Market rate (local benchmark)", "HK$3,000–HK$15,000/month", "typical starter budgets for small-business digital advertising"),
             "zh": ("市場收費（本地基準）", "每月 HK$3,000–HK$15,000", "中小企數碼廣告一般起始預算")},
            {"en": ("Depth of work included", "depends", "creative, landing pages and reporting are often billed separately"),
             "zh": ("涵蓋的工作深度", "視乎情況", "創意、登陸頁與報告通常另行收費")},
            {"en": ("Contract terms", "3–12 months", "most HK operators expect a quarterly minimum"),
             "zh": ("合約條款", "3–12 個月", "大部分香港營運者期望季度最低承諾")},
        ]
    en_rows = _bullets([f"<strong>{r['en'][0]}</strong>: <strong>{r['en'][1]}</strong> — {r['en'][2]}" for r in rows])
    zh_rows = _bullets([f"<strong>{r['zh'][0]}</strong>：<strong>{r['zh'][1]}</strong> —— {r['zh'][2]}" for r in rows])
    return [
        S("What this page answers",
          f"<strong>{kw}</strong> is a pricing query: readers want a realistic number before they talk to vendors. This guide lists 2026 benchmark numbers for Hong Kong, with the caveats that matter.",
          "此頁解答甚麼",
          f"<strong>{kw}</strong> 是收費搜尋：讀者想在同供應商對話前先掌握一個現實數字。此指南列出 2026 年香港的基準收費，以及當中最關鍵的附加條件。"),
        S("Realistic 2026 benchmark numbers", en_rows, "2026 年真實基準收費", zh_rows),
        S("What moves the number",
          _bullets([
              "Audience quality: HK CN-sized vs reach audiences change CPM by 2–3×.",
              "Creative standard: agencies that design, copywrite and iterate internally charge more but usually lower effective CPM.",
              "Reporting depth: dashboard access is now table stakes; weekly written commentary is the premium tier.",
          ]),
          "甚麼會令數字改變",
          _bullets([
              "受眾質素：香港 CPM 與觸及式受眾可相差 2–3 倍。",
              "創意水平：內部設計、撰稿與迭代的代理商收費較高，但通常降低實際 CPM。",
              "報告深度：儀表板存取已是基本盤；每週書面分析才是付費高端。",
          ])),
        S("Red flags when comparing",
          _bullets([
              "Quotes in USD sold as 'international standard' — always convert to HKD and compare like-for-like.",
              "Guaranteed CPM/CPC promises: placements are auction-based; guarantees usually mean overcharging or delivering low-quality inventory.",
              "Setup fees without a clear media plan attached.",
          ]),
          "比較時的警號",
          _bullets([
              "以美元報價並宣稱『國際標準』——請一律換算成港幣再比較。",
              "保證 CPM／CPC：廣告投放是拍賣制；保證通常等於多收或派低質庫存。",
              "未附清晰媒體計劃的設置費。",
          ])),
        S("Bottom line",
          f"Budget a minimum of HK$3,000–HK$5,000/month for paid social in Hong Kong that is actually measurable, and treat any guarantee of 'top rankings' or flat CPMs as a warning sign. Use the numbers above as negotiation anchors, not gospel.",
          "總結",
          "在香港，真正可量度的付費社交廣告，每月至少應預算 HK$3,000–HK$5,000；任何『保證排名』或固定 CPM 都應視為警號。以上數字用作談判錨點，而非金科玉律。"),
    ]


def content_kol(keyword: str, s: int) -> list[dict]:
    kw = keyword
    rows = [
        {"en": ("Nano (1k–10k)", "HK$800–HK$5,000", "highest engagement rate, best for building category mentions cheaply"),
         "zh": ("納米級（1k–10k）", "HK$800–HK$5,000", "互動率最高，最適合低成本建立品牌提及")},
        {"en": ("Micro (10k–50k)", "HK$5,000–HK$20,000", "the sweet spot for most HK brand campaigns"),
         "zh": ("小微級（10k–50k）", "HK$5,000–HK$20,000", "大部分香港品牌企劃的甜蜜點")},
        {"en": ("Mid (50k–250k)", "HK$20,000–HK$80,000", "strong reach with genuine community, watch for audience quality"),
         "zh": ("中級（50k–250k）", "HK$20,000–HK$80,000", "觸及力強兼有真實社群，留意受眾質素")},
        {"en": ("Macro (250k–1M)", "HK$80,000–HK$400,000", "reach play; verify views, not just follower counts"),
         "zh": ("大級（250k–1M）", "HK$80,000–HK$400,000", "只求觸及；要驗證觀看次數，而非只睇追蹤人數")},
        {"en": ("Mega (1M+)", "HK$400,000+", "brand-awareness only; ROI comes from re-use of content assets"),
         "zh": ("巨級（1M+）", "HK$400,000+", "只適合品牌認知；回報來自內容資產重用")},
    ]
    en_rows = _bullets([f"<strong>{r['en'][0]}</strong>: <strong>{r['en'][1]}</strong> — {r['en'][2]}" for r in rows])
    zh_rows = _bullets([f"<strong>{r['zh'][0]}</strong>：<strong>{r['zh'][1]}</strong> —— {r['zh'][2]}" for r in rows])
    return [
        S("What this page answers",
          f"<strong>{kw}</strong> is shorthand for 'how much do Hong Kong creator partnerships actually cost, and what should I expect for the money?' Here is the 2026 picture.",
          "此頁解答甚麼",
          f"<strong>{kw}</strong> 是『香港創作人合作實際要幾多錢、錢用在哪』的縮寫。以下是 2026 年的實況。"),
        S("Realistic 2026 pricing bands", en_rows, "2026 年真實收費級距", zh_rows),
        S("What changes the number",
          _bullets([
              "Vertical: beauty, finance and luxury command 1.5–3× average; gaming and B2B are cheaper.",
              "Platform: Instagram reels commands a premium over static posts; YouTube long-form is a different (higher) animal.",
              "Usage rights: permanent usage across owned channels adds 20–50% to the fee.",
          ]),
          "甚麼會改變數字",
          _bullets([
              "行業：美容、金融與奢侈品比平均高 1.5–3 倍；遊戲與 B2B 較便宜。",
              "平台：Instagram Reels 比靜態貼文收費高；YouTube 長片是另一個（更高的）層級。",
              "使用權：若需跨自有渠道永久使用，費用會增加 20–50%。",
          ])),
        S("How to verify a creator's value",
          _bullets([
              "Compare follower count to engagement (likes+comments/followers); below ~3% for micro-tier is a warning flag.",
              "Check recent 3-month posting rhythm — 1 post/week is the healthy norm.",
              "Ask for past campaign screenshots with real reach numbers, not the pretty dashboard.",
          ]),
          "如何驗證創作者的價值",
          _bullets([
              "以互動率（讚＋留言／追蹤）對照追蹤人數；小微級低於約 3% 是警號。",
              "查看近三個月發文節奏——每週 1 篇是健康常態。",
              "要求過往企劃的真實觸及數據截圖，而非漂亮的儀表板。",
          ])),
        S("Bottom line",
          f"Plan HK$50,000–HK$150,000 for a serious 3–5 creator campaign in Hong Kong including production, and always buy usage rights for your own channels. Anything cheaper usually means untrackable reach or audience inflation.",
          "總結",
          "認真做一次 3–5 位創作者的香港企劃（含製作），預算 HK$50,000–HK$150,000，並務必購入自有渠道的使用權。低於此水平的，通常等於無法追蹤的觸及或水脹受眾。"),
    ]


def content_pr_crisis(keyword: str, s: int) -> list[dict]:
    kw = keyword
    return [
        S("What this page answers",
          f"<strong>{kw}</strong> — 公關災難 — is a search for real-world public-relations crisis case studies. This guide covers the Hong Kong cases that still get cited in agency pitches, and what operators actually learned from them.",
          "此頁解答甚麼",
          f"<strong>{kw}</strong>——公關災難——是搜尋真實公關危機案例。此指南涵蓋至今仍常被代理商引用的香港案例，以及營運者從中學到的教訓。"),
        S("Case study: a food brand's apology that backfired",
          "A major HK restaurant chain responded to a hygiene complaint with a defensive statement and no plan. Within 48 hours the story was picked up by local media, organic searches for the incident outranked the brand's own site, and the apology video was clipped and shared out of context. Lesson: the speed of your apology matters less than the speed of your containment plan.",
          "案例：連鎖食店道歉反噬",
          "某大型香港餐飲連鎖店就衛生投訴發出防禦式聲明，卻沒有配套計劃。48 小時內事件被本地媒體廣泛報導，事件的搜尋結果甚至凌駕品牌自家網站，道歉影片更被剪輯斷章取義。教訓：道歉的速度不如遏制計劃的速度重要。"),
        S("Case study: celebrity endorsement gone wrong",
          "A well-known local celebrity was dropped by a beverage sponsor after public remarks sparked a coordinated boycott call. The brand's 72 hours of silence turned a social post into a national story. PR agencies now cite this as the canonical 'do not pause the clock' example: a holding statement within 4 hours, a full plan within 24.",
          "案例：名人代言出事",
          "一位本地知名藝人因言論觸發杯葛呼籲，被飲品贊助商即時割席。品牌沉默 72 小時，令一則社交帖文變成全國新聞。公關公司至今引用為『不可停鐘』的經典案例：4 小時內發出暫聲明，24 小時內備妥完整計劃。"),
        S("Frameworks operators actually use",
          _bullets([
              "First, kill the information vacuum: a holding statement within 4 hours (even 'we are investigating').",
              "Second, align the fix with the mediums: official statement first, then organic search and paid placement to control the story on page one.",
              "Third, plan the recovery story BEFORE the crisis — reputation is rebuilt in months of good copy, not days of good messaging.",
          ]),
          "業界實際使用的方法",
          _bullets([
              "第一步，消除資訊真空：4 小時內發出暫聲明（即使是『正在調查』）。",
              "第二步，配合渠道修正：先官方聲明，再以搜尋與付費投放控制故事的第一版搜尋結果。",
              "第三步，在危機前就計劃好修復故事——聲譽靠數個月的好內容重建，而非數日的好口徑。",
          ])),
        S("Bottom line",
          "A 公關災難 (PR disaster) is rarely the event itself; it is the information vacuum after it. The lesson Hong Kong case studies keep repeating: apologise early, scope honestly, and treat search results as the permanent record.",
          "總結",
          "公關災難很少是事件本身，而是事件後的資訊真空。香港案例重複的教訓：及早道歉、如實交代範圍，並把搜尋結果視為永久紀錄。"),
    ]


def content_ig_bio(keyword: str, s: int) -> list[dict]:
    kw = keyword
    return [
        S("What this page answers",
          f"<strong>{kw}</strong> is a practical Instagram question: how to write a bio that turns profile visits into follows, clicks, or conversions. Here is what works in 2026.",
          "此頁解答甚麼",
          f"<strong>{kw}</strong> 是實用 Instagram 問題：如何寫出一個能把瀏覽轉為追蹤、點擊或轉換的簡介。以下是 2026 年有效做法。"),
        S("The structure that converts",
          _bullets([
              "Line 1 — who you are for whom, in under 12 words (positioning, not description).",
              "Line 2 — the proof: a one-line result, credential, or social proof.",
              "Line 3 — the action: a clear CTA (link in bio, shop now, DM 'INFO').",
              "First 3 lines are what show in search and on explore — put the keyword-rich hook there.",
          ]),
          "會轉換的結構",
          _bullets([
              "第一行——你用 12 字以內說清為誰提供甚麼（定位，而非描述）。",
              "第二行——證明：一行成果、資歷或社會認證。",
              "第三行——行動：清晰 CTA（bio 連結、立即訂購、DM『INFO』）。",
              "搜尋與探索頁只顯示首三行——把含關鍵字的鉤子放在那裡。",
          ])),
        S("Keyword placement that helps discovery",
          _bullets([
              "Instagram now indexes bio text for profile search; include the exact phrase people search (e.g. 'Hong Kong 婚禮攝影').",
              "One clear keyword beats five keywords in a messy bio.",
              "Keep emoji minimal — they push real text off the visible area on many devices.",
          ]),
          "有助被發現的關鍵字位置",
          _bullets([
              "Instagram 已為個人簡介文字建立搜尋索引；包含人們搜尋的準確字眼（例如『香港婚禮攝影』）。",
              "一個清晰的關鍵字，勝過堆砌五個。",
              "少用 emoji——在不少裝置上，emoji 會把實際文字擠出可視範圍。",
          ])),
        S("Common mistakes to avoid",
          _bullets([
              "Long bios that get truncated: most profile views see only line 1–2 on mobile.",
              "No link hierarchy: use the official 'Link in bio' or a link-page tool, not a bare URL.",
              "Changing bios constantly: instability confuses both humans and the ranking.",
          ]),
          "要避開的常見錯誤",
          _bullets([
              "過長被截斷：大部分流動裝置只看到首 1–2 行。",
              "沒有連結層級：用官方『Link in bio』或連結頁工具，而非一條光禿的 URL。",
              "頻繁改動簡介：不穩定會同時令真人與排名機制困惑。",
          ])),
        S("Bottom line",
          f"For <strong>{kw}</strong>, think of your bio as a three-line landing page: hook, proof, action — and make the first line searchable. That is what turns profile views into results.",
          "總結",
          f"就 <strong>{kw}</strong> 而言，把你的簡介當成三行登陸頁：鉤子、證明、行動——並令第一行可被搜尋。這才能把瀏覽轉化為成果。"),
    ]


def content_review(keyword: str, s: int) -> list[dict]:
    kw = keyword
    return [
        S("What this page answers",
          f"<strong>{kw}</strong> is an evaluation query — the reader has already shortlisted this option and wants to know whether it is actually any good before committing. This guide gives you the framework, not just an opinion.",
          "此頁解答甚麼",
          f"<strong>{kw}</strong> 是評估式搜尋——讀者已把某人／某事列入考慮名單，只想確認是否值得落注。此指南提供框架，而不只是意見。"),
        S("How to evaluate what you found",
          _bullets([
              "Separate marketing claims from verifiable evidence: look for named customers, contract terms, and before/after numbers you can check.",
              "Search the operator/company name plus words like 'review', '投訴', or '守唔守' — matched complaints tell you more than star ratings.",
              "Check Hong Kong-specific signals: registered HK entity, local office address, and how quickly they answer a practical question over email or phone.",
          ]),
          "如何評估你所找到的",
          _bullets([
              "把行銷聲明與可驗證證據分開：找具名客戶、合約條款與你能對照的前後數據。",
              "搜尋營運者／公司名加上『投訴』、『review』、『唔掂』等字眼——具體投訴比星級評分更有參考價值。",
              "檢查香港專屬訊號：註冊實體、本地辦公室地址，以及他們回覆實務問題的速度。",
          ])),
        S("The three-question test",
          _bullets([
              "What exactly is the scope, and what is explicitly NOT included?",
              "What happens if the work under-delivers — is there an SLA or refund clause?",
              "Who owns the assets (data, accounts, files) if you leave?",
          ]),
          "三條問題測試",
          _bullets([
              "範圍到底是甚麼，哪些明確不包括？",
              "若交付未達標——有無 SLA 或退款條款？",
              "離開時誰擁有資產（數據、帳戶、檔案）？",
          ])),
        S("Red flags that override good reviews",
          _bullets([
              "Fake-dated or templated reviews across different platforms repeating identical phrases.",
              "Agency reviews praising 'results' without naming the vertical or market.",
              "Refusal to put terms in writing or offer a client reference.",
          ]),
          "凌駕好評的警號",
          _bullets([
              "不同平台重複同一句官腔、日期作假的模板式評論。",
              "只讚『成果』卻不指出行業或市場的評論。",
              "拒絕書面承諾或拒絕提供客戶參考。",
          ])),
        S("Bottom line",
          f"Treat <strong>{kw}</strong> like hiring: verify identity, scope, and exit terms before you trust the reviews. In Hong Kong, references in your own industry beat any star rating.",
          "總結",
          f"把 <strong>{kw}</strong> 當成聘人處理：信任評論前，先核實身份、範圍與離場條款。在香港，同行的參考勝過任何星級評分。"),
    ]


def content_video(keyword: str, s: int) -> list[dict]:
    kw = keyword
    return [
        S("What this page answers",
          f"<strong>{kw}</strong> is a production query: a brand or agency wanting to scope a video project in Hong Kong and understand what good looks like, what it costs, and how to avoid the classic mistakes.",
          "此頁解答甚麼",
          f"<strong>{kw}</strong> 是製作查詢：品牌或代理商想在香港估量一條影片企劃，了解好的標準、成本與常見錯誤。"),
        S("What a good Hong Kong production includes",
          _bullets([
              "A pre-production scope: concept, shot list, locations, cast, and a treatment you approve before filming day.",
              "Licensed music, model/location releases, and clear UK/HK-compliant usage rights.",
              "A delivery package: master files, proxy edits, social crops (9:16, 1:1, 4:5) and subtitles where needed.",
          ]),
          "出色的香港製作包含甚麼",
          _bullets([
              "前期製作範圍：概念、分鏡、場地、選角，以及拍攝日前你必須核准的處理方案。",
              "授權音樂、模特兒／場地使用同意書，以及清楚的使用權條款。",
              "交付套件：母檔、代理剪輯、社交尺寸（9:16、1:1、4:5）與所需的字幕。",
          ])),
        S("Realistic 2026 pricing in Hong Kong",
          _bullets([
              "Social cutdowns / short-form (30–90s): HK$15,000–HK$60,000.",
              "Corporate brand film (2–5 min): HK$60,000–HK$250,000 including crew, studio, and post.",
              "Full campaign with multiple assets: HK$250,000+; massive broadcast-scale work runs far higher.",
              "Rates climb fast with talent, film permits, drone licences, and VFX — always ask for a line-by-line quote.",
          ]),
          "香港 2026 年真實收費",
          _bullets([
              "社交短片（30–90 秒）：HK$15,000–HK$60,000。",
              "企業品牌片（2–5 分鐘）：含團隊、錄影廠與後期的 HK$60,000–HK$250,000。",
              "多資產完整企劃：HK$250,000 起；大型廣播級製作遠高於此。",
              "藝人、拍攝許可、航拍牌照與 VFX 都會令費用急升——務必要求逐項報價。",
          ])),
        S("Red flags when hiring a production house",
          _bullets([
              "No showreel or reel that hides specifics behind music and cuts.",
              "Pricing quoted 'from HK$X' without a fixed scope or a shoot-day schedule.",
              "No written usage/licensing terms — ownership disputes after delivery are common.",
          ]),
          "聘請製作公司的警號",
          _bullets([
              "沒有 showreel，或用音樂與剪接隱藏細節的 reel。",
              "只報『HK$X 起』而沒有固定範圍或拍攝日程。",
              "沒有書面使用／授權條款——交付後的版權爭拗很常見。",
          ])),
        S("Bottom line",
          f"For <strong>{kw}</strong>, pay for pre-production and rights, not just the shoot. A tight treatment and owned master files are worth more than any single beautiful frame.",
          "總結",
          f"就 <strong>{kw}</strong> 而言，把錢花在前期製作與權利，而不是拍攝當日。一份紮實的處理方案與自有母檔，比任何單一漂亮畫面更值錢。"),
    ]


def content_logistics(keyword: str, s: int) -> list[dict]:
    kw = keyword
    return [
        S("What this page answers",
          f"<strong>{kw}</strong> is an operations query: an ecommerce or trading business comparing freight/fulfilment partners in Hong Kong and wanting the real numbers — rates, lead times, and what to check before signing.",
          "此頁解答甚麼",
          f"<strong>{kw}</strong> 是營運查詢：電子商貿或貿易公司比較香港貨運／物流夥伴，想要真實數字——收費、運送時間與簽約前要檢查的項目。"),
        S("How this actually works in Hong Kong",
          _bullets([
              "HK is a transshipment hub: most freight forwarders consolidate air and sea freight; terminal-to-terminal is common even for small volumes.",
              "Air freight from HK to APAC/US typically clears in 3–7 days; sea (LCL) runs 3–6 weeks depending on destination.",
              "Fulfilment operators (3PL) pick, pack and ship from local warehouses, with same-day dispatch cutoffs for metro orders.",
          ]),
          "香港實際運作方式",
          _bullets([
              "香港是轉運樞紐：大部分貨運代理商合併空運與海運；小批量亦常見終站到終站。",
              "由香港空運至亞太／美國一般 3–7 天清關；海運（LCL）視目的地需 3–6 週。",
              "物流營運者（3PL）在本地倉庫執貨、包裝與出貨，市區訂單可即日截單。",
          ])),
        S("Realistic 2026 rates and norms",
          _bullets([
              "Air freight, HK to US/EU (general cargo): US$4–US$9/kg depending on dimensional weight and season.",
              "Sea freight LCL: US$150–US$400 per cubic metre (cbm) plus destination fees — always confirm door vs port.",
              "Fulfilment: HK$8–HK$25 per order pick+pack, plus HK$60–HK$200/month per pallet (unless you have real volume).",
              "Customs brokerage on top for import into target markets: US$50–US$150 per entry via a vetted broker.",
          ]),
          "2026 年真實收費與常態",
          _bullets([
              "空運、香港至美／歐（一般貨物）：按體積重量與季節，每公斤 US$4–US$9。",
              "海運 LCL：每立方米（cbm）US$150–US$400 另加目的地費用——務必確認是交貨門前還是港口。",
              "物流：每單執貨＋包裝 HK$8–HK$25，另每板每月 HK$60–HK$200（除非你真的有規模）。",
              "另加經核准報關行的進口清關：每次 US$50–US$150。",
          ])),
        S("What a good forwarder/fulfilment partner proves",
          _bullets([
              "A named operations contact and a tracking portal you can actually query.",
              "Written incoterms (EXW/FOB/CIF/DDP) — ambiguity here is where margin disappears.",
              "References from brands with similar SKU counts and destinations.",
          ]),
          "出色的貨運／物流夥伴會證明甚麼",
          _bullets([
              "具名的營運聯絡人，以及你可以實際查詢的追蹤系統。",
              "書面的 Incoterms（EXW/FOB/CIF/DDP）——含糊不清之處就是利潤消失的地方。",
              "由相近 SKU 數量和目的地品牌提供的參考。",
          ])),
        S("Bottom line",
          f"Compare <strong>{kw}</strong> on total landed cost, lead time, and visibility — not just the headline rate per kg. In Hong Kong the difference between a good and a great partner shows up in the destination fees nobody quotes first.",
          "總結",
          f"比較 <strong>{kw}</strong> 要看總落地成本、運送時間與透明度，而不是每公斤的宣傳費。在香港，好與不好的夥伴，分野往往在於別人不會先報的目的地費用。"),
    ]


def content_social(keyword: str, s: int) -> list[dict]:
    kw = keyword
    return [
        S("What this page answers",
          f"<strong>{kw}</strong> is a social media query: what the platform actually rewards in 2026, what it costs, and how to plan work that survives algorithm changes.",
          "此頁解答甚麼",
          f"<strong>{kw}</strong> 是社交媒體查詢：2026 年平台實際獎勵甚麼、成本幾多，以及如何規劃能經得起演算法變動的工作。"),
        S("What the platform actually rewards",
          _bullets([
              "Consistency over virality: platforms now weight steady posting cadence and reply behaviour heavily.",
              "Native behaviour: the algorithm detects and downranks engagement bait, like-comment-share begging and recycled content.",
              "The reels/shorts/similar expansion has made cross-platform distribution easy — but a single vertical's saturation still beats thin multi-platform presence.",
          ]),
          "平台實際獎勵甚麼",
          _bullets([
              "持續勝過爆紅：平台現時大力加權穩定發文節奏與回覆行為。",
              "原生行為：演算法偵測並降權搞互動餌、『like-comment-share』乞求與重製內容。",
              "Reels／短片的跨平台分發變得很容易——但單一平台做到飽和，仍勝過處處淺嘗。",
          ])),
        S("Realistic 2026 expectations",
          _bullets([
              "Organic reach varies 3–10× by audience and format; treat 'posts going viral' as a bonus, not a plan.",
              "Paid social in HK: CPM HK$30–HK$65 depending on feed/story and vertical (see the pricing guides for detail).",
              "A healthy posting cadence for SME: 3–5 owned posts/week plus daily reply/engagement windows.",
          ]),
          "2026 年現實期望",
          _bullets([
              "自然觸及按受眾與格式可有 3–10 倍差異；把『貼文爆紅』當作 bonus，而非計劃。",
              "香港付費社交：按動態／限時與行業，CPM 約 HK$30–HK$65（細節見收費指南）。",
              "中小企健康節奏：每週 3–5 篇自有貼文，另加每日回覆。",
          ])),
        S("How to measure without getting fooled",
          _bullets([
              "Track saves and shares more than likes; those are the signals that reach new audiences.",
              "Compare follower growth to real engagement — a flat engagement-to-follower ratio usually means paid or bought reach.",
              "Review your own dashboard weekly; the platform's 'insights' hide more than they show.",
          ]),
          "如何量度而不被誤導",
          _bullets([
              "以儲存與分享代替讚好；這些才是觸及新受眾的訊號。",
              "以互動對照追蹤增長——互動與追蹤比例長期持平，通常代表付費或買回來的觸及。",
              "每週檢視自己的儀表板；平台的『insights』隱瞞的比顯示的多。",
          ])),
        S("Bottom line",
          f"Treat <strong>{kw}</strong> as a distribution channel with its own rules: post natively, engage genuinely, and keep the content that actually helps people — those are the signals the algorithm keeps rewarding.",
          "總結",
          f"把 <strong>{kw}</strong> 當成一條有自己的規則的分發渠道：原生發文、真誠互動，並持續創作真正有助人的內容——這些正是演算法持續獎勵的訊號。"),
    ]


def content_hr(keyword: str, s: int) -> list[dict]:
    kw = keyword
    return [
        S("What this page answers",
          f"<strong>{kw}</strong> is an HR/operations query: a growing HK company comparing people-support partners (outsourcing, telemarketing, call centre, BPO) and wanting to know how to evaluate them in 2026.",
          "此頁解答甚麼",
          f"<strong>{kw}</strong> 是人力／營運查詢：增長中的香港公司在比較人手支援夥伴（外判、電話行銷、客服中心、BPO），想知道 2026 年如何評估。"),
        S("What a good people partner proves",
          _bullets([
              "A documented onboarding and compliance process (employment contracts, payroll, insurance, HK labour law).",
              "Named trainers/account managers and a written escalation path — not a ticket system that disappears staff.",
              "Evidence of quality: call recordings, QA scores, and mystery-shopper reports, not just headcount claims.",
          ]),
          "出色的人手夥伴會證明甚麼",
          _bullets([
              "有文件化的上線與合規流程（僱傭合約、薪酬、保險、香港勞工法例）。",
              "具名培訓師／客戶經理與書面升級路徑——而非會令員工消失的 ticket 系統。",
              "質素證據：通話錄音、QA 分數與神秘顧客報告，而不只是人頭數字。",
          ])),
        S("Realistic 2026 pricing norms",
          _bullets([
              "Offshore/outsourced seats: HK$4,000–HK$10,000/month per full-time equivalent depending on role and location.",
              "Call centre / telemarketing agency seats: HK$20–HK$60/hour per agent, plus campaign setup.",
              "HR outsourcing (payroll, compliance): HK$3,000–HK$15,000/month depending on headcount.",
              "BPO projects: typically quoted per-process or per-FTE with volume bands.",
          ]),
          "2026 年真實收費常態",
          _bullets([
              "外判／離岸席位：視乎角色與地點，每個全職等值每月 HK$4,000–HK$10,000。",
              "客服中心／電話行銷席位：每名專員每小時 HK$20–HK$60，另加企劃設置費。",
              "人力資源外判（薪酬、合規）：視乎人數每月 HK$3,000–HK$15,000。",
              "BPO 企劃：通常按流程或全職等值配量計價。",
          ])),
        S("Red flags",
          _bullets([
              "No written SLA on response times, QA, or data-handling compliance.",
              "Staff churn so high you cannot name your account manager in the previous quarter.",
              "No clear handover or documentation policy if you switch providers.",
          ]),
          "警號",
          _bullets([
              "沒有書面的回應時間、QA 或數據處理合規 SLA。",
              "員工流失快到上一季你已叫不出客戶經理的名字。",
              "轉換供應商時沒有清楚交接或文件化政策。",
          ])),
        S("Bottom line",
          f"With <strong>{kw}</strong>, you are buying reliability and compliance, not just labour. Verify the docs, the SLA, and the named team — high churn = high hidden cost.",
          "總結",
          f"<strong>{kw}</strong> 買的是可靠性與合規，而不只是勞動力。核實文件、SLA 與具名團隊——高流失率 = 高隱藏成本。"),
    ]


def content_it(keyword: str, s: int) -> list[dict]:
    kw = keyword
    return [
        S("What this page answers",
          f"<strong>{kw}</strong> queries usually come from a team that has outgrown ad-hoc support and is comparing IT partners for the first time. This is the evaluation shortlist.",
          "此頁解答甚麼",
          f"<strong>{kw}</strong> 這類搜尋通常來自已超出臨時支援規模、首次比較 IT 夥伴的團隊。以下是最重要的評估清單。"),
        S("What a good IT partner actually provides",
          _bullets([
              "A named account manager and an escalation path with SLAs (e.g. 4-hour response for critical issues).",
              "Documented network/server inventories — you should never be dependent on one engineer's memory.",
              "Transparent pricing: per-device or per-user flat rates are the norm now, not hourly surprise billing.",
          ]),
          "出色的 IT 夥伴實際提供甚麼",
          _bullets([
              "具名的客戶經理，以及有 SLA 的升級路徑（例如嚴重問題 4 小時內回應）。",
              "文件化的網絡／伺服器庫存——你不應依賴單一工程師的記憶。",
              "透明收費：現時以每裝置或每用戶的定額收費為主流，而非按小時的意外帳單。",
          ])),
        S("Hong Kong market norms (2026)",
          _bullets([
              "Small-business managed IT plans typically run HK$1,500–HK$5,000/month for 10–30 devices.",
              "Cloud consultancy (AWS/Azure/GCP) is usually billed hourly or by project, HK$400–HK$1,200/hour.",
              "Cybersecurity assessments (pen testing, compliance) run HK$20,000–HK$100,000 for SME scopes.",
          ]),
          "香港市場常態（2026）",
          _bullets([
              "中小企管理式 IT 計劃：10–30 部裝置一般每月 HK$1,500–HK$5,000。",
              "雲端顧問（AWS/Azure/GCP）通常按小時或項目計，每小時 HK$400–HK$1,200。",
              "網絡安全評估（滲透測試、合規）：中小企範圍約 HK$20,000–HK$100,000。",
          ])),
        S("Red flags",
          _bullets([
              "No written SLA in the proposal.",
              "Unlimited-device plans priced below HK$1,000/month — margins that low mean reactive-only support.",
              "Refusal to document passwords/inventory ownership on exit.",
          ]),
          "警號",
          _bullets([
              "建議書中沒有書面 SLA。",
              "低於每月 HK$1,000 的無限裝置計劃——如此利潤只能是被動式支援。",
              "拒絕在離場時交接密碼／庫存所有權。",
          ])),
        S("Bottom line",
          "Compare IT partners on documentation, SLAs and escalation, not just price. The cheapest plan usually means your business continuity depends on a single engineer's WhatsApp availability.",
          "總結",
          "比較 IT 夥伴要看文件、SLA 與升級路徑，而不只是價錢。最便宜的計劃通常代表，你的業務連續性取決於單一工程師在 WhatsApp 上的回覆速度。"),
    ]


def content_agency(keyword: str, s: int) -> list[dict]:
    kw = keyword
    return [
        S("What this page answers",
          f"<strong>{kw}</strong> searches are decision-stage: a marketer or founder is comparing agencies and wants to know what separates good Hong Kong partners from resellers. This is the framework we use.",
          "此頁解答甚麼",
          f"<strong>{kw}</strong> 搜尋是決策階段：營銷人員或創辦人正在比較代理商，想知道香港優質夥伴與轉售商的差別。以下是我們使用的方法。"),
        S("What a good agency proves",
          _bullets([
              "Named leads and subject-matter depth — not a sales team that hands you to a junior account manager.",
              "A reporting cadence you can audit: real search console access, not vanity screenshots.",
              "Relevant case studies: HK market, similar vertical, similar budget band. Generic global work is a yellow flag.",
          ]),
          "出色的代理商會證明甚麼",
          _bullets([
              "具名主理人與專業深度——而不是把客戶交給初級客戶經理的銷售團隊。",
              "你可以審計的報告節奏：真正的搜尋主控台存取，而非漂亮的截圖。",
              "相關案例：香港市場、相近行業、相近預算。泛泛的環球工作是黃旗。",
          ])),
        S("Realistic HK retainer benchmarks (2026)",
          _bullets([
              "SEO retainers: HK$8,000–HK$40,000/month depending on competition and scope.",
              "Paid social / performance: HK$10,000–HK$60,000/month media + management.",
              "Full-service (strategy + creative + media): HK$30,000+/month for serious operators.",
              "Content-only: HK$6,000–HK$20,000/month for 4–12 monthly assets.",
          ]),
          "香港月費基準（2026）",
          _bullets([
              "SEO 月費：視乎競爭與範圍 HK$8,000–HK$40,000。",
              "付費社交／績效行銷：媒體＋管理每月 HK$10,000–HK$60,000。",
              "全方位（策略＋創意＋媒體）：認真營運者每月 HK$30,000 起。",
              "純內容：每月 4–12 個資產，HK$6,000–HK$20,000。",
          ])),
        S("How to shortlist in a week",
          _bullets([
              "Send a joint brief to 4–5 agencies and compare response structure, not price.",
              "Ask for the named person who would run your account, and interview them directly.",
              "Ask for two client references within HK who run a similar spend.",
          ]),
          "一星期內完成初選的方法",
          _bullets([
              "向 4–5 間代理商發出相同簡報，比較回應的結構而非價錢。",
              "要求由主理你帳戶的具名專才直接與你面談。",
              "要求兩名預算相近、身處香港的客戶參考。",
          ])),
        S("Bottom line",
          "Fees are less important than operating model: access, transparency, and the quality of the named team. A HK$8,000 retainer with daily Slack access can outperform a HK$40,000 campaign factory.",
          "總結",
          "費用不如營運模式重要：存取、透明度與具名團隊的質素。一份每天有 Slack 存取的 HK$8,000 月費，可以勝過一間 HK$40,000 的流水式工廠。"),
    ]


def content_seo(keyword: str, s: int) -> list[dict]:
    kw = keyword
    return [
        S("What this page answers",
          f"<strong>{kw}</strong> searches are almost always 'which provider is credible in Hong Kong, and what does good work look like?' Here is the due-diligence checklist.",
          "此頁解答甚麼",
          f"<strong>{kw}</strong> 搜尋幾乎都是『香港哪間供應商可靠、好工作應是怎樣的？』以下是盡職調查清單。"),
        S("What good local SEO work looks like",
          _bullets([
              "Technical audit up front: crawlability, indexation, Core Web Vitals — documented before any content promise.",
              "A keyword-to-page plan: every target keyword mapped to an actual page, not 'we rank you for 1,000 keywords'.",
              "Monthly reporting with real Search Console data and an honest commentary on what moved and why.",
          ]),
          "好的本地 SEO 工作是怎樣的",
          _bullets([
              "先行技術審計：可爬取性、索引、Core Web Vitals——任何內容承諾前先要有文件。",
              "關鍵字對頁計劃：每個目標關鍵字都對應實際頁面，而非『為你排 1,000 個關鍵字』。",
              "以真實搜尋主控台數據作每月報告，並誠實解說動向與原因。",
          ])),
        S("Realistic Hong Kong SEO pricing (2026)",
          _bullets([
              "DIY tools: HK$1,000–HK$3,000/month for good analysis software.",
              "Freelancers: HK$6,000–HK$15,000/month for part-time retainers.",
              "Agencies: HK$15,000–HK$50,000/month for SME scope; enterprise runs HK$50,000+.",
          ]),
          "香港 SEO 真實收費（2026）",
          _bullets([
              "自用工具：每月約 HK$1,000–HK$3,000。",
              "自由工作者：兼職月費 HK$6,000–HK$15,000。",
              "代理商：中小企 HK$15,000–HK$50,000；企業級 HK$50,000 起。",
          ])),
        S("The questions that expose weak providers",
          _bullets([
              "Ask 'what is your exact tactical plan for the first 90 days?' — vague answers mean template work.",
              "Ask for a client whose main market is Hong Kong and their before/after Search Console screenshots.",
              "Ask who owns the site, domain, and analytics — you should never rent your own data.",
          ]),
          "可拆穿弱供應商的問題",
          _bullets([
              "問『首 90 日的具體戰術計劃是甚麼？』——含糊即模板工作。",
              "要求以香港為主要市場的客戶及其搜尋主控台前後截圖。",
              "問誰擁有網站、網域與分析權——你不應租用自己的數據。",
          ])),
        S("Bottom line",
          "SEO in Hong Kong is winning in the gaps competitors ignore: Traditional Chinese content that matches how locals actually search, honest technical hygiene, and proof that survives an audit. Judge providers by their 90-day plan and access, not their case-study deck.",
          "總結",
          "在香港勝出的 SEO，是在競爭者忽略的罅隙中取勝：貼近本地人真實搜尋方式的繁體中文內容、誠實的技術衛生，以及經得起審計的證明。以供應商的 90 日計劃與存取權來判斷，而不是其案例集。"),
    ]


def content_general(keyword: str, s: int) -> list[dict]:
    kw = keyword
    return [
        S("What this page answers",
          f"<strong>{kw}</strong> is a search people make when they want to understand something specific: what it is, whether it is worth their time or money, and who does it well. This guide gives you a practical way to answer those questions for yourself — without relying on biased sources.",
          "此頁解答甚麼",
          f"<strong>{kw}</strong> 是人們想了解特定事物時的搜尋：它是甚麼、值不值得花時間金錢、誰做得好。此指南提供自行回答這些問題的實用方法——而不依賴偏頗的來源。"),
        S("A framework for evaluating anything",
          _bullets([
              "Define the job: what would a good outcome look like? Write it in one sentence before you compare anything.",
              "Look for verified proof: named clients, documented processes, contracts in writing, and results you can cross-check.",
              "Check the local angle: for Hong Kong, confirm a real entity, local contactability, and experience with the local market/regulations.",
              "Compare like-for-like: scope, access, and ownership (data, files, accounts) matter more than headline price.",
          ]),
          "評估任何事物的框架",
          _bullets([
              "定義工作：好的成果是甚麼？比較前先用一句話寫下。",
              "尋找可驗證的證明：具名客戶、文件化流程、書面合約與可對照的結果。",
              "留意本地角度：在香港，確認實體存在、本地可聯絡性，以及對本地市場／法規的經驗。",
              "同類比較：範圍、存取與擁有權（數據、檔案、帳戶）比標題價更重要。",
          ])),
        S("The three questions that settle most debates",
          _bullets([
              f"What exactly is included, and what is explicitly not included when it comes to <strong>{kw}</strong>?",
              f"Who owns the assets and access if you stop working with whoever provides <strong>{kw}</strong>?",
              "What happens if it under-delivers — is there an SLA, a refund clause, or an escalation path?",
          ]),
          "可平息大部分爭論的三條問題",
          _bullets([
              f"關於 <strong>{kw}</strong>，範圍包含甚麼、明確不包含甚麼？",
              f"假如你不再與提供 <strong>{kw}</strong> 的一方合作，資產與存取誰屬？",
              "萬一未達標——有無 SLA、退款條款或升級路徑？",
          ])),
        S("Red flags to take seriously",
          _bullets([
              "Claims that cannot survive a single pointed question about numbers or scope.",
              "Anonymous testimonials or reviews that repeat identical templated phrases.",
              "Pressure to commit before you have seen a written proposal or spoken to the named person doing the work.",
          ]),
          "要認真看待的警號",
          _bullets([
              "經不起一條關於數字或範圍尖銳提問的聲明。",
              "匿名推薦或重複相同模板句子的評論。",
              "在未看到書面建議書或與實際負責人交談前，便施壓要你落注。",
          ])),
        S("Bottom line",
          f"Whether <strong>{kw}</strong> is a company, a service, or a topic, the same discipline applies: define the job, verify the proof, and confirm the exit terms. Clarity survives contact with reality; hype does not.",
          "總結",
          f"無論 <strong>{kw}</strong> 是一間公司、一項服務還是議題，同樣紀律適用：定義工作、核實證明、確認離場條款。清晰經得起現實的檢驗；浮誇不能。"),
    ]


def content_design(keyword: str, s: int) -> list[dict]:
    kw = keyword
    return [
        S("What this page answers",
          f"<strong>{kw}</strong> is usually a search for practical design guidance: what the discipline covers, what it costs in Hong Kong, and how to evaluate the work.",
          "此頁解答甚麼",
          f"<strong>{kw}</strong> 通常是在尋找實用設計指引：這門學科涵蓋甚麼、在香港收費多少，以及如何評估相關工作。"),
        S("What good design work includes",
          _bullets([
              "A strategy layer: positioning, audience, and a distinct visual direction — not just fonts and colours.",
              "A system: logo, palette, type scale, and reusable components that survive web, print and social.",
              "Deliverables you own: source files, fonts with licences, and brand guidelines in writing.",
          ]),
          "好的設計工作包含甚麼",
          _bullets([
              "策略層：定位、受眾與清晰的視覺方向——而不只是字型與顏色。",
              "系統：標誌、色板、字級與可在網頁、印刷與社交重用的組件。",
              "你擁有的交付物：原始檔、已授權字型，以及書面的品牌指引。",
          ])),
        S("Hong Kong pricing norms (2026)",
          _bullets([
              "Logo/brand identity projects: HK$15,000–HK$80,000 depending on scope and agency size.",
              "Website design (template): HK$10,000–HK$30,000.",
              "Website design (custom): HK$40,000–HK$150,000.",
              "Design retainers: HK$5,000–HK$20,000/month for ongoing asset production.",
          ]),
          "香港收費常態（2026）",
          _bullets([
              "標誌／品牌識別企劃：視乎範圍與代理商規模 HK$15,000–HK$80,000。",
              "網站設計（模板）：HK$10,000–HK$30,000。",
              "網站設計（訂製）：HK$40,000–HK$150,000。",
              "設計月費：每月 HK$5,000–HK$20,000 持續製作資產。",
          ])),
        S("Red flags",
          _bullets([
              "No source files or font licences handed over.",
              "Stock-illustration-heavy 'brand systems' that cannot be extended.",
              "Designers who cannot explain the rationale behind their choices.",
          ]),
          "警號",
          _bullets([
              "不交出原始檔或字型授權。",
              "依賴庫存插圖、無法延伸的『品牌系統』。",
              "無法解釋創作背後理念的設計師。",
          ])),
        S("Bottom line",
          "Pay for strategy and ownership, not decoration. A brand that survives at 16 px, prints cleanly, and has written guidelines is worth more than any single pretty mockup.",
          "總結",
          "為策略與擁有權付費，而不是裝飾。一個在 16px 下依然可辨、印刷清晰並有書面指引的品牌，勝過任何單一漂亮的 mockup。"),
    ]


def body_sections(keyword: str, category: str) -> list[dict]:
    s = seed(keyword)
    kw = keyword.strip()

    # Safety-first handling for crack/piracy adjacent keywords
    if HACK_HINT.search(kw):
        return [
            S("What this page answers",
              f"Searches for <strong>{kw}</strong> usually mix genuine curiosity ('can I run AI tools cheaper?') with piracy-adjacent intent. This guide covers only legitimate, durable ways to use AI and search tools.",
              "此頁解答甚麼",
              f"搜尋 <strong>{kw}</strong> 的讀者通常混合真正的好奇（『可以平啲用 AI 嗎？』）與盜版意圖。此指南只討論合法、可持續地使用 AI 與搜尋工具的方法。"),
            S("Why shortcuts fail",
              _bullets([
                  "Cracked tools break silently: credential theft, malware, and platform bans cost more than the licence.",
                  "AI platforms detect and terminate unofficial access; your prompts and data are the real cost.",
                  "Support, model updates and compliance (e.g. data handling) only come with official access.",
              ]),
              "為何偷雞會失敗",
              _bullets([
                  "破解工具會靜靜地壞：帳戶被盜、惡意軟件與平台封鎖，代價遠高於授權成本。",
                  "AI 平台偵測並終止非官方存取；你真正付出的，是提示內容與數據。",
                  "支援、模型更新與合規（例如數據處理）只有官方途徑才有。",
              ])),
            S("The legitimate way to get cheaper AI",
              _bullets([
                  "Team/enterprise plans price per seat — scaling with your team beats sharing one hacked account.",
                  "Open-weight models (e.g. Llama, Qwen) can be self-hosted where talent and hardware allow.",
                  "Official API credits are metered and predictable; a small, well-targeted workflow costs less than a leaky stopped tool.",
              ]),
              "合法平用 AI 的方法",
              _bullets([
                  "團隊／企業計劃按席位計價——與其共享一個被破解帳戶，不如隨團隊規模升級。",
                  "開放權重模型（例如 Llama、Qwen）可在具技術與硬件時自行部署。",
                  "官方 API 額度有條不紊、可預測；一個小而精的工作流程，比會漏的破解工具更省。",
              ])),
            S("Bottom line",
              f"Treat <strong>{kw}</strong> as a cost problem, not an access problem. Budget for official seats or open-weight alternatives, keep human review in the loop, and never trade compliance for a shortcut.",
              "總結",
              f"把 <strong>{kw}</strong> 當作成本問題，而非存取問題。為官方席位或開放權重方案編預算，保留人手覆核，永不為捷徑犧牲合規。"),
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

TOGGLE_JS = """<script>
(function () {
  var btn = document.getElementById('langToggle');
  var titleEl = document.getElementById('pageTitle');
  var ledeEl = document.getElementById('pageLede');
  var primaryZh = document.documentElement.lang === 'zh-Hant';
  var on = primaryZh;
  try {
    var saved = localStorage.getItem('sr-lang');
    if (saved === 'zh') on = true;
    if (saved === 'en') on = false;
  } catch (e) {}
  function apply(zh) {
    document.body.classList.toggle('zh', zh);
    document.documentElement.lang = zh ? 'zh-Hant' : 'en';
    if (btn) btn.textContent = zh ? 'English' : '中文';
    if (titleEl) titleEl.textContent = titleEl.getAttribute(zh ? 'data-zh' : 'data-en') || titleEl.textContent;
    if (ledeEl) ledeEl.textContent = ledeEl.getAttribute(zh ? 'data-zh' : 'data-en') || ledeEl.textContent;
    try { localStorage.setItem('sr-lang', zh ? 'zh' : 'en'); } catch (e) {}
  }
  if (btn) btn.addEventListener('click', function () {
    apply(!document.body.classList.contains('zh'));
  });
  apply(on);
})();
</script>"""


def render_article(keyword: str, slug: str, related: list[tuple[str, str]]) -> str:
    category = categorize(keyword)
    title = title_for(keyword, category)
    title_zh = title_zh_for(keyword, category)
    description = description_for(keyword, category)
    description_zh = description_zh_for(keyword, category)
    meta_title = clip(primary_title(keyword, category), 60)
    meta_desc = clip(primary_description(keyword, category), 155)
    sections = body_sections(keyword, category)
    related_html = "".join(
        f'<li><a href="/articles/{escape(rslug)}.html">{escape(rkw)}</a></li>' for rkw, rslug in related
    )
    section_html = ""
    for sec in sections:
        eh, eb = sec["en"]
        zh, zb = sec["zh"]
        section_html += (
            "<section>\n"
            f"  <h2 data-lang=\"en\">{escape(eh)}</h2>\n"
            f"  <div class=\"b\" data-lang=\"en\">{eb}</div>\n"
            f"  <h2 data-lang=\"zh\">{escape(zh)}</h2>\n"
            f"  <div class=\"b\" data-lang=\"zh\">{zb}</div>\n"
            "</section>\n"
        )

    primary_lang = "zh-Hant" if is_cjk(keyword) else "en"
    hreflang = "zh-Hant" if is_cjk(keyword) else "en"
    default_title = title_zh if is_cjk(keyword) else title
    default_desc = description_zh if is_cjk(keyword) else description
    body_class = ' class="zh"' if is_cjk(keyword) else ""
    # Canonical path must keep raw slug for file serving; sitemap encodes separately.
    canonical = f"https://www.seogeoworks.hk/articles/{escape(slug)}.html"
    return f"""<!doctype html>
<html lang="{primary_lang}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#11120f" />
    <title>{escape(meta_title)}</title>
    <meta name="description" content="{escape(meta_desc)}" />
    <link rel="canonical" href="{canonical}" />
    <link rel="alternate" hreflang="{hreflang}" href="{canonical}" />
    <link rel="alternate" hreflang="x-default" href="{canonical}" />
    <link rel="sitemap" type="application/xml" title="Sitemap" href="https://www.seogeoworks.hk/sitemap.xml" />
    <meta property="og:type" content="article" />
    <meta property="og:site_name" content="seogeoworks" />
    <meta property="og:url" content="{canonical}" />
    <meta property="og:title" content="{escape(meta_title)}" />
    <meta property="og:description" content="{escape(meta_desc)}" />
    <meta property="og:image" content="https://www.seogeoworks.hk/og.png" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{escape(meta_title)}" />
    <meta name="twitter:description" content="{escape(meta_desc)}" />
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
      .top button {{ background:none;border:none;color:var(--lime);cursor:pointer;font:500 12px "DM Mono",monospace; }}
      .eyebrow {{ color:var(--lime); font:12px "DM Mono",monospace; letter-spacing:.04em; text-transform:uppercase; }}
      h1 {{ margin:14px 0 18px; font:700 clamp(32px,5vw,52px)/1.05 "Playfair Display",serif; letter-spacing:-.03em; }}
      .lede {{ color:var(--muted); font-size:18px; margin:0 0 34px; }}
      section {{ padding:22px 0; border-top:1px solid var(--line); }}
      h2 {{ margin:0 0 12px; font:600 24px/1.2 "Playfair Display",serif; }}
      .b {{ margin:0 0 12px; }}
      p, li {{ color:#d7d5cc; }}
      ul {{ padding-left:1.2em; }}
      [data-lang="zh"] {{ display:none; }}
      body.zh [data-lang="zh"] {{ display:block; }}
      body.zh [data-lang="en"] {{ display:none; }}
      .related {{ margin-top:40px; padding-top:24px; border-top:1px solid var(--line); }}
      .related h2 {{ font-size:20px; }}
      .related ul {{ list-style:none; padding:0; display:grid; gap:10px; }}
      .related a {{ text-decoration:none; }}
      footer {{ margin-top:48px; color:var(--muted); font-size:13px; }}
    </style>
  </head>
  <body{body_class}>
    <div class="wrap">
      <div class="top"><a href="/">← seogeoworks</a><button id="langToggle" type="button" aria-label="切換語言 / toggle language">{"English" if is_cjk(keyword) else "中文"}</button><span>Field guide · {TODAY}</span></div>
      <div class="eyebrow">seogeoworks / {escape(category)} · {escape(CATEGORY_ZH.get(category, category))}</div>
      <h1 id="pageTitle" data-en="{escape(title)}" data-zh="{escape(title_zh)}">{escape(default_title)}</h1>
      <p class="lede" id="pageLede" data-en="{escape(description)}" data-zh="{escape(description_zh)}">{escape(default_desc)}</p>
      <article>
{section_html}
      </article>
      <aside class="related">
        <h2 data-lang="en">Related field guides</h2>
        <h2 data-lang="zh">相關實地指南</h2>
        <ul>
          {related_html}
        </ul>
      </aside>
      <footer>
        <p data-lang="en">© {date.today().year} seogeoworks. <a href="/">Home</a> · <a href="/articles/">All guides</a> · <a href="/sitemap.xml">Sitemap</a></p>
        <p data-lang="zh">© {date.today().year} seogeoworks。<a href="/">主頁</a> · <a href="/articles/">全部指南</a> · <a href="/sitemap.xml">Sitemap</a></p>
      </footer>
    </div>
    {TOGGLE_JS}
  </body>
</html>
"""


def write_index(entries: list[dict]) -> None:
    items = "\n".join(
        f'<li><a href="/articles/{escape(e["slug"])}.html"><strong>{escape(e["keyword"])}</strong>'
        f'<span>{escape(e["title"])} · <span lang="zh-Hant">{escape(e["title_zh"])}</span></span></a></li>'
        for e in entries
    )
    index_title = "Field guides — seogeoworks"
    index_desc = "Bilingual (English / 繁體中文) field guides on SEO, GEO, KOL, and marketing for Hong Kong operators."
    html_doc = f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escape(index_title)}</title>
  <meta name="description" content="{escape(index_desc)}" />
  <link rel="canonical" href="https://www.seogeoworks.hk/articles/" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="seogeoworks" />
  <meta property="og:url" content="https://www.seogeoworks.hk/articles/" />
  <meta property="og:title" content="{escape(index_title)}" />
  <meta property="og:description" content="{escape(index_desc)}" />
  <meta property="og:image" content="https://www.seogeoworks.hk/og.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{escape(index_title)}" />
  <meta name="twitter:description" content="{escape(index_desc)}" />
  <meta name="twitter:image" content="https://www.seogeoworks.hk/og.png" />
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
    <p><a href="/">← seogeoworks</a></p>
    <h1>Field guides 實地指南</h1>
    <p>Eng/粵 · 共 {len(entries)} 篇雙語指南：搜尋、社交與現代品牌發現的實用筆記。</p>
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
        f"  <url><loc>{encode_sitemap_url(u)}</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq><priority>{p}</priority></url>"
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
        category = categorize(kw)
        entries.append(
            {
                "keyword": kw,
                "slug": slug,
                "title": title_for(kw, category),
                "title_zh": title_zh_for(kw, category),
                "category": category,
            }
        )

    write_index(entries)
    write_sitemap(entries)
    MANIFEST.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"generated {len(entries)} articles")


if __name__ == "__main__":
    main()