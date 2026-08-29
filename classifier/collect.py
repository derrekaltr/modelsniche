#!/usr/bin/env python3
"""Collect public Instagram profile fields with headless Chrome (logged-out) → classifier JSONL.

    python3 classifier/collect.py prospects/batch-01.txt > prospects/batch-01.jsonl

Logged-out Instagram renders the profile header: name, follower/following counts, bio, bio link,
story-highlight names and "Accounts you might like". Post counts are not shown logged-out.
Private and unavailable profiles are flagged. ~8-12 s per handle; be polite (sequential, no retries storm).
"""
from __future__ import annotations
import html, json, re, subprocess, sys, time

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
STOP = {"Threads", "Link icon", "Posts", "Reels", "Tagged", "Highlights"}

def num(s: str) -> int | None:
    m = re.match(r"^\s*([\d.,]+)\s*([KkMm]?)\s*$", s)
    if not m: return None
    v = float(m.group(1).replace(",", "")); u = m.group(2).upper()
    return int(v * (1_000_000 if u == "M" else 1_000 if u == "K" else 1))

def fetch_text(handle: str) -> str:
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--window-size=1200,1600",
           "--virtual-time-budget=6000", "--dump-dom", f"https://www.instagram.com/{handle}/"]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
    t = re.sub(r"<script.*?</script>", "", out, flags=re.S)
    t = re.sub(r"<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t)
    t = html.unescape(t)
    return "\n".join(l.strip() for l in t.splitlines() if l.strip())

def parse(handle: str, text: str) -> dict:
    rec = {"handle": handle, "collected": time.strftime("%Y-%m-%d"), "source": "instagram-loggedout-headless"}
    lines = text.splitlines()
    if "Sorry, this page isn't available" in text or "Page not found" in text:
        rec["unavailable"] = True; return rec
    if "This account is private" in text or "This Account is Private" in text:
        rec["private"] = True
    if "You must be 18 years old or over to see this profile" in text:
        rec["restricted"] = "18+"          # Instagram age-gates the profile for logged-out viewers
        m = re.search(r"^(.*?) \(@", lines[0]); rec["display_name"] = m.group(1) if m else ""
        return rec
    if "unavailable for certain audiences" in text:
        rec["restricted"] = "audience"     # Instagram restricts the profile for logged-out viewers
        m = re.search(r"^(.*?) \(@", lines[0]); rec["display_name"] = m.group(1) if m else ""
        return rec
    try:
        i = next(k for k, l in enumerate(lines) if l == "followers") - 1
    except StopIteration:
        rec["unparsed"] = True; rec["raw_head"] = lines[:40]; return rec
    rec["followers"] = num(lines[i])
    j = next((k for k, l in enumerate(lines) if l == "following"), None)
    if j: rec["following"] = num(lines[j - 1])
    k = (j or i) + 1
    rec["display_name"] = lines[k] if k < len(lines) else ""
    k += 1
    bio, links, highs = [], [], []
    mode = "bio"
    while k < len(lines):
        l = lines[k]
        if l in ("Posts", "Reels", "Tagged") and mode != "bio": break
        if l == "Posts" and mode == "bio": break
        if l == "Threads": k += 2; continue                     # "Threads" badge + handle; bio continues after it
        if l == "Link icon":
            k += 1
            if k < len(lines): links.append(lines[k])
            k += 1; mode = "hl"; continue
        if mode == "bio":
            # no bio link: highlights still follow the bio — detect the switch by short emoji/title-like lines
            bio.append(l)
        else:
            highs.append(l)
        k += 1
    rec["bio"] = " ".join(bio).strip()
    rec["links"] = links
    rec["highlights"] = [h for h in highs if h not in ("Verified", "Options", "Follow", "Message")]
    if "Accounts you might like" in text:
        s = lines.index("Accounts you might like") + 1
        sug = [l for l in lines[s:s + 60] if l not in ("See all", "Verified", "Follow", "Meta", "About") and not l.startswith("Show more")]
        rec["suggested_display_names"] = list(dict.fromkeys(sug))[:12]
    return rec

def main():
    src = sys.argv[1]
    handles = [h.strip().lstrip("@") for h in open(src) if h.strip() and not h.startswith("#")]
    for h in handles:
        try:
            rec = parse(h, fetch_text(h))
        except Exception as e:  # noqa: BLE001
            rec = {"handle": h, "error": str(e)}
        print(json.dumps(rec, ensure_ascii=False), flush=True)
        time.sleep(2)

if __name__ == "__main__":
    main()
