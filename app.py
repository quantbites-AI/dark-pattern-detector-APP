import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import Optional
import json

st.set_page_config(
    page_title="DarkScan — Dark Pattern Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0a0c0f;
    color: #c8d0db;
}

.stApp {
    background-color: #0a0c0f;
}

/* Hide streamlit default elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem; max-width: 1100px; }

/* ── Hero header ── */
.hero {
    border-bottom: 1px solid #1e2530;
    padding: 2.5rem 0 2rem;
    margin-bottom: 2rem;
}
.hero-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.2em;
    color: #e05a2b;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.hero-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.8rem;
    font-weight: 600;
    color: #f0f4f8;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 0.5rem;
}
.hero-title span { color: #e05a2b; }
.hero-sub {
    font-size: 14px;
    color: #6b7a8d;
    max-width: 520px;
    line-height: 1.6;
    margin-top: 0.75rem;
}

/* ── Input area ── */
.stTextInput > div > div > input {
    background: #0f1318 !important;
    border: 1px solid #1e2530 !important;
    border-radius: 4px !important;
    color: #c8d0db !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 14px !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: #e05a2b !important;
    box-shadow: 0 0 0 2px rgba(224,90,43,0.12) !important;
}
.stTextInput > div > div > input::placeholder { color: #3a4455 !important; }

.stButton > button {
    background: #e05a2b !important;
    color: #fff !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    padding: 0.65rem 2rem !important;
    transition: background 0.2s, transform 0.1s !important;
    text-transform: uppercase !important;
}
.stButton > button:hover { background: #c44d23 !important; }
.stButton > button:active { transform: scale(0.98) !important; }

/* ── Score display ── */
.score-ring {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    background: #0f1318;
    border: 1px solid #1e2530;
    border-radius: 8px;
    padding: 1.5rem 2rem;
    margin: 1.5rem 0;
}
.score-number {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 4rem;
    font-weight: 600;
    line-height: 1;
}
.score-meta { flex: 1; }
.score-label {
    font-size: 11px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #6b7a8d;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 4px;
}
.score-verdict {
    font-size: 1.3rem;
    font-weight: 500;
    color: #f0f4f8;
}
.score-summary { font-size: 13px; color: #6b7a8d; margin-top: 4px; line-height: 1.5; }

.severity-bar {
    height: 4px;
    border-radius: 2px;
    background: #1e2530;
    margin-top: 10px;
    overflow: hidden;
}
.severity-fill { height: 100%; border-radius: 2px; transition: width 1s ease; }

/* ── Finding cards ── */
.finding-card {
    background: #0f1318;
    border: 1px solid #1e2530;
    border-left: 3px solid;
    border-radius: 0 6px 6px 0;
    padding: 1.1rem 1.25rem;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.finding-card:hover { background: #111620; }
.finding-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.finding-name {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    font-weight: 600;
    color: #f0f4f8;
}
.finding-category {
    font-size: 11px;
    color: #6b7a8d;
    margin-bottom: 5px;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.finding-desc { font-size: 13px; color: #8a9ab0; line-height: 1.6; }
.finding-evidence {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    background: #0a0c0f;
    border: 1px solid #1e2530;
    border-radius: 4px;
    padding: 6px 10px;
    margin-top: 8px;
    color: #e05a2b;
    word-break: break-all;
}
.badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 9px;
    border-radius: 3px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge-critical { background: rgba(220,53,53,0.15); color: #f07070; border: 1px solid rgba(220,53,53,0.25); }
.badge-high     { background: rgba(224,90,43,0.15); color: #e08060; border: 1px solid rgba(224,90,43,0.25); }
.badge-medium   { background: rgba(200,150,30,0.15); color: #d4aa50; border: 1px solid rgba(200,150,30,0.25); }
.badge-low      { background: rgba(80,140,180,0.15); color: #70a8cc; border: 1px solid rgba(80,140,180,0.25); }

/* ── Section headers ── */
.section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #3a4455;
    border-bottom: 1px solid #1e2530;
    padding-bottom: 0.5rem;
    margin: 1.5rem 0 1rem;
}

/* ── Stats row ── */
.stats-row {
    display: flex;
    gap: 12px;
    margin: 1rem 0;
}
.stat-box {
    flex: 1;
    background: #0f1318;
    border: 1px solid #1e2530;
    border-radius: 6px;
    padding: 0.9rem 1rem;
    text-align: center;
}
.stat-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    line-height: 1;
}
.stat-label { font-size: 11px; color: #6b7a8d; margin-top: 4px; letter-spacing: 0.08em; text-transform: uppercase; }

/* ── URL display ── */
.url-chip {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    background: #0f1318;
    border: 1px solid #1e2530;
    border-radius: 4px;
    padding: 6px 12px;
    color: #6b7a8d;
    display: inline-block;
    margin-bottom: 1rem;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Progress bar */
.stProgress > div > div > div > div {
    background: #e05a2b !important;
}

/* Clean category tabs */
.stSelectbox select {
    background: #0f1318 !important;
    border: 1px solid #1e2530 !important;
    color: #c8d0db !important;
    font-family: 'IBM Plex Mono', monospace !important;
}

.clean-divider {
    border: none;
    border-top: 1px solid #1e2530;
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)


# ── Dark Pattern Definitions ──────────────────────────────────────────────
@dataclass
class Finding:
    name: str
    category: str
    severity: str  # critical, high, medium, low
    description: str
    evidence: str
    recommendation: str


SEVERITY_COLOR = {
    "critical": "#dc3535",
    "high":     "#e05a2b",
    "medium":   "#c89620",
    "low":      "#3e8ab0",
}

SEVERITY_SCORE = {"critical": 30, "high": 20, "medium": 10, "low": 5}


def fetch_page(url: str) -> tuple[Optional[BeautifulSoup], Optional[str], int]:
    """Fetch page and return (soup, raw_text, status_code)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    try:
        r = requests.get(url, headers=headers, timeout=12, allow_redirects=True)
        soup = BeautifulSoup(r.text, "lxml")
        return soup, r.text, r.status_code
    except Exception as e:
        return None, None, 0


def check_fake_urgency(soup: BeautifulSoup, text: str) -> list[Finding]:
    findings = []
    urgency_patterns = [
        (r'\b(\d+)\s*(items?|people|visitors?|others?)\s*(are\s+)?(viewing|looking at|watching)\s+this', "Social proof urgency"),
        (r'only\s+(\d+)\s+(left|remaining|in stock)', "False scarcity"),
        (r'(sale|offer|deal)\s+(ends?|expires?|in)\s+(\d+|today|tonight|soon)', "Artificial deadline"),
        (r'limited\s+time\s+(offer|only|deal)', "Limited time pressure"),
        (r'(\d+)\s+(sold|bought|ordered)\s+(today|recently|in the last)', "Social urgency"),
        (r'hurry[!,.]|act\s+now|don\'t\s+(miss|wait)|last\s+chance', "Urgency language"),
        (r'(price|offer)\s+expires?\s+in', "Countdown pressure"),
    ]
    full_text = soup.get_text(" ", strip=True).lower()
    found = []
    for pattern, name in urgency_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            snippet = re.search(pattern, full_text, re.IGNORECASE)
            evidence = full_text[max(0, snippet.start()-20):snippet.end()+30].strip() if snippet else str(matches[0])
            if name not in found:
                found.append(name)
                findings.append(Finding(
                    name=name,
                    category="Fake Urgency / Scarcity",
                    severity="high",
                    description="Creates artificial time or quantity pressure to rush users into decisions before they can think critically.",
                    evidence=f'"{evidence[:120]}..."',
                    recommendation="Check if the countdown/scarcity resets on page reload. Real scarcity doesn't need manipulation language."
                ))
    return findings


def check_hidden_costs(soup: BeautifulSoup, text: str) -> list[Finding]:
    findings = []
    full_text = soup.get_text(" ", strip=True).lower()

    # Hidden fees patterns
    fee_patterns = [
        (r'(service|booking|processing|handling|convenience)\s+fee', "Hidden service fee"),
        (r'taxes?\s+(and\s+fees?\s+)?not\s+included', "Taxes hidden until checkout"),
        (r'(resort|destination|facility)\s+fee', "Hidden resort/facility fee"),
        (r'(shipping|delivery)\s+calculated\s+at\s+checkout', "Hidden shipping cost"),
    ]
    for pattern, name in fee_patterns:
        if re.search(pattern, full_text, re.IGNORECASE):
            match = re.search(pattern, full_text, re.IGNORECASE)
            snippet = full_text[max(0, match.start()-15):match.end()+40].strip()
            findings.append(Finding(
                name=name,
                category="Hidden Costs",
                severity="high",
                description="Fees are concealed during browsing and revealed only at checkout, after significant user investment.",
                evidence=f'"{snippet[:120]}"',
                recommendation="Disclose all fees upfront on product/service pages before checkout."
            ))
            break

    # Fine print buried pricing
    small_tags = soup.find_all(['small', 'sup', 'sub'])
    for tag in small_tags:
        t = tag.get_text(strip=True).lower()
        if re.search(r'\$|€|£|fee|charge|extra|additional', t):
            findings.append(Finding(
                name="Buried pricing in fine print",
                category="Hidden Costs",
                severity="medium",
                description="Pricing details are hidden in visually de-emphasized small text, making them easy to miss.",
                evidence=f'Small/fine print: "{tag.get_text(strip=True)[:100]}"',
                recommendation="Show all pricing in same font size as surrounding content."
            ))
            break

    return findings


def check_confirm_shaming(soup: BeautifulSoup, text: str) -> list[Finding]:
    findings = []
    full_text = soup.get_text(" ", strip=True)

    shame_patterns = [
        r"no\s+thanks[,.]?\s+I\s+(don'?t|hate|prefer not)",
        r"no[,.]?\s+I\s+(don'?t want|hate|refuse|prefer not to)\s+(save|get|have|be|enjoy)",
        r"I\s+(don'?t|hate|prefer not to)\s+(want|care about|need)\s+(saving|deals|discount|offer)",
        r"decline\s+and\s+(stay|remain|keep)\s+(vulnerable|ignorant|broke|poor)",
        r"no\s+thanks[,.]?\s+I\s+(like|love|enjoy)\s+paying\s+(full|more|extra)",
    ]
    for pattern in shame_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            findings.append(Finding(
                name="Confirm-shaming opt-out",
                category="Emotional Manipulation",
                severity="high",
                description="The 'No' option is written to shame or guilt-trip users, making declining feel like a negative character judgment.",
                evidence=f'"{match.group(0)[:120]}"',
                recommendation="Use neutral language for all options, e.g. 'No thanks' instead of 'No thanks, I hate saving money.'"
            ))
            break

    return findings


def check_pre_ticked_boxes(soup: BeautifulSoup, text: str) -> list[Finding]:
    findings = []

    # Find all checked checkboxes
    checked_boxes = soup.find_all('input', {'type': 'checkbox', 'checked': True})
    checked_boxes += soup.find_all('input', {'type': 'checkbox', 'checked': ''})

    marketing_keywords = ['newsletter', 'offer', 'promo', 'marketing', 'email', 'sms', 'text message',
                          'partner', 'third party', 'contact', 'update', 'deal', 'subscribe']

    for box in checked_boxes:
        # Look at surrounding label text
        label_text = ""
        box_id = box.get('id', '')
        name_attr = box.get('name', '').lower()
        if box_id:
            label = soup.find('label', {'for': box_id})
            if label:
                label_text = label.get_text(strip=True).lower()
        if not label_text:
            parent = box.parent
            if parent:
                label_text = parent.get_text(strip=True).lower()

        combined = label_text + " " + name_attr
        if any(kw in combined for kw in marketing_keywords):
            findings.append(Finding(
                name="Pre-ticked marketing consent box",
                category="Forced Consent",
                severity="critical",
                description="A marketing/communication opt-in checkbox is checked by default, collecting consent without active user choice. This violates GDPR Article 7.",
                evidence=f'Pre-checked input: name="{box.get("name","")}", label="{label_text[:80]}"',
                recommendation="All opt-in checkboxes must be unchecked by default. Consent must be freely given and unambiguous."
            ))

    # Also check for visual checkbox patterns in page text
    full_text = soup.get_text(" ", strip=True).lower()
    if not findings:
        if re.search(r'(yes[,!]?\s+)?(sign\s+me\s+up|i\s+want|keep\s+me|send\s+me).*(newsletter|offers?|updates?|deals?)', full_text, re.IGNORECASE):
            # Check if this seems to be a default opt-in
            if re.search(r'(default|automatically|already)\s+(subscribed|opted|enrolled)', full_text, re.IGNORECASE):
                findings.append(Finding(
                    name="Automatic newsletter enrollment",
                    category="Forced Consent",
                    severity="high",
                    description="Users are automatically enrolled in marketing communications without explicit action.",
                    evidence="Page indicates automatic opt-in to newsletter/marketing",
                    recommendation="Require explicit opt-in action; never auto-subscribe users."
                ))

    return findings


def check_misdirection(soup: BeautifulSoup, text: str) -> list[Finding]:
    findings = []

    # Look for visually de-emphasized cancel/decline buttons
    all_buttons = soup.find_all(['button', 'a', 'input'])
    cancel_patterns = r'(cancel|no thanks|skip|decline|close|dismiss|not now|maybe later)'
    accept_patterns = r'(yes|agree|accept|continue|subscribe|sign up|get started|buy|add to cart|checkout)'

    cancel_btns = [b for b in all_buttons if re.search(cancel_patterns, b.get_text(strip=True), re.IGNORECASE)
                   or re.search(cancel_patterns, b.get('value', ''), re.IGNORECASE)]
    accept_btns = [b for b in all_buttons if re.search(accept_patterns, b.get_text(strip=True), re.IGNORECASE)
                   or re.search(accept_patterns, b.get('value', ''), re.IGNORECASE)]

    # Check if cancel button has visually-hidden/small classes
    for btn in cancel_btns:
        classes = ' '.join(btn.get('class', [])).lower()
        style = btn.get('style', '').lower()
        if any(kw in classes for kw in ['small', 'minor', 'secondary', 'ghost', 'link', 'text-', 'muted']):
            findings.append(Finding(
                name="Visually de-emphasized cancel/decline option",
                category="Misdirection",
                severity="medium",
                description="The cancel or decline option is styled as a minor link vs a prominent accept button, making the desired-by-designer action visually dominant.",
                evidence=f'Cancel button classes: "{classes[:80]}", text: "{btn.get_text(strip=True)[:60]}"',
                recommendation="Give cancel and accept options equal visual weight. Users should make a clear choice, not be nudged."
            ))
            break

    # Misleading ad-like content
    sponsored_near_organic = soup.find_all(text=re.compile(r'(sponsored|advertisement|promoted)', re.IGNORECASE))
    if sponsored_near_organic and len(sponsored_near_organic) > 2:
        findings.append(Finding(
            name="Ads disguised as organic content",
            category="Misdirection",
            severity="medium",
            description="Sponsored/advertisement content appears inline with organic content without clear visual distinction.",
            evidence=f"Found {len(sponsored_near_organic)} 'sponsored/advertisement' labels — check if visually distinct from organic results.",
            recommendation="Ads must have clear visual separation (background color, border, explicit 'Ad' label) from organic content."
        ))

    return findings


def check_roach_motel(soup: BeautifulSoup, text: str) -> list[Finding]:
    findings = []
    full_text = soup.get_text(" ", strip=True).lower()

    roach_patterns = [
        (r'(cancel|unsubscribe|delete account).*(call|phone|contact us|email us|write to)', "Cancellation requires phone call"),
        (r'(to cancel|to unsubscribe).*(send (a )?(letter|mail|written))', "Cancellation requires written letter"),
        (r'cancel(lation)?\s+(is|can be)\s+(done|processed|completed)\s+(by|via|through)\s+(calling|phoning|contacting)', "Cancel-by-phone-only"),
        (r'(free trial|subscription).{0,50}cancel.{0,80}(before|prior to).{0,50}(renew|charge|bill)', "Renewal trap with buried cancel instructions"),
    ]

    for pattern, name in roach_patterns:
        if re.search(pattern, full_text, re.IGNORECASE):
            match = re.search(pattern, full_text, re.IGNORECASE)
            snippet = full_text[max(0, match.start()-10):match.end()+50].strip()
            findings.append(Finding(
                name=name,
                category="Roach Motel",
                severity="critical",
                description="Easy to sign up, deliberately hard to cancel. Creating friction in the exit process to retain unwilling users.",
                evidence=f'"{snippet[:120]}"',
                recommendation="The cancellation process must be as easy as the sign-up process — one-click cancellation should be the standard."
            ))

    return findings


def check_privacy_zuckering(soup: BeautifulSoup, text: str) -> list[Finding]:
    findings = []
    full_text = soup.get_text(" ", strip=True).lower()

    # Vague data sharing language
    vague_patterns = [
        (r'(share|sell|transfer|provide).{0,40}(partners?|third part(y|ies)|affiliates?|select companies)', "Data shared with vague 'partners'"),
        (r'(trusted|carefully selected|vetted)\s+(partners?|third part)', "Data sold to 'trusted partners'"),
        (r'(improve|enhance|personalize).{0,40}(experience|service).{0,40}(partner|third)', "Disguised data sale as 'improvement'"),
    ]
    for pattern, name in vague_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            snippet = full_text[max(0, match.start()-10):match.end()+60].strip()
            findings.append(Finding(
                name=name,
                category="Privacy Zuckering",
                severity="high",
                description="Vague language obscures that user data is being sold or shared with third parties for commercial purposes.",
                evidence=f'"{snippet[:120]}"',
                recommendation="Explicitly state which companies receive data, for what purpose, and provide a clear opt-out mechanism."
            ))
            break

    # Over-broad permissions in cookie banners
    cookie_banner = soup.find(id=re.compile(r'cookie|consent|gdpr|privacy', re.IGNORECASE))
    if not cookie_banner:
        cookie_banner = soup.find(class_=re.compile(r'cookie|consent|gdpr|privacy|banner', re.IGNORECASE))

    if cookie_banner:
        banner_text = cookie_banner.get_text(strip=True).lower()
        if re.search(r'accept all|allow all|i agree', banner_text, re.IGNORECASE):
            # Check if there's a clear decline option
            decline_btn = cookie_banner.find(text=re.compile(r'(decline|reject|necessary only|manage|customize)', re.IGNORECASE))
            if not decline_btn:
                findings.append(Finding(
                    name="Cookie banner without clear decline option",
                    category="Privacy Zuckering",
                    severity="high",
                    description="Cookie consent banner has a prominent 'Accept All' but no equally visible option to decline or manage cookies.",
                    evidence="Cookie banner detected with Accept All but no visible Decline/Reject option",
                    recommendation="'Accept All' and 'Reject All' must be equally visible and prominent per GDPR requirements."
                ))

    return findings


def check_disguised_ads(soup: BeautifulSoup, text: str) -> list[Finding]:
    findings = []

    # Look for fake download buttons
    download_links = soup.find_all(['a', 'button'], text=re.compile(r'download|get\s+it\s+free|free\s+download', re.IGNORECASE))
    for link in download_links:
        href = link.get('href', '') if link.name == 'a' else ''
        classes = ' '.join(link.get('class', [])).lower()
        if 'ad' in classes or 'sponsor' in classes or 'banner' in classes:
            findings.append(Finding(
                name="Fake download button (ad)",
                category="Disguised Ads",
                severity="high",
                description="A button styled as 'Download' is actually an advertisement, designed to mislead users into clicking ads.",
                evidence=f'"{link.get_text(strip=True)[:60]}" → {href[:60]}',
                recommendation="Clearly label all advertisements. Never use action-intent language ('Download', 'Play') for ad units."
            ))
            break

    # Advertorials
    advertorial_markers = soup.find_all(text=re.compile(r'(partner content|presented by|sponsored content|paid post|brought to you by)', re.IGNORECASE))
    if advertorial_markers:
        parent_classes = []
        for m in advertorial_markers:
            parent = m.parent
            if parent:
                parent_classes.append(' '.join(parent.get('class', [])))
        findings.append(Finding(
            name="Advertorial / sponsored content",
            category="Disguised Ads",
            severity="low",
            description="Commercial content is presented in a format identical to editorial content with only small 'sponsored' labels.",
            evidence=f"Found labels: {[m[:40] for m in advertorial_markers[:3]]}",
            recommendation="Sponsored content must have a persistent, visually distinct header — not just a small inline label."
        ))

    return findings


def check_trick_questions(soup: BeautifulSoup, text: str) -> list[Finding]:
    findings = []

    # Double negatives in forms
    form_texts = []
    for form_elem in soup.find_all(['label', 'span', 'p']):
        t = form_elem.get_text(strip=True)
        if re.search(r"(uncheck|untick|deselect|opt.out).{0,60}(not|no).{0,60}(receive|want|like)", t, re.IGNORECASE):
            form_texts.append(t[:120])
        if re.search(r"(do\s+not|don't|uncheck)\s+.{0,30}if\s+you\s+(do\s+not|don't)\s+want", t, re.IGNORECASE):
            form_texts.append(t[:120])

    if form_texts:
        findings.append(Finding(
            name="Double-negative opt-out language",
            category="Trick Questions",
            severity="high",
            description="Deliberately confusing double-negative phrasing makes it hard to understand what action will result in what outcome.",
            evidence=f'"{form_texts[0]}"',
            recommendation="Use simple, direct language: 'Send me emails: Yes / No' instead of double negatives."
        ))

    return findings


def run_all_checks(soup: BeautifulSoup, text: str) -> list[Finding]:
    all_findings = []
    checks = [
        check_fake_urgency,
        check_hidden_costs,
        check_confirm_shaming,
        check_pre_ticked_boxes,
        check_misdirection,
        check_roach_motel,
        check_privacy_zuckering,
        check_disguised_ads,
        check_trick_questions,
    ]
    for check in checks:
        try:
            all_findings.extend(check(soup, text))
        except Exception:
            pass
    return all_findings


def compute_score(findings: list[Finding]) -> int:
    raw = sum(SEVERITY_SCORE[f.severity] for f in findings)
    return min(100, raw)


def verdict(score: int) -> tuple[str, str]:
    if score == 0:
        return "Clean", "#5ab070"
    elif score < 20:
        return "Mildly Suspicious", "#70a8cc"
    elif score < 40:
        return "Moderately Manipulative", "#c89620"
    elif score < 60:
        return "Highly Manipulative", "#e05a2b"
    else:
        return "Extremely Predatory", "#dc3535"


def get_score_color(score: int) -> str:
    if score == 0: return "#5ab070"
    elif score < 20: return "#70a8cc"
    elif score < 40: return "#c89620"
    elif score < 60: return "#e05a2b"
    else: return "#dc3535"


# ── UI ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
  <div class="hero-label">Consumer Protection Tool</div>
  <div class="hero-title">Dark<span>Scan</span></div>
  <div class="hero-sub">Paste any URL. We scrape the page and flag every manipulative UI pattern — fake urgency, hidden costs, pre-ticked boxes, confirm-shaming, and more.</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])
with col1:
    url_input = st.text_input(
        label="url",
        label_visibility="collapsed",
        placeholder="https://example.com  —  paste any website URL",
        key="url_field"
    )
with col2:
    scan_btn = st.button("SCAN →", use_container_width=True)

# Quick example links
st.markdown("""
<div style="font-size: 12px; color: #3a4455; margin-top: -4px; font-family: 'IBM Plex Mono', monospace;">
Try: amazon.com &nbsp;·&nbsp; booking.com &nbsp;·&nbsp; any e-commerce checkout page
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="clean-divider">', unsafe_allow_html=True)

if scan_btn and url_input:
    # Normalize URL
    if not url_input.startswith(('http://', 'https://')):
        url_input = 'https://' + url_input

    parsed = urlparse(url_input)
    domain = parsed.netloc.replace('www.', '')

    st.markdown(f'<div class="url-chip">Scanning: {url_input[:90]}</div>', unsafe_allow_html=True)

    progress = st.progress(0, text="Fetching page...")
    time.sleep(0.3)

    soup, raw_text, status = fetch_page(url_input)

    if not soup or status == 0:
        st.error(f"Could not reach the URL. Check the address and try again.")
        st.stop()

    progress.progress(30, text="Analysing HTML structure...")
    time.sleep(0.2)

    progress.progress(60, text="Running dark pattern checks...")
    findings = run_all_checks(soup, raw_text or "")
    time.sleep(0.2)

    progress.progress(90, text="Computing severity scores...")
    time.sleep(0.2)

    score = compute_score(findings)
    verdict_text, verdict_color = verdict(score)
    score_color = get_score_color(score)

    progress.progress(100, text="Done.")
    time.sleep(0.3)
    progress.empty()

    # ── Score display ──
    critical_count = sum(1 for f in findings if f.severity == "critical")
    high_count     = sum(1 for f in findings if f.severity == "high")
    medium_count   = sum(1 for f in findings if f.severity == "medium")
    low_count      = sum(1 for f in findings if f.severity == "low")

    categories = list(set(f.category for f in findings))

    st.markdown(f"""
    <div class="score-ring">
      <div>
        <div class="score-label">manipulation score</div>
        <div class="score-number" style="color:{score_color}">{score}</div>
        <div class="severity-bar" style="width:120px">
          <div class="severity-fill" style="width:{score}%; background:{score_color}"></div>
        </div>
      </div>
      <div class="score-meta">
        <div class="score-label">verdict for {domain}</div>
        <div class="score-verdict" style="color:{verdict_color}">{verdict_text}</div>
        <div class="score-summary">{len(findings)} pattern{'s' if len(findings) != 1 else ''} found across {len(categories)} categor{'ies' if len(categories) != 1 else 'y'}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    st.markdown(f"""
    <div class="stats-row">
      <div class="stat-box">
        <div class="stat-num" style="color:#f07070">{critical_count}</div>
        <div class="stat-label">Critical</div>
      </div>
      <div class="stat-box">
        <div class="stat-num" style="color:#e08060">{high_count}</div>
        <div class="stat-label">High</div>
      </div>
      <div class="stat-box">
        <div class="stat-num" style="color:#d4aa50">{medium_count}</div>
        <div class="stat-label">Medium</div>
      </div>
      <div class="stat-box">
        <div class="stat-num" style="color:#70a8cc">{low_count}</div>
        <div class="stat-label">Low</div>
      </div>
      <div class="stat-box">
        <div class="stat-num" style="color:#c8d0db">{len(categories)}</div>
        <div class="stat-label">Categories</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if not findings:
        st.markdown("""
        <div style="text-align:center; padding: 3rem 1rem; color: #5ab070;">
          <div style="font-family: 'IBM Plex Mono', monospace; font-size: 2rem; margin-bottom: 0.5rem;">✓</div>
          <div style="font-size: 1.1rem; font-weight: 500;">No dark patterns detected</div>
          <div style="font-size: 13px; color: #3a4455; margin-top: 4px;">This page passed all checks. Note: some patterns require JavaScript execution to detect.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-header">— findings by severity</div>', unsafe_allow_html=True)

        # Sort: critical first
        order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_findings = sorted(findings, key=lambda f: order[f.severity])

        for f in sorted_findings:
            color = SEVERITY_COLOR[f.severity]
            badge_class = f"badge-{f.severity}"
            st.markdown(f"""
            <div class="finding-card" style="border-left-color:{color}">
              <div class="finding-header">
                <div class="finding-name">{f.name}</div>
                <span class="badge {badge_class}">{f.severity}</span>
              </div>
              <div class="finding-category">{f.category}</div>
              <div class="finding-desc">{f.description}</div>
              <div class="finding-evidence">{f.evidence}</div>
              <div style="font-size:12px; color:#3a4455; margin-top:8px; padding-top:8px; border-top: 1px solid #1e2530;">
                <span style="color:#6b7a8d; font-weight:500;">Fix: </span>{f.recommendation}
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Category breakdown
        st.markdown('<div class="section-header">— category breakdown</div>', unsafe_allow_html=True)

        cat_counts = {}
        for f in findings:
            cat_counts[f.category] = cat_counts.get(f.category, 0) + 1

        max_count = max(cat_counts.values()) if cat_counts else 1
        for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
            pct = int((count / max_count) * 100)
            st.markdown(f"""
            <div style="margin-bottom:10px;">
              <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <span style="font-size:13px; color:#c8d0db; font-family:'IBM Plex Mono',monospace">{cat}</span>
                <span style="font-size:13px; color:#6b7a8d; font-family:'IBM Plex Mono',monospace">{count} finding{'s' if count != 1 else ''}</span>
              </div>
              <div class="severity-bar">
                <div class="severity-fill" style="width:{pct}%; background:#e05a2b; opacity:{0.4 + 0.6*(pct/100):.2f}"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Export JSON
        st.markdown('<div class="section-header">— export report</div>', unsafe_allow_html=True)
        report = {
            "url": url_input,
            "domain": domain,
            "score": score,
            "verdict": verdict_text,
            "total_findings": len(findings),
            "findings": [
                {
                    "name": f.name,
                    "category": f.category,
                    "severity": f.severity,
                    "description": f.description,
                    "evidence": f.evidence,
                    "recommendation": f.recommendation,
                } for f in findings
            ]
        }
        st.download_button(
            label="DOWNLOAD JSON REPORT",
            data=json.dumps(report, indent=2),
            file_name=f"darkscan_{domain.replace('.','_')}.json",
            mime="application/json",
        )

elif scan_btn and not url_input:
    st.warning("Please enter a URL to scan.")

else:
    # Empty state
    st.markdown("""
    <div style="padding: 2rem 0; color: #3a4455; font-family: 'IBM Plex Mono', monospace; font-size: 13px; line-height: 2;">
      Checks performed:<br>
      <span style="color:#e05a2b">01</span> Fake urgency &amp; false scarcity<br>
      <span style="color:#e05a2b">02</span> Hidden costs &amp; fine-print pricing<br>
      <span style="color:#e05a2b">03</span> Confirm-shaming opt-outs<br>
      <span style="color:#e05a2b">04</span> Pre-ticked consent checkboxes<br>
      <span style="color:#e05a2b">05</span> Misdirection &amp; de-emphasized cancel buttons<br>
      <span style="color:#e05a2b">06</span> Roach motel (easy in, hard out)<br>
      <span style="color:#e05a2b">07</span> Privacy zuckering &amp; vague data sharing<br>
      <span style="color:#e05a2b">08</span> Disguised ads &amp; fake download buttons<br>
      <span style="color:#e05a2b">09</span> Trick questions &amp; double negatives<br>
    </div>
    """, unsafe_allow_html=True)
