#!/usr/bin/env python3
"""간다GO — 중랑 출장마사지·홈타이 정적 사이트 빌드 스크립트.

content/ 패키지의 페이지 정의를 읽어 정적 HTML을 생성한다.

규칙(자동 적용):
  - 본문 텍스트 2,000자 미만 페이지는 robots noindex 처리
  - sitemap.xml 에는 index 허용 페이지만 포함
  - 지역+역+테마 조합 경로는 생성 자체가 불가능한 구조
"""
import html
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from content import PAGES
from content.site import (BASE_URL, BRAND, NAV, PHONE, PHONE_DISPLAY,
                          INDEXNOW_KEY, NAVER_VERIFY, RATING_VALUE,
                          RATING_COUNT, REVIEWS)
from content import magazine

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = BASE_URL.rstrip("/")
BUILD_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")
MIN_INDEX_CHARS = 2000


def text_length(body_html: str) -> int:
    """태그를 제거한 본문 글자수(공백 포함, 연속 공백은 1자).
    공통 요금 블록은 페이지 고유 본문이 아니므로 측정에서 제외한다."""
    text = re.sub(r'<section class="pricing">.*?</section>', " ", body_html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text)


def render_nav(current_path: str) -> str:
    items = []
    for label, href, children in NAV:
        active = " is-active" if href == "/" + current_path else ""
        if children:
            sub = "".join(
                f'<li><a href="{c_href}">{c_label}</a></li>'
                for c_label, c_href in children
            )
            items.append(
                f'<li class="nav-item has-sub{active}">'
                f'<a href="{href}">{label}</a>'
                f'<ul class="sub-menu">{sub}</ul></li>'
            )
        else:
            items.append(
                f'<li class="nav-item{active}"><a href="{href}">{label}</a></li>'
            )
    return "".join(items)


def render_breadcrumb(crumbs) -> str:
    if not crumbs:
        return ""
    parts = ['<nav class="breadcrumb" aria-label="현재 위치"><ol>']
    parts.append('<li><a href="/">홈</a></li>')
    for label, href in crumbs:
        if href:
            parts.append(f'<li><a href="{href}">{label}</a></li>')
        else:
            parts.append(f"<li><span>{label}</span></li>")
    parts.append("</ol></nav>")
    return "".join(parts)


def inject_toc(body: str):
    """본문 섹션(h2)에 id를 보장하고 좌측 목차 데이터를 만든다."""
    items = []
    counter = [0]

    def repl(m):
        attrs, title = m.group(1), m.group(2)
        idm = re.search(r'id="([^"]+)"', attrs)
        if idm:
            sid = idm.group(1)
            opening = f"<section{attrs}>"
        else:
            counter[0] += 1
            sid = f"sec-{counter[0]}"
            opening = f'<section id="{sid}"{attrs}>'
        label = re.sub(r"<[^>]+>", "", title).strip()
        items.append((sid, label))
        return f"{opening}<h2>{title}</h2>"

    body = re.sub(r"<section([^>]*)>\s*<h2>(.*?)</h2>", repl, body, flags=re.S)
    return body, items


def render_toc(items) -> str:
    if len(items) < 3:
        return ""
    links = "".join(
        f'<li><a href="#{sid}">{label}</a></li>' for sid, label in items
    )
    return (
        '<aside class="page-toc"><nav aria-label="페이지 목차">'
        '<p class="toc-title">목차</p>'
        f"<ul>{links}</ul></nav></aside>"
    )


# ─────────────────────────────────────────────────────────────────────────
# 구조화 데이터(JSON-LD) — 모든 페이지에 사업자·후기·평점·이동경로·FAQ 자동 삽입.
# 페이지별로 본문에서 FAQ를 추출하고 경로에 따라 Service 노드를 더한다.
# ─────────────────────────────────────────────────────────────────────────

_FAQ_RE = re.compile(r'<div class="faq-item">\s*<h3>(.*?)</h3>\s*(.*?)\s*</div>', re.S)


def _plain(fragment: str) -> str:
    """HTML 조각에서 태그를 제거하고 엔티티를 풀어 한 줄 텍스트로 만든다."""
    text = re.sub(r"<[^>]+>", " ", fragment)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _business_node() -> dict:
    return {
        "@type": ["HealthAndBeautyBusiness", "LocalBusiness"],
        "@id": SITE + "/#business",
        "name": BRAND,
        "url": SITE + "/",
        "telephone": PHONE,
        "image": SITE + "/assets/og-image.png",
        "logo": SITE + "/assets/icon-512.png",
        "priceRange": "₩70,000~₩200,000",
        "currenciesAccepted": "KRW",
        "paymentAccepted": "현금, 계좌이체, 카드",
        "description": "서울 중랑구 전지역 방문 출장마사지·홈타이 예약 안내. "
                       "면목동·상봉동·중화동·묵동·망우동·신내동 및 주요 역세권 방문 관리.",
        "areaServed": {"@type": "AdministrativeArea", "name": "서울특별시 중랑구"},
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "중랑구",
            "addressRegion": "서울특별시",
            "addressCountry": "KR",
        },
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday",
                          "Friday", "Saturday", "Sunday"],
            "opens": "00:00", "closes": "23:59",
        }],
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": RATING_VALUE,
            "reviewCount": RATING_COUNT,
            "bestRating": "5", "worstRating": "1",
        },
        "review": [
            {
                "@type": "Review",
                "author": {"@type": "Person", "name": r["author"]},
                "datePublished": r["date"],
                "reviewRating": {
                    "@type": "Rating", "ratingValue": r["rating"],
                    "bestRating": "5", "worstRating": "1",
                },
                "reviewBody": r["body"],
            }
            for r in REVIEWS
        ],
    }


def _website_node() -> dict:
    return {
        "@type": "WebSite",
        "@id": SITE + "/#website",
        "url": SITE + "/",
        "name": BRAND,
        "inLanguage": "ko",
        "publisher": {"@id": SITE + "/#business"},
    }


def _breadcrumb_node(page: dict, canonical: str):
    crumbs = page.get("breadcrumb") or []
    items = [{"@type": "ListItem", "position": 1, "name": "홈", "item": SITE + "/"}]
    pos = 2
    for label, href in crumbs:
        url = (SITE + href) if href else canonical
        items.append({"@type": "ListItem", "position": pos, "name": label, "item": url})
        pos += 1
    if len(items) < 2:
        return None
    return {
        "@type": "BreadcrumbList",
        "@id": canonical + "#breadcrumb",
        "itemListElement": items,
    }


def _webpage_node(page: dict, canonical: str) -> dict:
    return {
        "@type": "WebPage",
        "@id": canonical + "#webpage",
        "url": canonical,
        "name": _plain(page["title"]),
        "description": _plain(page["desc"]),
        "inLanguage": "ko",
        "isPartOf": {"@id": SITE + "/#website"},
        "about": {"@id": SITE + "/#business"},
    }


def _faq_node(body: str, canonical: str):
    entries = []
    for q, a in _FAQ_RE.findall(body):
        q, a = _plain(q), _plain(a)
        if q and a:
            entries.append({
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            })
    if not entries:
        return None
    return {
        "@type": "FAQPage",
        "@id": canonical + "#faq",
        "mainEntity": entries,
    }


def _service_node(page: dict, canonical: str):
    path = page["path"]
    if path.startswith("jungnang/"):
        service_type = "출장마사지·홈타이"
    elif path.startswith("themes/"):
        service_type = _plain(page["h1"]).replace(" 안내", "")
    elif path in ("massage/", "courses/"):
        service_type = "출장마사지·홈타이"
    else:
        return None
    return {
        "@type": "Service",
        "@id": canonical + "#service",
        "serviceType": service_type,
        "name": _plain(page["h1"]),
        "provider": {"@id": SITE + "/#business"},
        "areaServed": {"@type": "AdministrativeArea", "name": "서울특별시 중랑구"},
        "url": canonical,
    }


def build_jsonld(page: dict, canonical: str) -> str:
    """페이지 메타데이터로 schema.org @graph JSON-LD 블록을 만든다."""
    graph = [_business_node(), _website_node(), _webpage_node(page, canonical)]
    for node in (_breadcrumb_node(page, canonical),
                 _faq_node(page["body"], canonical),
                 _service_node(page, canonical)):
        if node:
            graph.append(node)
    payload = {"@context": "https://schema.org", "@graph": graph}
    return ('<script type="application/ld+json">\n'
            + json.dumps(payload, ensure_ascii=False, indent=2)
            + "\n</script>\n")


# ─────────────────────────────────────────────────────────────────────────
# 관련 안내(내부링크) 모듈 — 지역·역·테마 상세 페이지 하단에 롱테일 앵커로
# 다른 지역/역/테마를 연결한다. NAV 정의에서 목록을 가져와 자동 생성한다.
# ─────────────────────────────────────────────────────────────────────────

def _nav_children(menu_label: str):
    for label, href, children in NAV:
        if label == menu_label:
            return children
    return []


_AREA_ITEMS = [(l, h) for l, h in _nav_children("지역별 안내")
               if h.endswith("-chuljangmassage/") and "-station-" not in h]
_STATION_ITEMS = [(l, h) for l, h in _nav_children("지하철역별 안내")
                  if h.endswith("-station-chuljangmassage/")]
_THEME_ITEMS = [(l, h) for l, h in _nav_children("테마별 안내")
                if h.startswith("/themes/") and h != "/themes/"]


def _related_block(heading: str, items, current: str, suffix: str, limit: int) -> str:
    picks = [(l, h) for l, h in items if h != current][:limit]
    if not picks:
        return ""
    lis = "".join(
        f'<li><a href="{h}">{l}{suffix}</a></li>' for l, h in picks
    )
    return (f'<div class="related-block"><p>{heading}</p>'
            f'<ul class="link-cloud">{lis}</ul></div>')


def related_html(page: dict) -> str:
    """지역/역/테마 상세 페이지 하단 내부링크 모듈 HTML. 해당 없으면 빈 문자열."""
    path = page["path"]
    current = "/" + path
    blocks = []
    is_area = (path.startswith("jungnang/") and path.endswith("-chuljangmassage/")
               and "-station-" not in path)
    is_station = path.endswith("-station-chuljangmassage/")
    is_theme = path.startswith("themes/") and path != "themes/"

    if is_area:
        blocks.append(_related_block("다른 동네 방문 안내", _AREA_ITEMS, current, " 출장마사지·홈타이", 5))
        blocks.append(_related_block("가까운 지하철역 안내", _STATION_ITEMS, current, " 마사지", 6))
        blocks.append(_related_block("인기 관리 테마", _THEME_ITEMS, current, "", 7))
    elif is_station:
        blocks.append(_related_block("다른 역세권 안내", _STATION_ITEMS, current, " 마사지", 6))
        blocks.append(_related_block("중랑구 지역별 안내", _AREA_ITEMS, current, " 출장마사지·홈타이", 6))
        blocks.append(_related_block("인기 관리 테마", _THEME_ITEMS, current, "", 7))
    elif is_theme:
        blocks.append(_related_block("다른 관리 테마", _THEME_ITEMS, current, "", 8))
        blocks.append(_related_block("지역별 방문 안내", _AREA_ITEMS, current, " 출장마사지·홈타이", 6))
        blocks.append(_related_block("지하철역별 안내", _STATION_ITEMS, current, " 마사지", 6))
    else:
        return ""

    body = "".join(b for b in blocks if b)
    if not body:
        return ""
    return ('<section class="related-links" aria-label="관련 안내">'
            '<h2>중랑 방문 관리 관련 안내</h2>' + body + '</section>')


def render_page(page: dict) -> str:
    path = page["path"]
    title = page["title"]
    desc = page["desc"]
    h1 = page["h1"]
    body = page["body"]
    crumbs = page.get("breadcrumb") or []
    extra_head = page.get("extra_head", "")
    hero = page.get("hero", "")

    chars = text_length(body)
    noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
    robots = (
        '<meta name="robots" content="noindex,follow">'
        if noindex
        else '<meta name="robots" content="index,follow">'
    )
    canonical = BASE_URL.rstrip("/") + "/" + path
    naver_meta = f'<meta name="naver-site-verification" content="{NAVER_VERIFY}" />\n'
    schema_jsonld = build_jsonld(page, canonical)

    # 히어로가 있는 페이지(메인)는 H1을 히어로 안에서 출력한다.
    if hero:
        page_head = hero
    else:
        page_head = ""

    h1_html = "" if hero else f"<h1>{h1}</h1>"

    body, toc_items = inject_toc(body)
    toc_html = render_toc(toc_items)
    layout_cls = "page-layout has-toc" if toc_html else "page-layout"
    body += related_html(page)  # 지역/역/테마 페이지 하단 내부링크 모듈

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:image" content="{BASE_URL.rstrip('/')}/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE_URL.rstrip('/')}/assets/og-image.png">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta name="theme-color" content="#0a1120">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@600;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
<link rel="alternate" type="application/rss+xml" title="{BRAND} 매거진" href="/rss.xml">
{naver_meta}{schema_jsonld}{extra_head}</head>
<body>
<header class="site-header">
  <div class="header-accent" aria-hidden="true"></div>
  <div class="header-top">
    <div class="header-inner">
      <a class="brand" href="/"><span class="brand-mark">G</span> <span class="brand-text">{BRAND}</span></a>
      <p class="header-tagline"><span class="tag-gem">◆</span> 중랑구 전지역 방문 관리 <span class="tag-gem">◆</span> 24시간 상담</p>
      <a class="header-call" href="tel:{PHONE}"><span class="call-label">예약전화</span> {PHONE_DISPLAY}</a>
      <button class="nav-toggle" aria-label="메뉴 열기" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </div>
  <nav class="main-nav" aria-label="주 메뉴">
    <div class="nav-inner"><ul class="nav-list">{render_nav(path)}</ul></div>
  </nav>
</header>
{page_head}<main class="site-main">
  <div class="container {layout_cls}">
    {toc_html}
    <article class="page-content">
      {render_breadcrumb(crumbs)}
      {h1_html}
      {body}
    </article>
  </div>
</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <div class="footer-col footer-about">
      <p class="footer-brand">{BRAND}</p>
      <p class="footer-desc">중랑구 전지역 방문 출장마사지·홈타이 안내 사이트입니다. 모든 서비스는 안내된 관리 범위와 위생·안전 기준 안에서만 제공됩니다.</p>
      <address class="footer-contact">
        <span class="footer-contact-row"><span class="footer-label">예약전화</span> <a href="tel:{PHONE}">{PHONE_DISPLAY}</a></span>
        <span class="footer-contact-row"><span class="footer-label">상담시간</span> 연중무휴 24시간</span>
        <span class="footer-contact-row"><span class="footer-label">서비스 지역</span> 서울특별시 중랑구 전지역</span>
      </address>
    </div>
    <nav class="footer-col" aria-label="서비스 안내">
      <p class="footer-title">서비스</p>
      <ul>
        <li><a href="/massage/">중랑 출장마사지</a></li>
        <li><a href="/jungnang/">지역별 안내</a></li>
        <li><a href="/jungnang/stations/">지하철역별 안내</a></li>
        <li><a href="/themes/">테마별 안내</a></li>
        <li><a href="/courses/">코스안내</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="이용 안내">
      <p class="footer-title">이용 안내</p>
      <ul>
        <li><a href="/reservation/">예약안내</a></li>
        <li><a href="/guide/">이용가이드</a></li>
        <li><a href="/reviews/">이용 후기</a></li>
        <li><a href="/support/">고객센터</a></li>
        <li><a href="/support/#faq">자주 묻는 질문</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="정책 및 기준">
      <p class="footer-title">정책</p>
      <ul>
        <li><a href="/about/">운영자 소개</a></li>
        <li><a href="/support/privacy/">개인정보처리방침</a></li>
        <li><a href="/support/terms/">이용약관</a></li>
        <li><a href="/guide/#hygiene">위생·안전 기준</a></li>
        <li><a href="/guide/#prohibited">금지행위 안내</a></li>
        <li><a href="/support/#biz">제휴·기업 문의</a></li>
      </ul>
    </nav>
  </div>
  <div class="footer-bottom">
    <div class="container footer-bottom-inner">
      <p class="footer-copy">&copy; {BRAND}. All rights reserved.</p>
      <p class="footer-note">건전한 방문 관리 서비스를 운영하며, 불법적인 요청은 어떤 경우에도 응하지 않습니다.</p>
      <a class="footer-made" href="https://t.me/googleseolab" target="_blank" rel="noopener nofollow">웹사이트 제작문의 ↗</a>
    </div>
  </div>
</footer>
<a class="call-fab" href="tel:{PHONE}" aria-label="전화 예약 {PHONE_DISPLAY}">
  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
  <span class="call-fab-label">예약 전화</span>
</a>
<script src="/assets/nav.js"></script>
</body>
</html>
"""


def _rfc822(date_str: str) -> str:
    """'YYYY-MM-DD' → RFC-822 (KST). RSS pubDate 형식."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        dt = datetime.now()
    return dt.strftime("%a, %d %b %Y 09:00:00 +0900")


def _sitemap_meta(path: str):
    """경로별 changefreq·priority. 색인 우선순위를 검색엔진에 힌트로 전달한다."""
    if path == "":
        return "daily", "1.0"
    if path in ("jungnang/", "jungnang/stations/", "themes/", "magazine/", "reviews/"):
        return "weekly", "0.9"
    if path.startswith("jungnang/") or path.startswith("themes/"):
        return "weekly", "0.8"
    if path.startswith("magazine/"):
        return "weekly", "0.7"
    return "monthly", "0.6"


def write_sitemap(entries) -> None:
    """entries: [(loc, lastmod, changefreq, priority), ...]"""
    urls = "\n".join(
        f"  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod>"
        f"<changefreq>{cf}</changefreq><priority>{pr}</priority></url>"
        for loc, lastmod, cf, pr in entries
    )
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}\n</urlset>\n"
        )


def write_rss() -> None:
    """매거진 아티클로 RSS 2.0 피드(rss.xml)를 생성한다."""
    posts = [p for p in magazine.PAGES if p.get("date")]
    posts.sort(key=lambda p: p["date"], reverse=True)
    last_build = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = []
    for p in posts:
        link = f"{SITE}/{p['path']}"
        items.append(
            "    <item>\n"
            f"      <title>{html.escape(p['title'])}</title>\n"
            f"      <link>{link}</link>\n"
            f"      <guid isPermaLink=\"true\">{link}</guid>\n"
            f"      <pubDate>{_rfc822(p['date'])}</pubDate>\n"
            f"      <description>{html.escape(p['desc'])}</description>\n"
            "    </item>"
        )
    items_xml = "\n".join(items)
    with open(os.path.join(ROOT, "rss.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
            "  <channel>\n"
            f"    <title>{html.escape(BRAND)} 매거진</title>\n"
            f"    <link>{SITE}/magazine/</link>\n"
            f'    <atom:link href="{SITE}/rss.xml" rel="self" type="application/rss+xml"/>\n'
            "    <description>중랑 출장마사지·홈타이 — 마사지·휴식·컨디션 관리 가이드</description>\n"
            "    <language>ko</language>\n"
            f"    <lastBuildDate>{last_build}</lastBuildDate>\n"
            f"{items_xml}\n"
            "  </channel>\n</rss>\n"
        )


def build() -> None:
    report = []
    sitemap_entries = []
    article_dates = {p["path"]: p.get("date") for p in magazine.PAGES}

    for page in PAGES:
        path = page["path"]  # "" 또는 "jungnang/myeonmok-chuljangmassage/" 형태
        out_dir = os.path.join(ROOT, path)
        os.makedirs(out_dir, exist_ok=True)
        html_out = render_page(page)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_out)

        chars = text_length(page["body"])
        noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
        if not noindex:
            lastmod = article_dates.get(path) or BUILD_DATE
            cf, pr = _sitemap_meta(path)
            sitemap_entries.append((SITE + "/" + path, lastmod, cf, pr))
        report.append((path or "/", chars, "noindex" if noindex else "index"))

    write_sitemap(sitemap_entries)
    write_rss()

    # robots.txt — 모든 봇 허용 + 주요 색인 봇 명시 + 사이트맵 위치 고지.
    # 네이버 Yeti·구글봇·빙봇을 명시해 색인 우선 크롤링을 유도한다.
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(
            "User-agent: Yeti\nAllow: /\n\n"          # 네이버
            "User-agent: Googlebot\nAllow: /\n\n"     # 구글
            "User-agent: Googlebot-Image\nAllow: /\n\n"
            "User-agent: bingbot\nAllow: /\n\n"       # 빙
            "User-agent: Daumoa\nAllow: /\n\n"        # 다음
            "User-agent: *\nAllow: /\n\n"
            f"Sitemap: {SITE}/sitemap.xml\n"
        )

    # IndexNow 키 파일 — 빙·네이버·얀덱스 즉시 색인 통보용 (루트에 {key}.txt)
    with open(os.path.join(ROOT, f"{INDEXNOW_KEY}.txt"), "w", encoding="utf-8") as f:
        f.write(INDEXNOW_KEY + "\n")

    # .nojekyll (GitHub Pages)
    open(os.path.join(ROOT, ".nojekyll"), "w").close()

    width = max(len(p) for p, _, _ in report)
    print(f"{'PATH'.ljust(width)}  CHARS  ROBOTS")
    for p, c, r in sorted(report):
        flag = "" if (r == "noindex" or MIN_INDEX_CHARS <= c <= 2500) else "  ⚠"
        print(f"{p.ljust(width)}  {str(c).rjust(5)}  {r}{flag}")
    rss_n = len([p for p in magazine.PAGES if p.get("date")])
    print(f"\n{len(report)} pages built, {len(sitemap_entries)} in sitemap, "
          f"{rss_n} in rss.xml.")
    print(f"IndexNow key file: /{INDEXNOW_KEY}.txt")


if __name__ == "__main__":
    build()
