#!/usr/bin/env python3
"""Build dashboard/index.html from niches.md, tagging-rules.md and the classifier fixtures.

    python3 dashboard/build.py          # writes dashboard/index.html
    open dashboard/index.html

Single self-contained file: no network, no build tooling, works from the filesystem.
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "classifier"))
from classify import classify, load  # noqa: E402

# --------------------------------------------------------------------------- #
# Markdown helpers
# --------------------------------------------------------------------------- #

def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{link_target(m.group(2))}">{m.group(1)}</a>', s)
    s = re.sub(r"(?<![\w@/])@([A-Za-z0-9_.]+[A-Za-z0-9_])", r'<a class="handle" href="https://www.instagram.com/\1/" target="_blank" rel="noopener">@\1</a>', s)
    return s


def link_target(url: str) -> str:
    if url.startswith("tagging-rules.md"):
        return "#rules"
    if url.startswith("niches.md"):
        return "#niches"
    return html.escape(url)


def parse_table(lines: list[str]) -> tuple[list[str], list[list[str]]]:
    rows = []
    for ln in lines:
        ln = ln.strip()
        if not ln.startswith("|"):
            continue
        if re.match(r"^\|\s*:?-{2,}", ln):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        rows.append(cells)
    if not rows:
        return [], []
    return rows[0], rows[1:]


def table_html(header, rows, cls=""):
    out = [f'<table class="{cls}"><thead><tr>' + "".join(f"<th>{inline(h)}</th>" for h in header) + "</tr></thead><tbody>"]
    for r in rows:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def md_to_html(md: str, heading_shift: int = 1) -> str:
    """Small markdown renderer for the rules doc: headings, tables, lists, paragraphs, hr."""
    lines = md.splitlines()
    out, i, para = [], 0, []

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            flush(); i += 1; continue
        if s == "---":
            flush(); out.append("<hr>"); i += 1; continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            flush()
            lvl = min(6, len(m.group(1)) + heading_shift)
            txt = m.group(2)
            hid = "r-" + re.sub(r"[^a-z0-9]+", "-", txt.lower()).strip("-")
            out.append(f'<h{lvl} id="{hid}">{inline(txt)}</h{lvl}>')
            i += 1; continue
        if s.startswith("|"):
            flush()
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i]); i += 1
            h, rows = parse_table(block)
            out.append(table_html(h, rows, "doc"))
            continue
        if re.match(r"^[-*]\s+", s):
            flush()
            out.append("<ul>")
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                out.append("<li>" + inline(re.sub(r"^\s*[-*]\s+", "", lines[i])) + "</li>"); i += 1
            out.append("</ul>")
            continue
        if re.match(r"^\d+\.\s+", s):
            flush()
            out.append("<ol>")
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                out.append("<li>" + inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])) + "</li>"); i += 1
            out.append("</ol>")
            continue
        para.append(s); i += 1
    flush()
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# niches.md → structured data
# --------------------------------------------------------------------------- #

FIELD_RE = re.compile(r"^\*\*([^*]+?)\.\*\*\s*(.*)$")
FIT_RE = re.compile(r"^\*\*New-creator fit:\s*([^*]+?)\.?\*\*\s*(.*)$")
EX_RE = re.compile(r"^-\s+`@([A-Za-z0-9_.]+)`(?:\s*[/↔]\s*`@([A-Za-z0-9_.]+)`)?\s*·\s*([^·]+?)\s*·\s*(.*)$")


def fit_level(label: str) -> str:
    l = label.lower()
    if l.startswith("high") and "low" in l:
        return "mixed"
    if l.startswith("high"):
        return "high"
    if l.startswith("medium") or l.startswith("med"):
        return "medium" if "high" not in l else "medhigh"
    if l.startswith("low"):
        return "low" if "med" not in l else "lowmed"
    return "mixed"


def parse_niches(md: str) -> dict:
    lines = md.splitlines()
    data = {"intro": [], "families": [], "provisional": {"header": [], "rows": []},
            "fit_matrix": {"header": [], "rows": [], "reading": ""}, "notes": [], "verified_date": ""}
    fam = None
    niche = None
    section = "intro"
    i = 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        m_fam = re.match(r"^# Family ([A-F]) — (.+)$", s)
        if m_fam:
            fam = {"code": m_fam.group(1), "name": m_fam.group(2), "niches": []}
            data["families"].append(fam); niche = None; section = "family"; i += 1; continue
        if s.startswith("# Provisional"):
            section = "provisional"; niche = None; i += 1; continue
        if s.startswith("# Fit matrix"):
            section = "fit"; niche = None; i += 1; continue
        if s.startswith("# Research notes"):
            section = "notes"; niche = None; i += 1; continue
        if s.startswith("# ") or s.startswith("## How to read"):
            if section == "intro" and s.startswith("## How to read"):
                section = "howto"
            i += 1; continue
        m_n = re.match(r"^## ([A-F]\d)\. (.+)$", s)
        if m_n and fam:
            niche = {"code": m_n.group(1), "name": m_n.group(2), "family": fam["code"], "family_name": fam["name"],
                     "fields": {}, "fit": "", "fit_level": "mixed", "fit_text": "", "examples": [], "example_notes": []}
            fam["niches"].append(niche); i += 1; continue

        if section == "intro":
            if s.startswith("**"):
                data["intro"].append(inline(s))
                md_ = re.search(r"\*\*(\d{4}-\d{2}-\d{2})\*\*", s)
                if md_:
                    data["verified_date"] = md_.group(1)
            i += 1; continue

        if section == "family" and niche:
            m_fit = FIT_RE.match(s)
            if m_fit:
                niche["fit"] = m_fit.group(1).strip()
                niche["fit_level"] = fit_level(niche["fit"])
                niche["fit_text"] = inline(m_fit.group(2))
                i += 1; continue
            m_f = FIELD_RE.match(s)
            if m_f and m_f.group(1) != "Verified examples":
                niche["fields"][m_f.group(1)] = inline(m_f.group(2)); i += 1; continue
            if m_f and m_f.group(1) == "Verified examples":
                i += 1
                while i < len(lines) and lines[i].strip().startswith("-"):
                    t = lines[i].strip()
                    m_e = EX_RE.match(t)
                    if m_e:
                        sizes = [x.strip() for x in m_e.group(3).split("/")]
                        handles = [h for h in (m_e.group(1), m_e.group(2)) if h]
                        for k, h in enumerate(handles):
                            niche["examples"].append({"handle": h, "size": sizes[min(k, len(sizes) - 1)], "signal": inline(m_e.group(4))})
                    else:
                        niche["example_notes"].append(inline(re.sub(r"^-\s+", "", t).strip("*() ").rstrip(".")))
                    i += 1
                continue
            i += 1; continue

        if section == "provisional":
            if s.startswith("|"):
                block = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    block.append(lines[i]); i += 1
                h, rows = parse_table(block)
                data["provisional"] = {"header": h, "rows": rows}
                continue
            i += 1; continue

        if section == "fit":
            if s.startswith("|"):
                block = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    block.append(lines[i]); i += 1
                h, rows = parse_table(block)
                data["fit_matrix"]["header"] = h
                data["fit_matrix"]["rows"] = rows
                continue
            if s.startswith("**Reading it"):
                data["fit_matrix"]["reading"] = inline(s)
            i += 1; continue

        if section == "notes":
            if s.startswith("-"):
                data["notes"].append(inline(re.sub(r"^-\s+", "", s)))
            i += 1; continue
        i += 1
    return data


# --------------------------------------------------------------------------- #
# Classifier audit
# --------------------------------------------------------------------------- #

def audit() -> list[dict]:
    import glob
    sources = [("fixtures", os.path.join(ROOT, "classifier", "fixtures", "profiles.jsonl"))]
    for f in sorted(glob.glob(os.path.join(ROOT, "prospects", "*.jsonl"))):
        sources.append((os.path.splitext(os.path.basename(f))[0], f))
    rows = []
    for batch, path in sources:
      for p in load(path):
        r = classify(p)
        rows.append({
            "batch": batch, "link_resolves_to": p.get("link_resolves_to", ""), "restricted": p.get("restricted", ""),
            "handle": r.handle, "score": r.score, "verdict": r.verdict, "tier": r.tier,
            "signals": r.signals, "excludes": r.excludes, "gray": r.gray, "niches": r.niches,
            "evidence": {k: str(v) for k, v in r.evidence.items()}, "notes": r.notes,
            "expected": p.get("expect", []), "ok": r.verdict in p.get("expect", []),
            "followers": p.get("followers"), "bio": p.get("bio", ""), "highlights": p.get("highlights", []),
            "links": p.get("links", []), "category": p.get("category", ""), "fixture_note": p.get("note", ""),
        })
    return rows


# --------------------------------------------------------------------------- #
# Template
# --------------------------------------------------------------------------- #

# DashMin-style outline hexagon mark. Drop a real mark at dashboard/brand/logo.svg to override.
FALLBACK_LOGO = (
    '<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" aria-label="Creator Niche Dossier">'
    '<polygon points="20,3 35,11.5 35,28.5 20,37 5,28.5 5,11.5" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linejoin="round"/>'
    '<polygon points="20,12 27,16 27,24 20,28 13,24 13,16" fill="#c26bbc"/>'
    '</svg>'
)

TEMPLATE = r"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Creator Niche Dossier — OF creators as branded on Instagram</title>
<style>__CSS__</style>
</head>
<body>
<aside class="rail">
  <div class="brand" style="color:var(--text)">__LOGO__<div class="wordmark"><b>Dossier</b><small>Creator niches · Instagram</small></div></div>
  <div class="section">Playbook</div>
  <nav>
    <a href="#overview"><span class="n">01</span>Overview</a>
    <a href="#niches"><span class="n">02</span>Niche explorer</a>
    <a href="#matrix"><span class="n">03</span>Fit matrix</a>
    <a href="#provisional"><span class="n">04</span>Provisional &amp; modifiers</a>
    <a href="#rules"><span class="n">05</span>Tagging rules</a>
    <a href="#audit"><span class="n">06</span>Classifier audit</a>
    <a href="#method"><span class="n">07</span>Method &amp; caveats</a>
  </nav>
  <div class="meta">Handles verified <b>__VERIFIED__</b><br>Built <b>__BUILT__</b> from <code>niches.md</code>, <code>tagging-rules.md</code>, <code>classifier/</code><br><br>Regenerate: <code>python3 dashboard/build.py</code></div>
</aside>

<div class="themebar"><button class="tbtn" id="themeToggle" title="Toggle light / dark"><span class="moon">🌙</span><span class="sun">☀️</span></button></div>

<main>
<section id="overview">
  <p class="eyebrow">01 · Overview</p>
  <h1>How OnlyFans creators brand themselves on Instagram — and how to tell them apart from influencers who don't.</h1>
  <p class="lede">A field guide for matching new creators to a niche they can credibly execute, plus the rules for tagging accounts so fitness models and brand-deal influencers stay out of the pool.</p>
  <div class="stats">
    <div class="stat"><div class="v">__N_NICHES__</div><div class="l">Niches · __N_FAMILIES__ families</div></div>
    <div class="stat"><div class="v">__N_EXAMPLES__</div><div class="l">Verified example handles</div></div>
    <div class="stat"><div class="v">__N_PROV__</div><div class="l">Provisional niches &amp; modifiers</div></div>
    <div class="stat"><div class="v">__N_AUDIT__</div><div class="l">Profiles classified · __N_PROSPECTS__ prospects</div></div>
  </div>
  <div class="twocol">
    <div class="intro">__INTRO__</div>
    <div>
      <div class="callout">
        <h4>Where a brand-new creator should start</h4>
        <ul>
          <li><b>Base:</b> girl-next-door tone (A1) — cheapest to execute, but never alone.</li>
          <li><b>Differentiator:</b> one of alt/goth (A3), country (C1), MILF (D1) or a real physical trait (D2).</li>
          <li><b>Operating model:</b> GFE (B1) — the DM relationship is where retention lives.</li>
          <li><b>Needs something you must already have:</b> glamour (budget), streamer (audience), musician (career), male (physique/hook).</li>
          <li><b>Wrong channel for Instagram:</b> femdom/findom — lives on X and Telegram.</li>
        </ul>
      </div>
      <div class="callout" style="margin-top:16px">
        <h4>The one rule that matters</h4>
        <p style="margin:0">OF creators <em>obscure</em> the commercial relationship (coded highlights, buffered links, "yes I have one ⬇️"); influencers <em>name</em> it (brand, code, coaching CTA). The classifier is a detector of deliberate obscurity plus a funnel. An OF link alone is not enough — SFW-OF athletes exist.</p>
      </div>
    </div>
  </div>
</section>

<section id="niches">
  <p class="eyebrow">02 · Niche explorer</p>
  <div class="rulehead"><h2>Twenty-one niches, six families</h2><span class="count" id="nicheCount"></span></div>
  <div class="toolbar">
    <input class="search" id="q" type="search" placeholder="Search niche, handle, keyword…">
    <span class="sep"></span>
    <span class="chip on" data-fam="all">All families</span>
    __FAM_CHIPS__
    <span class="sep"></span>
    <span class="chip fit-high" data-fit="high">Fit: High</span>
    <span class="chip fit-medium" data-fit="medium">Medium</span>
    <span class="chip fit-low" data-fit="low">Low</span>
    <span class="sep"></span>
    <span class="chip" id="expandAll">Expand all</span>
  </div>
  <div id="nicheHost"></div>
</section>

<section id="matrix">
  <p class="eyebrow">03 · Fit matrix</p>
  <div class="rulehead"><h2>Barrier, saturation, persona load, Instagram risk</h2></div>
  __FIT_TABLE__
  <p class="legend">Green = favourable for a new creator (high fit, low barrier, low saturation, low risk). Red = unfavourable. Grey = neutral or not scaled.</p>
  <p class="lede" style="margin-top:18px">__FIT_READING__</p>
</section>

<section id="provisional">
  <p class="eyebrow">04 · Provisional niches &amp; cross-cutting modifiers</p>
  <div class="rulehead"><h2>Real, but not yet two verified examples</h2></div>
  <p class="lede">These surfaced in research and are included so the taxonomy is complete. They are not equal in maturity to the families above; several are better modelled as a modifier or tone layered onto a host niche.</p>
  __PROV_TABLE__
</section>

<section id="rules">
  <p class="eyebrow">05 · Tagging rules</p>
  <div class="rulehead"><h2>Is this Instagram account OF-branded?</h2><span class="count">rendered from tagging-rules.md</span></div>
  <div class="doc-body">__RULES__</div>
</section>

<section id="audit">
  <p class="eyebrow">06 · Classifier audit</p>
  <div class="rulehead"><h2>The rules, run against every verified profile</h2><span class="count">__N_AUDIT__ profiles · __AUDIT_OK__ fixtures match expected verdict</span></div>
  <p class="lede">Each row is a profile as observed on __VERIFIED__. Click a row to see the matched evidence. <code>S</code> strong · <code>M</code> medium · <code>W</code> weak · <code>X</code> exclude · <code>G</code> gray zone. Include ≥ 3, review = 2, exclude otherwise.</p>
  <div class="toolbar" style="position:static;border:0;padding:8px 0">
    <span class="chip on" data-v="all">All</span>
    <span class="chip" data-v="include">Include</span>
    <span class="chip" data-v="review">Review</span>
    <span class="chip" data-v="exclude">Exclude</span>
    <span class="chip" data-v="unverifiable">Unverifiable</span>
    <span class="sep"></span>
    <span class="chip on" data-b="all">All batches</span>
    __BATCH_CHIPS__
  </div>
  <table class="audit" id="auditTable"><thead><tr><th>Handle</th><th>Batch</th><th>Score</th><th>Verdict</th><th>Signals</th><th>Niche hints</th><th>Expected</th></tr></thead><tbody></tbody></table>
</section>

<section id="method">
  <p class="eyebrow">07 · Method &amp; caveats</p>
  <div class="rulehead"><h2>How this was built</h2></div>
  <ul class="lede">__NOTES__</ul>
  <div class="foot">Sources of truth are the markdown files in the repo; this page is generated from them. Handles, follower counts and highlight names drift — re-verify before acting on any single account.</div>
</section>
</main>

<script>
(function(){const t=localStorage.getItem('dossier-theme')||'dark';document.documentElement.setAttribute('data-theme',t);})();
document.getElementById('themeToggle').addEventListener('click',()=>{const h=document.documentElement;const t=h.getAttribute('data-theme')==='light'?'dark':'light';h.setAttribute('data-theme',t);localStorage.setItem('dossier-theme',t);});
const DATA = __DATA__;
const AUDIT = __AUDIT__;

// ---------- niche cards ----------
const host = document.getElementById('nicheHost');
const state = {fam:'all', fit:null, q:''};
const FIT_ORDER = {high:0, medhigh:1, medium:2, lowmed:3, low:4, mixed:5};
const fitBucket = l => (l==='high'||l==='medhigh') ? 'high' : (l==='medium'||l==='lowmed') ? 'medium' : (l==='low') ? 'low' : 'mixed';

function card(n, idx){
  const f = n.fields;
  const ex = n.examples.map(e=>`<a class="handle" href="https://www.instagram.com/${e.handle}/" target="_blank" rel="noopener" title="${e.size}">@${e.handle}</a>`).join('');
  const exl = n.examples.map(e=>`<li><span class="h">@${e.handle}</span><span class="s">${e.size}</span>${e.signal}</li>`).join('')
            + n.example_notes.map(t=>`<li class="note">${t}</li>`).join('');
  const field = (k,label)=> f[k] ? `<div class="field"><div class="k">${label||k}</div><div class="v">${f[k]}</div></div>` : '';
  return `<article class="card" style="animation-delay:${Math.min(idx*35,420)}ms" data-fam="${n.family}" data-fit="${fitBucket(n.fit_level)}" data-text="${(n.code+' '+n.name+' '+Object.values(f).join(' ')+' '+n.examples.map(e=>e.handle).join(' ')).replace(/<[^>]+>/g,'').toLowerCase().replace(/"/g,'')}">
    <div class="top"><div><div class="code">${n.code} · ${n.family_name}</div><h4>${n.name}</h4></div><span class="pill ${n.fit_level}" title="${n.fit.replace(/"/g,'&quot;')}">${n.fit.length>26 ? n.fit.split(/[\s(—–-]/)[0]+' ·' : n.fit}</span></div>
    <p class="one">${f['One-liner']||''}</p>
    <div class="ex">${ex}</div>
    <details>
      <summary>Full profile</summary>
      <div class="field"><div class="k">New-creator fit — ${n.fit}</div><div class="v">${n.fit_text}</div></div>
      ${field('Visual signature')}${field('Content pillars')}${field('Voice & CTA','Voice &amp; CTA')}${field('Audience')}${field('Hybrids')}
      <div class="field"><div class="k">Verified examples</div><ul class="exlist">${exl}</ul></div>
      ${f["Don't confuse with"] ? `<div class="field confuse"><div class="k">Don't confuse with</div><div class="v">${f["Don't confuse with"]}</div></div>` : ''}
    </details>
  </article>`;
}

function render(){
  let idx=0, shown=0, total=0;
  host.innerHTML = DATA.families.map(fam=>{
    const cards = fam.niches.map(n=>{total++; return card(n, idx++);}).join('');
    return `<div class="family" data-fam="${fam.code}"><span class="code">FAMILY ${fam.code}</span><h3>${fam.name}</h3><span class="ln"></span></div><div class="cards">${cards}</div>`;
  }).join('');
  applyFilters();
}
function applyFilters(){
  let shown=0;
  document.querySelectorAll('#nicheHost .card').forEach(c=>{
    const okFam = state.fam==='all' || c.dataset.fam===state.fam;
    const okFit = !state.fit || c.dataset.fit===state.fit;
    const okQ = !state.q || c.dataset.text.includes(state.q);
    const on = okFam && okFit && okQ;
    c.classList.toggle('hidden', !on); if(on) shown++;
  });
  document.querySelectorAll('#nicheHost .family').forEach(h=>{
    const any = [...h.nextElementSibling.querySelectorAll('.card')].some(c=>!c.classList.contains('hidden'));
    h.style.display = any?'':'none'; h.nextElementSibling.style.display = any?'':'none';
  });
  document.getElementById('nicheCount').textContent = `${shown} of ${document.querySelectorAll('#nicheHost .card').length} niches`;
}
document.querySelectorAll('.toolbar .chip[data-fam]').forEach(ch=>ch.addEventListener('click',()=>{
  document.querySelectorAll('.toolbar .chip[data-fam]').forEach(x=>x.classList.remove('on')); ch.classList.add('on'); state.fam=ch.dataset.fam; applyFilters();
}));
document.querySelectorAll('.toolbar .chip[data-fit]').forEach(ch=>ch.addEventListener('click',()=>{
  const on = ch.classList.contains('on');
  document.querySelectorAll('.toolbar .chip[data-fit]').forEach(x=>x.classList.remove('on'));
  if(!on){ch.classList.add('on'); state.fit=ch.dataset.fit;} else state.fit=null; applyFilters();
}));
document.getElementById('q').addEventListener('input',e=>{state.q=e.target.value.trim().toLowerCase(); applyFilters();});
document.getElementById('expandAll').addEventListener('click',e=>{
  const open = !e.target.classList.contains('on'); e.target.classList.toggle('on', open); e.target.textContent = open?'Collapse all':'Expand all';
  document.querySelectorAll('#nicheHost details').forEach(d=>d.open=open);
});
render();

// ---------- audit ----------
const tb = document.querySelector('#auditTable tbody');
const sigClass = s => s.startsWith('S')?'s':s.startsWith('M')?'m':s.startsWith('W')?'w':'';
const AF={v:'all',b:'all'};
function auditRows(){
  tb.innerHTML = AUDIT.filter(r=>(AF.v==='all'||r.verdict===AF.v)&&(AF.b==='all'||r.batch===AF.b)).map((r,i)=>{
    const sigs = r.signals.map(s=>`<span class="sig ${sigClass(s)}">${s}</span>`).join('')
      + r.excludes.map(s=>`<span class="sig x">!${s}</span>`).join('')
      + r.gray.map(s=>`<span class="sig g">~${s}</span>`).join('');
    const ev = Object.entries(r.evidence).map(([k,v])=>`<div class="kv"><b>${k}</b> ${escapeHtml(v)}</div>`).join('')
      + r.notes.map(n=>`<div class="kv"><b>note</b> ${escapeHtml(n)}</div>`).join('')
      + (r.fixture_note?`<div class="kv"><b>fixture</b> ${escapeHtml(r.fixture_note)}</div>`:'')
      + (r.link_resolves_to?`<div class="kv"><b>link →</b> ${escapeHtml(r.link_resolves_to)}</div>`:'')
      + (r.restricted?`<div class="kv"><b>restricted</b> ${escapeHtml(r.restricted)}</div>`:'')
      + `<div class="kv" style="margin-top:6px;color:var(--ink-3)"><b>bio</b> ${escapeHtml(r.bio||'—')}</div>`
      + `<div class="kv" style="color:var(--ink-3)"><b>highlights</b> ${escapeHtml((r.highlights||[]).join(' · ')||'—')}</div>`
      + `<div class="kv" style="color:var(--ink-3)"><b>links</b> ${escapeHtml((r.links||[]).join(' · ')||'—')}</div>`;
    return `<tr class="row" data-i="${i}"><td><a class="handle" href="https://www.instagram.com/${r.handle}/" target="_blank" rel="noopener" onclick="event.stopPropagation()">@${r.handle}</a>${r.followers?`<div style="font-family:var(--sans);font-size:11px;color:var(--ink-3)">${fmt(r.followers)} followers</div>`:''}</td>
      <td style="font-size:12px;color:var(--muted)">${r.batch}</td>
      <td><span class="score">${r.score}</span><span class="bar"><i style="width:${r.score*20}%"></i></span></td>
      <td><span class="pill ${r.verdict}">${r.verdict}</span></td>
      <td>${sigs||'<span class="sig">—</span>'}</td>
      <td style="font-family:var(--sans);font-size:12.5px;color:var(--ink-2)">${r.niches.map(n=>n.split(':')[1]).join(', ')||'—'}</td>
      <td>${r.expected.length?`<span class="${r.ok?'ok':'bad'}">${r.ok?'✓':'✗'}</span> <span style="font-size:12px;color:var(--muted)">${r.expected.join(' / ')}</span>`:'<span style="color:var(--muted-2)">— prospect</span>'}</td></tr>
      <tr class="detail" style="display:none"><td colspan="7">${ev}</td></tr>`;
  }).join('');
  tb.querySelectorAll('tr.row').forEach(tr=>tr.addEventListener('click',()=>{const d=tr.nextElementSibling; d.style.display = d.style.display==='none'?'':'none';}));
}
function fmt(n){return n>=1e6?(n/1e6).toFixed(1).replace(/\.0$/,'')+'M':n>=1e3?(n/1e3).toFixed(n<10000?1:0).replace(/\.0$/,'')+'K':String(n);}
function escapeHtml(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
document.querySelectorAll('#audit .chip[data-v]').forEach(ch=>ch.addEventListener('click',()=>{
  document.querySelectorAll('#audit .chip[data-v]').forEach(x=>x.classList.remove('on')); ch.classList.add('on'); AF.v=ch.dataset.v; auditRows();
}));
document.querySelectorAll('#audit .chip[data-b]').forEach(ch=>ch.addEventListener('click',()=>{
  document.querySelectorAll('#audit .chip[data-b]').forEach(x=>x.classList.remove('on')); ch.classList.add('on'); AF.b=ch.dataset.b; auditRows();
}));
auditRows();

// ---------- rail highlight ----------
const links=[...document.querySelectorAll('.rail nav a')];
const io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){links.forEach(l=>l.classList.toggle('active',l.getAttribute('href')==='#'+e.target.id));}})},{rootMargin:'-20% 0px -70% 0px'});
document.querySelectorAll('main section').forEach(s=>io.observe(s));
</script>
</body>
</html>
"""

# --------------------------------------------------------------------------- #
# Fit matrix colouring
# --------------------------------------------------------------------------- #

def cell_class(col: str, val: str) -> str:
    v = val.lower().replace("**", "")
    good = {"fit": ["high"], "barrier": ["very low", "low"], "saturation": ["very low", "low"],
            "persona": ["none", "low"], "risk": ["low"]}
    bad = {"fit": ["low"], "barrier": ["high", "very high"], "saturation": ["high", "very high"],
           "persona": ["high", "very high"], "risk": ["high", "very high"]}
    key = ("fit" if "fit" in col else "barrier" if "barrier" in col else "saturation" if "saturation" in col
           else "persona" if "persona" in col else "risk" if "risk" in col else None)
    if not key:
        return ""
    first = re.split(r"[\s(–-]", v.strip())[0] if key == "fit" else v.strip()
    if key == "fit":
        if v.startswith("high"):
            return "c-g"
        if v.startswith("low"):
            return "c-r"
        if v.startswith("med"):
            return "c-y"
        return "c-n"
    if any(v.startswith(g) for g in good[key]):
        return "c-g"
    if any(v.startswith(b) for b in bad[key]):
        return "c-r"
    if v.startswith("med"):
        return "c-y"
    return "c-n"


def fit_table(fm: dict) -> str:
    h = fm["header"]
    out = ['<table class="fitm"><thead><tr>' + "".join(f"<th>{inline(x)}</th>" for x in h) + "</tr></thead><tbody>"]
    for r in fm["rows"]:
        tds = []
        for j, c in enumerate(r):
            col = h[j].lower() if j < len(h) else ""
            cls = cell_class(col, c)
            txt = inline(c)
            tds.append(f'<td><span class="cell {cls}">{txt}</span></td>' if cls else f"<td>{txt}</td>")
        out.append("<tr>" + "".join(tds) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #

def main() -> None:
    niches_md = open(os.path.join(ROOT, "niches.md"), encoding="utf-8").read()
    rules_md = open(os.path.join(ROOT, "tagging-rules.md"), encoding="utf-8").read()
    data = parse_niches(niches_md)
    rows = audit()

    # rules: drop the H1 (dashboard has its own) and shift headings under the section
    rules_body = re.sub(r"^# .*\n", "", rules_md, count=1)
    rules_html = md_to_html(rules_body, heading_shift=0)

    n_niches = sum(len(f["niches"]) for f in data["families"])
    n_examples = len({e["handle"] for f in data["families"] for n in f["niches"] for e in n["examples"]})
    batches = list(dict.fromkeys(r["batch"] for r in rows))
    batch_chips = "".join(f'<span class="chip" data-b="{b}">{html.escape(b)}</span>' for b in batches)
    fam_chips = "".join(f'<span class="chip" data-fam="{f["code"]}">{f["code"]} · {html.escape(f["name"])}</span>' for f in data["families"])

    css = open(os.path.join(ROOT, "dashboard", "theme.css"), encoding="utf-8").read()
    logo_path = os.path.join(ROOT, "dashboard", "brand", "logo.svg")
    logo = open(logo_path, encoding="utf-8").read() if os.path.exists(logo_path) else FALLBACK_LOGO
    logo = re.sub(r"<svg\b", '<svg class="mark"', logo, count=1)
    page = (TEMPLATE
            .replace("__CSS__", css)
            .replace("__LOGO__", logo)
            .replace("__VERIFIED__", data["verified_date"] or "—")
            .replace("__BUILT__", date.today().isoformat())
            .replace("__N_NICHES__", str(n_niches))
            .replace("__N_FAMILIES__", str(len(data["families"])))
            .replace("__N_EXAMPLES__", str(n_examples))
            .replace("__N_PROV__", str(len(data["provisional"]["rows"])))
            .replace("__N_AUDIT__", str(len(rows)))
            .replace("__N_PROSPECTS__", str(sum(1 for r in rows if r["batch"] != "fixtures")))
            .replace("__AUDIT_OK__", str(sum(1 for r in rows if r["expected"] and r["ok"])))
            .replace("__INTRO__", "".join(f"<p>{p}</p>" for p in data["intro"]))
            .replace("__FAM_CHIPS__", fam_chips)
            .replace("__BATCH_CHIPS__", batch_chips)
            .replace("__FIT_TABLE__", fit_table(data["fit_matrix"]))
            .replace("__FIT_READING__", data["fit_matrix"]["reading"])
            .replace("__PROV_TABLE__", table_html(data["provisional"]["header"], data["provisional"]["rows"], "doc prov"))
            .replace("__RULES__", rules_html)
            .replace("__NOTES__", "".join(f"<li>{n}</li>" for n in data["notes"]))
            .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
            .replace("__AUDIT__", json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")))

    out = os.path.join(ROOT, "dashboard", "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {os.path.relpath(out, ROOT)}  ({len(page)//1024} KB) — {n_niches} niches, {n_examples} handles, {len(rows)} audit rows")


if __name__ == "__main__":
    main()
