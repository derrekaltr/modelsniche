#!/usr/bin/env python3
"""Instagram profile → "is this an OF-branded creator?" classifier.

Implements the rules in ../tagging-rules.md. Deterministic, stdlib only.

Input: JSON Lines or a JSON array of profile records. All fields optional except handle:
    handle               str   "countrygirl_nat"
    display_name         str
    category             str   IG category label ("Athlete", "Digital creator", ...)
    bio                  str   full bio text
    links                list  URLs / domains shown in the bio link slot
    highlights           list  story-highlight names
    posts                int
    followers            int
    following            int
    followed_by          list  handles in the "Followed by ..." line
    private              bool
    unavailable          bool  page not available / removed
    confirmed_adult_tile bool  reviewer opened the link tool and saw an OF/Fansly/Fanvue/LoyalFans tile
    listicle             bool  named in an OF-creator listicle (weak corroboration)
    press                bool  press names the person as an OF creator (weak; confirms person, not account)

Output per profile: score 0-5, verdict (include / review / exclude / unverifiable),
signal codes that fired, gray-zone codes, and keyword niche hints.

Usage:
    python classify.py profiles.jsonl            # table
    python classify.py profiles.jsonl --json     # JSON lines
    python classify.py profiles.jsonl --explain  # evidence per signal
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field, asdict
from typing import Iterable

# --------------------------------------------------------------------------- #
# Normalisation
# --------------------------------------------------------------------------- #

# Mathematical alphanumeric blocks creators paste into bios (𝐓𝐎𝐏, 𝙔𝙀𝙎, 𝑻𝑿 ...) → ascii.
_MATH_STARTS = (0x1D400, 0x1D434, 0x1D468, 0x1D49C, 0x1D4D0, 0x1D504, 0x1D538, 0x1D56C,
                0x1D5A0, 0x1D5D4, 0x1D608, 0x1D63C, 0x1D670)
_FANCY: dict[str, str] = {}
for _s in _MATH_STARTS:
    for _i in range(26):
        _FANCY[chr(_s + _i)] = chr(ord("A") + _i)
        _FANCY[chr(_s + 26 + _i)] = chr(ord("a") + _i)


def norm(s: str | None) -> str:
    if not s:
        return ""
    s = "".join(_FANCY.get(ch, ch) for ch in s)
    s = re.sub(r"0nly", "only", s, flags=re.I)
    return s.lower()


def any_re(patterns: Iterable[str], text: str) -> str | None:
    for p in patterns:
        m = re.search(p, text, flags=re.I)
        if m:
            return m.group(0)
    return None


def first_hl(patterns: Iterable[str], highlights: list[str]) -> str | None:
    for h in highlights:
        if any_re(patterns, h):
            return h
    return None


# --------------------------------------------------------------------------- #
# Signal vocabularies (codes match tagging-rules.md)
# --------------------------------------------------------------------------- #

ADULT_EMOJI = "🌶🍑🔞😈💦🥵🍆"          # unambiguous
AMBIG_EMOJI = "👀🔗📎🔥"                # only meaningful with other signals (W6)

S1_HIGHLIGHT = [r"only\s*fans", r"^\s*o\.?f\.?\s*[😈🔥🌶️🍑\s]*$"]

S2_BIO = [
    r"\byes,?\s*i\s*have\s*one\b",
    r"check\s*(below|my\s*highlights?)",
    r"see\s*a\s*?lot\s*more\s*of\s*me",
    r"highlights?\s*for\s*more",
    r"for\s*you\s*to\s*find\s*on\s*your\s*own",
    r"(want|wanna)\s*(to\s*)?see\s*more\s*of\s*me",
    r"link\s*below\s*for\s*more",
    r"\ball\s*my\s*links\b",
    r"the\s*(real|good|fun)\s*stuff\s*is\s*(linked|below)",
    r"\bvip\s*(access|area|page)\b",
]

S3_TEXT = [
    r"\b18\s*\+\s*nsfw\b", r"\bnsfw\b", r"adult\s*content\s*creator", r"male\s*performer",
    r"\bexotic\s*dancer\b", r"\bcam\s*?girl\b", r"\bspicy\s*content\b",
    r"@blacked\w*", r"\bzz\s*contract\b", r"\bbrazzers\b", r"\bvixen\b",
    r"\bfanlock\w*", r"\bfansly\b", r"\bfanvue\b", r"\bloyalfans\b", r"mym\.fans",
]
S3_HIGHLIGHT = [r"\bavn\b", r"\bblacked\b", r"\bcasting\b", r"\bfansly\b"]

S4_BIO = [
    r"\bback-?\s*up\s*(account|page|acct)\b",
    r"this\s*is\s*my\s*back-?\s*up",
    r"\bmain\s*(acct|account|page)\b",
    r"go\s*to\s*@\w+\s*for\s*more",
    r"\bexclusive\s*@\w+",
    r"@\w+\s*on\s*everything",
    r"\b(2nd|3rd|second|third)\s*(insta|ig|instagram|page)\b",
    r"follow\s*my\s*main\s*@",
]

S6 = [r"only\s*brother", r"only\s*fee+ha?ns?", r"only\s*(fans?|fa[n]+)\s*(page|link)"]

M1_HIGHLIGHT = [
    r"\bvip\b", r"exclusive", r"click\s*here", r"^\s*here\b", r"find\s*me", r"check\s*here",
    r"^\s*links?\b", r"^\s*more\b", r"^\s*important", r"verification", r"my\s*socials",
    r"^\s*socials\b", r"\bspicy\b", r"\b18\s*\+", r"\breviews?\b", r"\bnaughty\b",
    r"^\s*[" + ADULT_EMOJI + r"\s️]+$",
]
W6_HIGHLIGHT = [r"^\s*[" + AMBIG_EMOJI + r"\s️]+$"]

M2_DOMAINS = [
    "link.me", "allmylinks.com", "beacons.ai", "hoo.be", "onlylinks.com", "bonafide.us",
    "snipfeed", "linkr.bio", "campsite.bio", "solo.to", "linkin.bio", "linkme.",
    "throne.com", "wishtender.com",
]
LINKTREE = "linktr.ee"
MAINSTREAM = ["instagram.com", "x.com", "twitter.com", "tiktok.com", "youtube.com", "youtu.be",
              "spotify", "facebook.com", "kqed.org", "amazon.com", "eventbrite"]
M3_TLDS = (".vip", ".business", ".xxx", ".fans", ".club")
M3_HINTS = ("yummy", "/welcome", "exclusive", "spicy")
BUSINESS_WORDS = ("shop", "store", "coach", "studio", "app", "academy", "fitness", "transformation",
                  "nutrition", "retreat", "products", "consult", "law", "realty", "agency")

M4_LABEL = r"(content\s*creator|digital\s*creator|creator)"
M4_WORDS = [r"\bspicy\b", r"\bexclusive\b", r"\bnaughty\b", r"\bwild\b", r"\bsexy\b"]
M5 = [r"\btop\s*\d*\.?\d*\s*%", r"\btop\s*(1|0\.\d+)\s*percent"]
M6_HIGHLIGHT = [r"wish\s*-?list", r"spoil", r"telegram", r"\bthrone\b", r"\btribute"]
M6_BIO = [r"spoil\s*(me|us)", r"wish\s*-?list", r"\btelegram\b", r"\bthrone\b", r"\btribute"]
M7 = [r"\bno\s*dms?\b", r"no\s*meet\s*-?ups?", r"dms?\s*(closed|off)\b", r"don'?t\s*dm\b"]

W1_AGENCIES = {"wearenudepr", "nudepr", "unrulyagency", "unruly.agency", "wearesirency", "sirency"}
W4 = [r"official_?$", r"_$", r"\.x{2,}$", r"\.xiii$", r"(?<![a-z])xo$", r"xx$", r"\d{2,}$"]

X1_COACH = [r"online\s*coach", r"apply\s*(for|below|now)", r"\bcoaching\b", r"\bprograms?\b",
            r"lives\s*changed", r"personal\s*trainer", r"\btransformations?\b", r"\bretreats?\b"]
X2_FOUNDER = [r"co-?\s*founder", r"\bfounder\b", r"creative\s*director", r"\bceo\b", r"\bowner\s*of\s*@"]
X3_SPONSOR = [r"\bteam\s*@\w+", r"\bathlete\b", r"sponsored\s*by", r"\bpartnered\s*(youtuber|with)",
              r"\bambassador\b"]
X3_ADULT_AMBASSADOR = [r"@blacked\w*", r"\bvixen\b", r"\bbrazzers\b", r"@bonafide"]
X4_CODES = [r"\bcode\s*[:\-]?\s*[a-z0-9]{3,}\b", r"\bdiscount\b", r"\bltk\b", r"amazon\s*store",
            r"storefront", r"\brevolve\b", r"shop\s*my\b"]
X5_BOOKING = [r"business\s*(inquir|enquir)", r"\bmgmt\b", r"\bmanager\s*:?\s*@", r"@\w*models\b",
              r"\bbookings?\b", r"\bbook\s*me\b"]
X7_CATEGORIES = {"athlete", "coach", "entrepreneur", "public figure", "reel creator", "personal coach",
                 "fitness trainer", "gym/physical fitness center", "fashion model", "model"}

G3 = [r"@onlyfans\s*athlete", r"\bof\s*-?\s*athlete\b", r"ofathlete"]
G4 = [r"official\s*instagram\s*for\s*your\s*favou?rites", r"\bfollows?\s*us\b", r"vote\s*(4|for)\s*your",
      r"hash\s*-?tag\s*your\s*picture", r"\bfan\s*page\b", r"\bfeatur(ing|ed)\s*(the\s*)?(hottest|sexiest)"]
G5 = [r"\bdominatrix\b", r"\bbookings?\s*(and|&)\s*(enquir|inquir)", r"\bcall\s*me\b", r"\btext\s*me\b",
      r"\bslixa\b", r"\bp411\b", r"\btryst\b", r"professional\s*girlfriend", r"this\s*is\s*my\s*only\s*account"]

NICHE_KEYWORDS = {
    "A1": [r"girl\s*next\s*door", r"\bshy\b", r"\bnerdy\b"],
    "A2": [r"\bplayboy\b", r"\bactress\b", r"\bmodel\b", r"\bglam", r"\bfashion\b", r"\brunway\b"],
    "A3": [r"\bgoth\b", r"\balt\b", r"tattoo", r"\bpunk\b", r"\bemo\b", r"\bsfx\b"],
    "A4": [r"\bbarbie\b", r"\bbimbo\b", r"\bdoll\b", r"\bprincess\b"],
    "A5": [r"pin\s*-?up", r"\bvintage\b", r"\bretro\b", r"burlesque"],
    "B1": [r"girlfriend", r"\bgf\b", r"\bgfe\b"],
    "B2": [r"\bnurse\b", r"\bteacher\b", r"flight\s*attendant", r"\bstewardess\b", r"\boffice\b", r"✈"],
    "B3": [r"\bgoddess\b", r"\bmistress\b", r"\bdomme\b", r"\bfindom\b", r"\bfemdom\b", r"\bdominant\b", r"\btribute"],
    "B4": [r"\bcomedian\b", r"\bcomedy\b", r"stand\s*-?up", r"\bpodcast", r"\bcomic\b"],
    "C1": [r"cowgirl", r"\bcountry\b", r"\bwestern\b", r"yeehaw", r"\brodeo\b", r"\bnfr\b", r"sundress", r"\btx\b", r"\btexas\b"],
    "C2": [r"stoner", r"\b420\b", r"\bweed\b", r"cannabis", r"\bdab", r"munchies"],
    "C3": [r"\bnature\b", r"van\s*-?life", r"camping", r"\bhik(e|ing)\b", r"sedona", r"\boutdoors?\b"],
    "C4": [r"bikini", r"\bbeach\b", r"\bsurf", r"\bsummer\b"],
    "D1": [r"\bmom\b", r"\bmommy\b", r"\bmama\b", r"\bmilf\b", r"\bmother\b", r"comeback"],
    "D2": [r"redhead", r"\bginger\b", r"petite", r"\btall\b", r"\d'\d{1,2}", r"freckle"],
    "D3": [r"\bgym\b", r"fitness", r"crossfit", r"gymnast", r"\bworkout", r"\bflex\b"],
    "E1": [r"\btrans\b", r"🏳️‍⚧️", r"\btgirl\b"],
    "E2": [r"\bhusband\b", r"\bfather\b", r"twink", r"\bhimbo\b", r"\bbrother\b", r"\bboy\b", r"\bfor\s*men\b", r"\bmale\b",
           r"\bactor\b", r"\bboxing\b", r"\bhunk\b", r"\bdaddy\b"],
    "F1": [r"cosplay", r"\bgamer\b", r"\banime\b", r"\bwaifu\b", r"\bweeb\b", r"\bsdcc\b", r"\bcon\b", r"(?<!\d):3(?!\d)",
           r"\bkawaii\b", r"\buwu\b", r"\bmeow"],
    "F2": [r"\btwitch\b", r"streamer", r"\bkick\b", r"\bdiscord\b", r"\blive\b"],
    "F3": [r"\bdj\b", r"producer", r"\bmusic\b", r"\brave\b", r"\bstudio\b", r"spotify"],
}
# substrings that are unambiguous inside a handle/slug even without word boundaries
HANDLE_STEMS = {
    "A3": ["goth", "tattoo", "punk", "emo"],
    "A4": ["barbie", "bimbo"],
    "A5": ["pinup"],
    "B1": ["girlfriend", "gfe"],
    "B2": ["nurse", "teacher"],
    "B3": ["goddess", "mistress", "domme", "findom"],
    "C1": ["cowgirl", "country", "western"],
    "C2": ["stoner", "420", "weed"],
    "C3": ["vanlife", "hiker", "nature"],
    "C4": ["bikini", "beach", "surf"],
    "D1": ["mommy", "milf", "mama"],
    "D2": ["redhead", "ginger", "petite"],
    "D3": ["fit", "gym"],
    "E1": ["trans"],
    "E2": ["twink", "hunk", "himbo", "boy"],
    "F1": ["cosplay", "gamer", "waifu", "egirl", "meow"],
    "F2": ["twitch", "stream"],
    "F3": ["dj", "music"],
}
NICHE_NAMES = {
    "A1": "girl-next-door", "A2": "glamour", "A3": "alt/goth", "A4": "bimbo/barbie", "A5": "pin-up",
    "B1": "GFE", "B2": "profession", "B3": "femdom/findom", "B4": "comedy",
    "C1": "country/cowgirl", "C2": "stoner", "C3": "outdoorsy", "C4": "beach/bikini",
    "D1": "MILF", "D2": "trait", "D3": "fitness-forward", "E1": "trans", "E2": "male",
    "F1": "cosplay/e-girl", "F2": "streamer", "F3": "musician",
}


# --------------------------------------------------------------------------- #
# Core
# --------------------------------------------------------------------------- #

@dataclass
class Result:
    handle: str
    score: int = 0
    verdict: str = "exclude"          # include | review | exclude | unverifiable
    tier: str = "none"                # strong | medium | weak | none
    signals: list[str] = field(default_factory=list)
    excludes: list[str] = field(default_factory=list)
    gray: list[str] = field(default_factory=list)
    niches: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)


def _domain(link: str) -> str:
    return re.sub(r"^https?://(www\.)?", "", link).split("/")[0]


def classify(p: dict) -> Result:
    handle = (p.get("handle") or "").lstrip("@").lower()
    bio = norm(p.get("bio"))
    name = norm(p.get("display_name"))
    cat = norm(p.get("category"))
    links = [norm(l) for l in (p.get("links") or [])]
    highs = [norm(h) for h in (p.get("highlights") or [])]
    followed_by = {norm(f).lstrip("@") for f in (p.get("followed_by") or [])}
    posts = p.get("posts")
    following = p.get("following") or 0
    private = bool(p.get("private"))
    text = " \n ".join([name, bio, cat])
    everything = " \n ".join([text] + links + highs)

    r = Result(handle=handle)
    ev = r.evidence

    def hit(code: str, val) -> int:
        if val:
            r.signals.append(code)
            ev[code] = val
            return 1
        return 0

    def ex(code: str, val) -> None:
        if val:
            r.excludes.append(code)
            ev[code] = val

    if p.get("unavailable"):
        r.verdict, r.notes = "unverifiable", ["profile unavailable (G8)"]
        return r

    # ---- pre-empting gray zones: studio/aggregator (G4), booking pages (G5) ----
    g4 = any_re(G4, text)
    if g4:
        r.gray.append("G4"); ev["G4"] = g4
        r.notes.append("studio / aggregator / fan page → exclude")
        return r
    g5 = any_re(G5, text)
    if g5:
        r.gray.append("G5"); ev["G5"] = g5
        r.notes.append("pro-domme / escort booking page → exclude from OF-creator set")
        return r

    # ---- exclude signals (computed first; they gate M3) ----------------------
    ex("X1", any_re(X1_COACH, text))
    ex("X2", any_re(X2_FOUNDER, text))
    x3 = any_re(X3_SPONSOR, text)
    if x3 and not any_re(X3_ADULT_AMBASSADOR, text):
        ex("X3", x3)
    ex("X4", any_re(X4_CODES, everything))
    ex("X5", any_re(X5_BOOKING, text))

    # ---- strong ---------------------------------------------------------------
    strong = 0
    strong += hit("S1", first_hl(S1_HIGHLIGHT, highs))
    strong += hit("S2", any_re(S2_BIO, bio))
    strong += hit("S3", any_re(S3_TEXT, text) or first_hl(S3_HIGHLIGHT, highs))
    strong += hit("S4", any_re(S4_BIO, bio))
    if posts is not None and posts <= 1 and following <= 5 and (links or re.search(r"@\w{3,}", bio)):
        strong += hit("S5", f"{posts} post(s), following {following}, pointer bio")
    strong += hit("S6", any_re(S6, everything))

    # ---- medium ---------------------------------------------------------------
    medium = 0
    weak = 0
    medium += hit("M1", first_hl(M1_HIGHLIGHT, highs))
    weak += hit("W6", first_hl(W6_HIGHLIGHT, highs))

    m2 = next((d for l in links for d in M2_DOMAINS if d in l), None)
    has_linktree = any(LINKTREE in l for l in links)
    corroborated = bool(p.get("confirmed_adult_tile") or p.get("listicle") or p.get("press"))
    if p.get("confirmed_adult_tile"):
        m2 = m2 or "link tool with confirmed adult tile"
    elif has_linktree and not m2:
        if corroborated:
            m2 = "linktr.ee + external corroboration"
        else:
            ev["M2?"] = "linktr.ee present — open it; auto-titled '<name> OnlyFans Official' when an OF tile exists"
            r.notes.append("Linktree unconfirmed (M2?) — fetch the page to resolve")
    medium += hit("M2", m2)

    m3 = None
    hstem = re.sub(r"[^a-z]", "", handle)
    nstem = re.sub(r"[^a-z]", "", name)
    for l in links:
        dom = _domain(l)
        if not dom or any(d in dom for d in M2_DOMAINS + [LINKTREE] + MAINSTREAM):
            continue
        if any(w in l for w in BUSINESS_WORDS):
            continue
        stem = re.sub(r"[^a-z]", "", dom.split(".")[0])
        vanity = dom.endswith(M3_TLDS) or any(h in l for h in M3_HINTS)
        namey = len(stem) >= 4 and (stem in hstem or hstem in stem or (len(nstem) >= 4 and (stem in nstem or nstem in stem)))
        if vanity or (namey and not r.excludes):
            m3 = dom
            break
    medium += hit("M3", m3)

    if re.search(M4_LABEL, text) and (any(e in everything for e in ADULT_EMOJI) or any_re(M4_WORDS, text)):
        medium += hit("M4", "creator label + adult emoji/word")
    medium += hit("M5", any_re(M5, bio))
    medium += hit("M6", first_hl(M6_HIGHLIGHT, highs) or any_re(M6_BIO, bio)
                  or next((d for l in links for d in ("throne.com", "wishtender", "t.me/") if d in l), None))
    medium += hit("M7", any_re(M7, bio))

    # ---- weak -----------------------------------------------------------------
    weak += hit("W1", next((f for f in followed_by if f in W1_AGENCIES), None))
    weak += hit("W2", "listicle" if p.get("listicle") else None)
    if re.search(r"follow\s*me\s*everywhere", bio) or sum(1 for h in highs if any_re([r"twitch", r"discord", r"tiktok", r"youtube", r"socials"], h)) >= 3:
        weak += hit("W3", "platform-hop funnel")
    weak += hit("W4", any_re(W4, handle))
    weak += hit("W5", "press" if p.get("press") else None)

    # ---- conditional excludes -------------------------------------------------
    if cat in X7_CATEGORIES and not (strong or medium):
        ex("X7", cat)
    if re.search(r"twitch\s*(partner|streamer|affiliate)", text) and not (strong or medium):
        ex("X6", "streamer without an adult tile")

    # ---- G3: OF link / OF-athlete framing without adult coding ----------------
    g3 = any_re(G3, everything)
    if g3 and not strong:
        r.gray.append("G3"); ev["G3"] = g3
        r.notes.append("OF-athlete / SFW-OF framing without adult coding → exclude (OF-person, not IG-branded)")
        medium = 0
        r.signals = [s for s in r.signals if not s.startswith("M")]

    # ---- score ----------------------------------------------------------------
    if "S1" in r.signals or "S3" in r.signals:
        r.score, r.tier = 5, "strong"
    elif strong:
        r.score, r.tier = 4, "strong"
    elif medium >= 2 or (medium == 1 and weak >= 1):
        r.score, r.tier = 3, "medium"
    elif medium == 1:
        r.score, r.tier = 2, "medium"
    elif weak:
        r.score, r.tier = 1, "weak"

    r.verdict = "include" if r.score >= 3 else "review" if r.score == 2 else "exclude"

    # ---- notes ----------------------------------------------------------------
    if "S4" in r.signals and strong == 1 and not medium:
        r.notes.append("cross-references an alt/main (G2) — tag as OF-creator; verify the paired account")
    if r.excludes and r.verdict == "include":
        r.notes.append("include signals override exclude signals (brand deals + funnel both present)")
    if r.verdict == "exclude" and not r.signals and not r.excludes and not private and not r.gray:
        r.notes.append("no signals either way — may be a sanitized main (G1)")
    if r.verdict == "exclude" and p.get("press") and not strong:
        r.notes.append("press confirms the person, not this account (G1) — IG-only negative is correct")
    if private:
        r.notes.append("private profile — highlights/links partly hidden")
    if (p.get("followers") or 0) >= 5_000_000 and r.verdict != "exclude":
        r.notes.append("mega account — flag as celebrity tier (G6)")

    # ---- niche hints ----------------------------------------------------------
    # handle and link slugs are strong niche cues ("katie_k_beach__", "linktr.ee/JovenTwinkOk", "gothpixi")
    slugs = re.sub(r"[._\-]+", " ", handle) + " " + " ".join(re.sub(r"[._\-/]+", " ", l) for l in links)
    hint_text = everything + " \n " + slugs
    scores = {c: sum(1 for pat in pats if re.search(pat, hint_text)) for c, pats in NICHE_KEYWORDS.items()}
    for c, stems in HANDLE_STEMS.items():           # boundary-less pass for compound handles
        n = sum(1 for s in stems if s in slugs)
        if n:
            scores[c] = scores.get(c, 0) + n
    r.niches = [f"{c}:{NICHE_NAMES[c]}" for c, n in sorted(scores.items(), key=lambda kv: -kv[1]) if n][:3]
    return r


# --------------------------------------------------------------------------- #
# IO
# --------------------------------------------------------------------------- #

def load(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        raw = f.read().strip()
    if not raw:
        return []
    if raw.startswith("["):
        return json.loads(raw)
    return [json.loads(line) for line in raw.splitlines() if line.strip() and not line.startswith("#")]


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="profiles .jsonl / .json")
    ap.add_argument("--json", action="store_true", help="emit JSON lines")
    ap.add_argument("--explain", action="store_true", help="show matched evidence and notes")
    a = ap.parse_args(argv)
    results = [classify(p) for p in load(a.path)]
    if a.json:
        for r in results:
            print(json.dumps(asdict(r), ensure_ascii=False))
        return
    w = max((len(r.handle) for r in results), default=6)
    print(f"{'handle':<{w}}  score  verdict       signals                          niches")
    for r in results:
        sig = ",".join(r.signals + [f"!{x}" for x in r.excludes] + [f"~{g}" for g in r.gray])
        print(f"{r.handle:<{w}}  {r.score:^5}  {r.verdict:<12}  {sig:<32} {' '.join(r.niches)}")
        if a.explain:
            for k, v in r.evidence.items():
                print(f"{'':<{w}}      {k}: {v!r}")
            for n in r.notes:
                print(f"{'':<{w}}      note: {n}")


if __name__ == "__main__":
    main()
