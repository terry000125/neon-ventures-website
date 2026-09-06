#!/usr/bin/env python3
"""Regenerate podcast.html from the Weeks Ahead AI RSS feed.

Stdlib only. Run:  python3 scripts/build_podcast.py
Writes podcast.html at the repo root. Safe to run repeatedly; if the feed
cannot be fetched the existing page is left untouched.
"""
import html
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

FEED = "https://rss.buzzsprout.com/2520442.rss"
SITE = "https://www.neonventures.biz"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "podcast.html")

NS = {
    "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
    "content": "http://purl.org/rss/1.0/modules/content/",
}

APPLE = "https://podcasts.apple.com/us/podcast/weeks-ahead-ai/id1831122696"
SPOTIFY = "https://open.spotify.com/show/4T69N0FqA46m4SlNnvVf8m"
YOUTUBE = "https://youtube.com/@WeeksAheadAI"


def text_of(raw, limit=260):
    """Strip HTML to a plain summary, dropping any leading headline line."""
    if not raw:
        return ""
    s = re.sub(r"<br\s*/?>", "\n", raw, flags=re.I)
    s = re.sub(r"</p>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\u00a0", " ")
    paras = [re.sub(r"\s+", " ", x).strip() for x in s.split("\n")]
    paras = [x for x in paras if x]
    # Show notes often open with a bold headline restating the episode title.
    if len(paras) > 1 and len(paras[0]) < 90 and paras[0][-1] not in ".!?":
        paras = paras[1:]
    s = " ".join(paras)
    if len(s) <= limit:
        return s
    cut = s[:limit].rsplit(" ", 1)[0].rstrip(" ,.;:\u2014-")
    return cut + "\u2026"


def duration(raw):
    """itunes:duration -> '29 min'. Accepts seconds or HH:MM:SS."""
    if not raw:
        return ""
    raw = raw.strip()
    if ":" in raw:
        parts = [int(p) for p in raw.split(":")]
        secs = 0
        for p in parts:
            secs = secs * 60 + p
    else:
        try:
            secs = int(raw)
        except ValueError:
            return ""
    mins = round(secs / 60)
    return f"{mins} min"


def episode_page(enclosure_url):
    """Buzzsprout enclosure -> public episode page."""
    if not enclosure_url:
        return ""
    return re.sub(r"\.mp3(\?.*)?$", "", enclosure_url)


def esc(s):
    return html.escape(s or "", quote=True)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "neonventures.biz podcast build"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def parse(raw):
    ch = ET.fromstring(raw).find("channel")
    show = {
        "title": ch.findtext("title") or "Weeks Ahead AI",
        "description": text_of(ch.findtext("description"), 400),
        "image": (ch.find("itunes:image", NS).get("href")
                  if ch.find("itunes:image", NS) is not None else ""),
    }
    eps = []
    for it in ch.findall("item"):
        enc = it.find("enclosure")
        enc_url = enc.get("url") if enc is not None else ""
        img = it.find("itunes:image", NS)
        try:
            dt = parsedate_to_datetime(it.findtext("pubDate") or "")
        except Exception:
            dt = None
        eps.append({
            "number": it.findtext("itunes:episode", default="", namespaces=NS),
            "title": it.findtext("title") or "",
            "summary": text_of(it.findtext("description")
                               or it.findtext("itunes:summary", namespaces=NS)),
            "date": dt,
            "duration": duration(it.findtext("itunes:duration", default="", namespaces=NS)),
            "audio": enc_url,
            "page": episode_page(enc_url),
            "image": img.get("href") if img is not None else show["image"],
        })
    eps.sort(key=lambda e: (e["date"] or datetime.min.replace(tzinfo=timezone.utc)), reverse=True)
    return show, eps


def strip_number(title):
    """'#25 - Foo' -> 'Foo' (the number is shown as its own badge)."""
    return re.sub(r"^#?\d+\s*[-–—:]\s*", "", title).strip()


NAV = """  <nav class="navbar" id="navbar">
    <a href="/" class="navbar-brand">
      <img src="/neon-ventures-a7.png" alt="Neon Ventures">
    </a>
    <div class="nav-links" id="navLinks">
      <a href="/">Home</a>
      <a href="/#portfolio">Portfolio</a>
      <a href="/#about">About</a>
      <a href="/podcast" aria-current="page">Podcast</a>
      <a href="/lending">Loan Program</a>
      <a href="/#contact">Contact</a>
    </div>
    <button class="nav-toggle" id="navToggle" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
  </nav>"""

FOOTER = """  <footer class="footer">
    <p>&copy; 2026 Neon Ventures. All rights reserved.</p>
    <p class="address">212 South Elm Street, Denton, TX 76201</p>
  </footer>"""

ICON_APPLE = ('<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">'
              '<path d="M12 2a10 10 0 0 0-10 10 10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2zm0 3.6a2.3 2.3 0 1 1 0 4.6 2.3 2.3 0 0 1 0-4.6zm0 5.9c1.9 0 3.1 1 3.1 2.3 0 .9-.3 2.4-.7 3.5-.4 1-1.2 1.7-2.4 1.7s-2-.7-2.4-1.7c-.4-1.1-.7-2.6-.7-3.5 0-1.3 1.2-2.3 3.1-2.3z"/></svg>')
ICON_SPOTIFY = ('<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">'
                '<path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm4.6 14.4a.8.8 0 0 1-1.1.3c-3-1.8-6.7-2.2-11.1-1.2a.8.8 0 1 1-.3-1.5c4.8-1.1 8.9-.6 12.2 1.4.4.2.5.7.3 1zm1.2-2.7a1 1 0 0 1-1.3.3c-3.4-2.1-8.6-2.7-12.6-1.5a1 1 0 1 1-.6-1.9c4.6-1.4 10.3-.7 14.2 1.7.5.3.6.9.3 1.4zm.1-2.8C14 8.6 7.9 8.4 4.4 9.5a1.2 1.2 0 0 1-.7-2.3c4-1.2 10.7-1 14.9 1.5a1.2 1.2 0 1 1-1.2 2z"/></svg>')
ICON_YOUTUBE = ('<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">'
                '<path d="M23 12s0-3.3-.4-4.8c-.2-.9-.9-1.5-1.7-1.7C19.3 5 12 5 12 5s-7.3 0-8.9.5c-.8.2-1.5.8-1.7 1.7C1 8.7 1 12 1 12s0 3.3.4 4.8c.2.9.9 1.5 1.7 1.7C4.7 19 12 19 12 19s7.3 0 8.9-.5c.8-.2 1.5-.8 1.7-1.7.4-1.5.4-4.8.4-4.8zM9.8 15.3V8.7l6.1 3.3-6.1 3.3z"/></svg>')


def render(show, eps):
    desc = ("Weeks Ahead AI is a biweekly podcast hosted by Brad Andrus, Mitch Felderhoff and "
            "Terry Brockett, showing business owners how to actually use AI to save time and stay ahead.")
    cards, ld_eps = [], []

    for e in eps:
        title = strip_number(e["title"])
        num = f'<span class="ep-num">#{esc(e["number"])}</span>' if e["number"] else ""
        meta = []
        if e["date"]:
            meta.append(e["date"].strftime("%B %-d, %Y"))
        if e["duration"]:
            meta.append(e["duration"])
        meta_line = " &middot; ".join(meta)
        page_link = (f'<a class="ep-link" href="{esc(e["page"])}" target="_blank" '
                     f'rel="noopener noreferrer">Episode page &amp; transcript &rarr;</a>'
                     if e["page"] else "")
        cards.append(f"""      <article class="ep-card">
        <div class="ep-head">
          {num}
          <div>
            <h2 class="ep-title">{esc(title)}</h2>
            <p class="ep-meta">{meta_line}</p>
          </div>
        </div>
        <p class="ep-summary">{esc(e["summary"])}</p>
        <audio class="ep-audio" controls preload="none" src="{esc(e["audio"])}"></audio>
        {page_link}
      </article>""")

        ld_eps.append(f"""        {{
          "@type": "PodcastEpisode",
          "episodeNumber": "{esc(e["number"])}",
          "name": {_json(title)},
          "datePublished": "{e["date"].strftime("%Y-%m-%d") if e["date"] else ""}",
          "associatedMedia": {{ "@type": "MediaObject", "contentUrl": "{esc(e["audio"])}" }}
        }}""")

    ld = f"""  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "PodcastSeries",
    "name": "Weeks Ahead AI",
    "url": "{SITE}/podcast",
    "description": {_json(desc)},
    "webFeed": "{FEED}",
    "author": [
      {{ "@type": "Person", "name": "Brad Andrus" }},
      {{ "@type": "Person", "name": "Mitch Felderhoff" }},
      {{ "@type": "Person", "name": "Terry Brockett" }}
    ],
    "hasPart": [
{",".join(ld_eps)}
    ]
  }}
  </script>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Weeks Ahead AI Podcast | Neon Ventures</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@400;500;600&display=swap" rel="stylesheet">
  <meta name="description" content="{esc(desc)}">
  <link rel="icon" type="image/png" href="/neon-ventures-a7.png">
  <link rel="canonical" href="{SITE}/podcast">
  <link rel="alternate" type="application/rss+xml" title="Weeks Ahead AI" href="{FEED}">
  <meta property="og:title" content="Weeks Ahead AI Podcast | Neon Ventures">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:image" content="{esc(show["image"])}">
  <meta property="og:url" content="{SITE}/podcast">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Neon Ventures">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Weeks Ahead AI Podcast | Neon Ventures">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{esc(show["image"])}">
  <link rel="stylesheet" href="/styles.css">
{ld}
</head>
<body>
{NAV}

  <section class="pod-hero">
    <div class="pod-hero-inner">
      <img class="pod-art" src="{esc(show["image"])}" alt="Weeks Ahead AI cover art">
      <div>
        <p class="section-label">Podcast</p>
        <h1 class="pod-title">Weeks Ahead AI</h1>
        <p class="pod-desc">{esc(show["description"])}</p>
        <p class="pod-hosts">Hosted by Brad Andrus, Mitch Felderhoff and Terry Brockett &middot; Biweekly</p>
        <div class="pod-subscribe">
          <a href="{APPLE}" target="_blank" rel="noopener noreferrer">{ICON_APPLE}<span>Apple Podcasts</span></a>
          <a href="{SPOTIFY}" target="_blank" rel="noopener noreferrer">{ICON_SPOTIFY}<span>Spotify</span></a>
          <a href="{YOUTUBE}" target="_blank" rel="noopener noreferrer">{ICON_YOUTUBE}<span>YouTube</span></a>
        </div>
      </div>
    </div>
  </section>

  <section class="pod-episodes">
    <div class="pod-episodes-inner">
      <p class="pod-count">{len(eps)} episodes</p>
{chr(10).join(cards)}
    </div>
  </section>

{FOOTER}

  <script src="/site.js"></script>
</body>
</html>
"""


def _json(s):
    import json
    return json.dumps(s, ensure_ascii=False)


def main():
    try:
        raw = fetch(FEED)
    except Exception as exc:
        print(f"feed fetch failed: {exc}", file=sys.stderr)
        return 1
    show, eps = parse(raw)
    if not eps:
        print("no episodes parsed; leaving podcast.html untouched", file=sys.stderr)
        return 1
    page = render(show, eps)
    old = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
    if old == page:
        print(f"podcast.html already current ({len(eps)} episodes)")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page)
    print(f"wrote podcast.html ({len(eps)} episodes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
