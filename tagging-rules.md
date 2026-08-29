# Tagging rules — is this Instagram account OF-branded?

Companion to [`niches.md`](niches.md). Goal: decide, from the Instagram profile alone (bio, link, highlights, category label, pinned posts), whether an account is branded as an OnlyFans/Fansly/Fanvue creator — and specifically to **exclude fitness models and general influencers who are not**. Every rule below was derived from signals actually observed on live profiles on 2026-08-26; examples are cited so the rule can be re-checked.

Principle: **OF creators obscure the commercial relationship (euphemism, coded highlights, buffered links) because naming it risks enforcement; influencers name it (brand, code, coaching CTA) because it's compliant.** The classifier is mostly a detector of *deliberate obscurity + a funnel*.

---

## 1. Include signals

### Strong (any one is sufficient)

| # | Signal | Observed on |
|---|---|---|
| S1 | Highlight literally named "OnlyFans" / "O.F." / "OF" (often with 😈) | `@stonergirldaily`, `@dailystonergirl`, `@countrygirl_nat` ("O.F.😈"), `@its.lucy.bb` |
| S2 | Bio CTA that says there *is* a hidden page without naming it: "Yes I have one 🌶⬇️", "↓YES, I have one↓", "Check below for more! 👇", "⤵️ See alot more of me here", "Highlights for more 😜", "Check my highlight ⬇️📎", "I also do other things… but that's for you to find on your own", "Want to see more of me? check out my link below" | `@countrygirl_nat`, `@spicycowgirlofficial_`, `@cierra_mistt_`, `@mommypaigexo`, `@katie_k_beach__`, `@peytonkinsly`, `@peachjars`, `@its.lucy.bb` |
| S3 | Adult-industry affiliation stated in bio/highlights: studio ambassador/contract ("@blackedxofficial Ambassador", "ZZ contract"), "AVN", "Male Performer", "Adult Content Creator", "18+NSFW", "Exotic Dancer", "camgirl", fan-platform founder ("@fanlockcom cofounder") | `@iamjasonluv`, `@girthmasterr`, `@maxkfit_backup`, `@its.lucy.bb`, `@bigguswombus` |
| S4 | Explicit backup/alt-account structure: "this is my BACKUP account", "Official backup page for @…", "Backup account is @…", "Main acct @…", "go to @x_ for more", "Exclusive @…", "MAIN PAGE" + "2ND/3RD Instagram", "@handle on everything" | `@dailystonergirl`, `@maxkfit_backup`, `@fullmetalifrit`, `@spicycowgirlofficial_`, `@cierra_mistt`, `@_li.si_`, `@therealbarbiede`, `@gothravemommy` |
| S5 | Zero-/one-post "pointer" account whose only content is a link or a handle: "Check below for more 👇 + link", "Get to know me? @…", "🔥Exclusive content🔥 + link" | `@cierra_mistt_`, `@aliyaroseofc`, `@exclusive_lisi` |
| S6 | Pun or in-joke naming the platform: "Only brother", podcast "OnlyFeehans" | `@yetifit__`, `@kerrynfeehan` |
| S7 | **Instagram age-gates the profile for logged-out viewers** ("You must be 18 years old or over to see this profile") — a platform-assigned adult flag, visible without logging in | `@amber_hazee`, `@guadadia` (prospect batch 01) |

### Medium (two of these, or one plus any Weak, is sufficient)

| # | Signal | Observed on |
|---|---|---|
| M1 | Highlight named with a coded CTA: "VIP" / "VIP Access" / "💙VIP💙", "EXCLUSIVE 🚨", "🌶️", "👀", "🔗", "More 📎", "Click here :)", "Here ☝️", "Find me", "Check here!!!", "Links", "Important", "Important Info!", "Verification" | `@bigguswombus`, `@katie_k_beach__`, `@salicerose`, `@sydneylint`, `@peachjars`, `@girthmasterr`, `@peytonkinsly`, `@momycarterx`, `@elainastjames`, `@viktoria_winslow`, `@theanyamatusevich`, `@giagotham`, `@spicytattoodoll`, `@ubeayork` |
| M2 | Link tool commonly used to front adult links: **link.me**, **AllMyLinks** / **GetAllMyLinks**, **Beacons**, **hoo.be**, **onlylinks.com**, **bonafide.us**, **Supalink** (custom `.vip`/`.fit` domains that redirect to `supalink.ai` — landing copy like "Your dream girl… What you're looking for 🤍🩵" / "Chat with me" is an adult funnel and counts as a confirmed tile), **Linktree whose page title is "<name> OnlyFans Official – Exclusive Content & Account"** (Linktree auto-titles pages this way when an OF tile exists — fetch the page to confirm) | link.me: `@spicycowgirlofficial_`, `@_li.si_`, `@victoriastwitch`, `@petitelilpeach`; AllMyLinks: `@gothravemommy`; Beacons: `@giagotham`, `@curvybaddie18`; hoo.be: `@therealbarbiede`; onlylinks: `@cierra_mistt_`; Linktree-OF-title: `@countrygirl_nat`, `@stonergirldaily`, `@brittymigs`, `@kerrynfeehan`, `@julietinthewild`, `@katie_k_beach__` |
| M3 | Custom-domain buffer link that is clearly personal, not a business site: `firstname.business`, `handle.com`, `yummy<name>.com`, `<name>.vip`, `<name>sadventures.com/welcome` | `@theanyamatusevich`, `@spicytattoodoll`, `@gothpixi`, `@mommypaigexo`, `@iamjasonluv`, `@lilliluxe` |
| M4 | "Content Creator" / "Digital creator" self-label **combined with** an emoji set from {🌶️ 🍑 🔞 😈 👀 💦 🥵} or the word "spicy"/"exclusive" | `@katie_k_beach__` ("Content Creator 🇦🇺👙 … 😜💋"), `@countrygirl_nat` ("Spicy country girl 💦") |
| M5 | "TOP %" / "Top 1%" / "Top 0.x%" boast in bio (OF creator-ranking language) | `@spicycowgirlofficial_`, `@countrybadasstay`, `@countrygirl_nat` |
| M6 | Wishlist / "Spoil me" / Throne / Telegram highlight or link with no other commercial explanation | `@thesilviasaige` ("Wishlist"), `@julietinthewild` ("Wishlist ❤️"), `@momycarterx` ("Telegram 🤍") |
| M7 | "NO DMS HERE ❌", "NO MEETUPS", "No DMs — use the link" (deflecting DMs to the paid channel) | `@curvybaddie18`, `@its.lucy.bb` |
| M8 | Instagram shows "Restricted profile — unavailable for certain audiences" to logged-out viewers (softer than the 18+ gate; also applied for other policy reasons) | `@shaynaholt`, `@lilia.angelx` (prospect batch 01) |

### Weak (supporting only — never sufficient alone)

| # | Signal | Note |
|---|---|---|
| W1 | "Followed by wearenudepr" (or another OF PR/management agency) visible in the social-proof line | Seen on `@cierra_mistt`, `@thesilviasaige`, `@lilliluxe`, `@leynainu`, `@elainastjames`, `@fullmetalifrit`, `@spicytattoodoll`. Useful for discovery; agencies also follow prospects. |
| W2 | Appears in an OF-creator listicle (Village Voice, Instinct, Pippin Club, OnlyMonster) | ~50% of listicle handles were dead or wrong on IG; confirm on-profile. |
| W3 | Cosplay/con/Twitch/Discord highlight stack with a catch-all "follow me everywhere ⬇️" | `@jennalynnmeowri` — platform-hopping funnel, adult tile is on the aggregator. |
| W4 | Handle contains a niche/trait keyword + "xo", "official", trailing underscore, numbers, or doubled letters (moderation-survival handle drift) | `@spicycowgirlofficial_`, `@momycarterx`, `@kimbothebimbo.xiii` |
| W5 | Press coverage naming the person as an OF creator | Confirms the *person*; does **not** confirm the *IG account is branded* (see gray zone G1). |

---

## 2. Exclude signals (fitness / brand-deal / general influencer)

These indicate a compliant commercial model and, **absent any Strong or Medium include signal**, tag the account as *not OF-branded*.

| # | Signal | Observed on (controls) |
|---|---|---|
| X1 | Coaching CTA: "ONLINE COACH", "Apply for Online Coaching ⬇️", "Programs", "1000+ lives changed", transformation highlights | `@hannahbarryuk` (241K) |
| X2 | Brand founder/exec role in bio: "Co Founder, Creative Director @oneractive", "Founder @WeRise App", "Owner of @thelintlabel" | `@krissycela` (3.2M), `@senada.greca` (6.8M) — note `@sydneylint` has an owner tag *and* a 🌶️ highlight, so X3 never overrides an include signal |
| X3 | Sponsor/partner tag list or "Athlete" category with product links: "@rad_global @reignbodyfuel @yeti…", supplement "Team @…" | `@daniellebrandon7` (842K); `@countrybadasstay` carries "Team @cbgnutrition" *and* is the clean main of an OF alt — see G2 |
| X4 | Discount code in bio ("code HANNAHB"), LTK / Amazon storefront / "Revolve Links" / "shop my looks" | `@kiera.bernier` ("Revolve Links"), general fitness-influencer pattern |
| X5 | Booking/business email as the only CTA; management/agency tags (`@bmg.models`, `Manager: @…`) with no adult reference | `@maxkfit_` main, `@salicerose` (business email; celebrity) |
| X6 | Streamer/creator label with a Linktree that contains **no** adult tile | `@mk_egirl`, `@lillytino_` |
| X7 | Category label "Athlete", "Coach", "Entrepreneur", "Public figure", "Reel creator" with a fully mainstream bio and no coded highlight | `@daniellebrandon7`, `@krissycela` |

Reminder: an exclude signal is *not* a veto. Several OF creators carry brand deals (`@sydneylint` + FashionNova; `@stonergirldaily` + glass-brand discount codes). Include signals win.

---

## 3. Gray zones and how to resolve them

| # | Case | Rule | Example |
|---|---|---|---|
| G1 | **Sanitized main of a known OF creator** — press/OF confirms the person, IG shows nothing | Tag the *account* as **not OF-branded**; tag the *person* as OF-creator only if a paired spicy alt (S4/S5) can be found. For an IG classifier this is the correct "negative". | `@kiera.bernier` (Maxim/of.tv confirm OF; IG = recipes, equestrian, Revolve) |
| G2 | **Dual-identity pair** — clean main + spicy alt cross-referencing each other | Tag *both*: main = "OF-creator (clean main)", alt = "OF-branded". The cross-reference is the S4 signal. | `@countrybadasstay` ↔ `@spicycowgirlofficial_`; `@_li.si_` ↔ `@exclusive_lisi`; `@maxkfit_` ↔ `@maxkfit_backup`; `@fullmetalifrit` ↔ `@bikini.ifrit`; `@cierra_mistt` ↔ `@cierra_mistt_` |
| G3 | **OF link present but content is SFW** (athletes, musicians, coaches on OF) | Require an OF link **plus** an adult-coded CTA/highlight (S2, M1, M4). OF-athlete branding ("@onlyfans Athlete", "OFAthlete 🏄") without adult coding → **exclude**. | `@moana.17` (pro surfer, 190K); `@justliketrevor` (yoga coach, Linktree says "OnlyFans (21+ only)" — borderline; his IG has no adult coding → exclude from IG-branded set, note as OF-person) |
| G4 | **Studio, aggregator or fan-page accounts** | Exclude. Tells: "Official Instagram for your favorites!", "ur girlfriend follows us", hashtag-collector bios, many different women in the grid, "vote for your favourites". | `@officialbrattymilf` (porn studio), `@1nternet.gf` (aggregator), `@latinhunk`, `@hotmoms_club` |
| G5 | **Pro-domme / escort / booking pages** | Exclude from the OF-creator set even though adult: tells are "Bookings", "Call me / Text me", Slixa/P411/Eros, "no OF link", "This is my only account". | `@cleoouyang` ("LA Dominatrix… bookings"), Linktree `salmaxo.gfe` ("Professional Girlfriend… Booking") |
| G6 | **Celebrity-added-OF** (mega accounts with a business email and one "EXCLUSIVE 🚨" highlight) | Include only if a Strong/Medium signal exists; flag as "celebrity tier" so they don't skew new-creator matching. | `@salicerose` (18.8M) |
| G7 | **Patreon / Fansly / Fanvue / LoyalFans / MYM instead of OnlyFans** | In scope — "OF space" means any adult fan-subscription platform. Patreon alone is ambiguous (SFW cosplay is common) → require an adult-coded CTA. | `@victoriastwitch` (Fansly + LoyalFans), `@julietinthewild` (Patreon + Playboy + Throne) |
| G8 | **Dead / renamed / private handle** | Tag "unverifiable"; do not carry over a previous tag. Roughly half of listicle-sourced handles were dead on the check date. | `@minki_minna_`, `@charlieeerose3`, `@leolulu.official`, `@goth__egg` … |

### Decision tree (30-second version)

1. Is it a studio/aggregator/fan page (G4) or a booking page (G5)? → **Exclude.**
2. Any **Strong** signal (S1–S6)? → **Include.**
3. Two **Medium** signals, or one Medium + one Weak? → **Include.**
4. Exactly one Medium and nothing else? → Open the link tool / follow the pointer handle (G2). Adult tile found → **Include**; not found → **Unclear**.
5. Only Exclude signals (X1–X7)? → **Exclude.**
6. OF link but SFW branding (G3)? → **Exclude** (note as "OF-person, not IG-branded").
7. Nothing at all? → **Not OF-branded** (may still be a sanitized main — G1).

---

## 4. Quick score (0–5)

| Score | Meaning | Rule |
|---|---|---|
| 5 | Explicit | S1 or S3 |
| 4 | Coded but unambiguous | S2, S4, S5, S6 or S7 |
| 3 | Funnel evident | ≥2 Medium, or 1 Medium + 1 Weak |
| 2 | Suggestive | exactly 1 Medium |
| 1 | Hint only | Weak signals only |
| 0 | None / excluded | no include signals, or G3/G4/G5 applies |

Threshold for "OF-branded": **≥3**. Threshold for "review manually": 2. Report the score *and* the highest-tier signal so reviewers can audit quickly.

---

## 5. Cross-check against the verified set

Applying the rules to every example in `niches.md` and to the control set. ✔ = classifier output matches ground truth.

**Should INCLUDE (OF-branded on IG)**

| Handle | Top signal | Score | Result |
|---|---|---|---|
| `@stonergirldaily` | S1 | 5 | ✔ |
| `@countrygirl_nat` | S1/S2 | 5 | ✔ |
| `@its.lucy.bb` | S1/S3 | 5 | ✔ |
| `@iamjasonluv` | S3 | 5 | ✔ |
| `@girthmasterr` | S3 | 5 | ✔ |
| `@bigguswombus` | S3 + M1 | 5 | ✔ |
| `@maxkfit_backup` | S3/S4 | 5 | ✔ |
| `@spicycowgirlofficial_` | S2/S4 | 4 | ✔ |
| `@cierra_mistt_` | S2/S5 | 4 | ✔ |
| `@exclusive_lisi` | S5 | 4 | ✔ |
| `@aliyaroseofc` | S5 | 4 | ✔ |
| `@dailystonergirl` | S1/S4 | 5 | ✔ |
| `@fullmetalifrit` | S4 | 4 | ✔ |
| `@therealbarbiede` | S4 + M2 | 4 | ✔ |
| `@gothravemommy` | S4 + M2 | 4 | ✔ |
| `@yetifit__` | S6 | 4 | ✔ |
| `@kerrynfeehan` | S6 + M2 | 4 | ✔ |
| `@peachjars` | S2 + M1 | 4 | ✔ |
| `@mommypaigexo` | S2 + M3 | 4 | ✔ |
| `@katie_k_beach__` | S2 + M1 + M4 | 4 | ✔ |
| `@peytonkinsly` | S2 + M1 + M2 | 4 | ✔ |
| `@momycarterx` | M1 + M6 | 3 | ✔ |
| `@elainastjames` | M1 + W1 + W5 | 3 | ✔ |
| `@viktoria_winslow` | M1 + W5 | 3 | ✔ |
| `@theanyamatusevich` | M1 + M3 | 3 | ✔ |
| `@sydneylint` | M1 ("🌶️") + W2 | 3 | ✔ (despite X2 owner tag) |
| `@giagotham` | M1 + M2 | 3 | ✔ |
| `@spicytattoodoll` | M1 + M3 | 3 | ✔ |
| `@gothpixi` | M3 + W2 | 3 | ✔ |
| `@petitelilpeach` | M2 + M1 ("reviews") | 3 | ✔ |
| `@curvybaddie18` | M2 + M4 + M7 | 3 | ✔ |
| `@victoriastwitch` | M2 + Linktree adult tiles | 3 | ✔ |
| `@brittymigs` | M2 (Linktree OF title) + W2 | 3 | ✔ |
| `@julietinthewild` | M2 + M6 | 3 | ✔ |
| `@lilliluxe` | M3 + W1 + W2 | 3 | ✔ |
| `@jennalynnmeowri` | W3 + M1 ("MY SOCIALS") + W2 | 3 | ✔ |
| `@thesilviasaige` | M6 + W1 + W2 | 3 | ✔ |
| `@carlottachampagne` | W2 + W1 | 2 | ⚠ review — IG alone is weak; kept in playbook as pin-up example on listicle + aesthetic |
| `@thejessiesims` | M1 ("Socials 💕") + W2 | 2–3 | ⚠ borderline |
| `@lovelyeviexoxo` | W2 only | 1 | ⚠ IG alone doesn't qualify; kept as trans-niche example with caveat |
| `@owlsgaze` | M2 (Linktree OF title) | 2 | ⚠ review |
| `@leonardooliveraok` | M2 (Linktree "JovenTwinkOk") + W2 | 3 | ✔ |
| `@cierra_mistt` | S4 (pointer to alt) | 4 | ✔ (tag: clean main) |
| `@countrybadasstay`, `@_li.si_`, `@maxkfit_` | S4 (cross-ref to alt) | 4 | ✔ (tag: clean main) |

**Should EXCLUDE (controls)**

| Handle | Signals | Score | Result |
|---|---|---|---|
| `@hannahbarryuk` | X1, X4 | 0 | ✔ |
| `@krissycela` | X2, X7 | 0 | ✔ |
| `@daniellebrandon7` | X3, X7 | 0 | ✔ |
| `@senada.greca` | X2 | 0 | ✔ |
| `@mk_egirl` | X6 | 0 | ✔ |
| `@lillytino_` | X6 | 0 | ✔ |
| `@moana.17` | OF link, SFW → G3 | 0 | ✔ |
| `@kiera.bernier` | X4; OF person → G1 | 0 | ✔ (correct IG-only negative) |
| `@officialbrattymilf` | G4 studio | 0 | ✔ |
| `@1nternet.gf` | G4 aggregator | 0 | ✔ |
| `@cleoouyang` | G5 | 0 | ✔ |
| `@justliketrevor` | G3 borderline | 0–1 | ✔ (excluded; flag as OF-person) |
| `@connerbobay` | none | 0 | ✔ (listicle claimed OF; IG shows "Husband · Father · Jesus", no funnel — correct negative) |
| `@noelle_best` | none | 0 | ✔ (listicle claimed OF; nothing on IG) |

### Prospect batch 01 (12 real prospects, collected logged-out on 2026-08-28)

| Handle | Result | What decided it |
|---|---|---|
| `@amber_hazee`, `@guadadia` | **include** (4) | Instagram 18+ age-gate on the profile (S7) — nothing else visible logged-out |
| `@shaynaholt`, `@lilia.angelx` | review (2) | "Restricted profile — unavailable for certain audiences" (M8); needs a logged-in look |
| `@valebragg`, `@jane.mautin` | **include** (3) | `.vip` domain → Supalink landing: "Your dream girl… What you're looking for 🤍🩵" (M2 + M3) |
| `@lizakovalenkoo` | **include** (3) | IG reads "Fashion / Lifestyle · @revolve ambassador" (X3, X4) but `lizaswrld.com` → Supalink "Your dream girl 🖤 Chat with me" — include overrides exclude; resolved via decision-tree step 4 |
| `@4mbuh` | **include** (3) | `4mbuh.com` → GetAllMyLinks "MORE OF ME" → `onlyfans.com/ambzy`; "👀" highlight, Twitch/Discord stack |
| `@alarahbelle` | **include** (3) | `alarah.link` shows an 18+ "Sensitive Content" gate before the tiles (the gate is the tell); bio carries a supplement discount code (X4) — overridden |
| `@anllela_sagra` | **include** (3, celebrity tier) | "Exclusive" highlight + `.fit` domain → Supalink "Explore More 💕😉"; 26.7M followers → G6 flag |
| `@hcoxofficial` | exclude (1) | "Chevy Girl 🐾 Bulldog Momma", no link, no highlights — nothing to act on |
| `@lalovetheboss` | exclude (0) | Artist/actress, music smart-link, management email — musician, not OF-branded |

**What this batch taught the rules**
- **Instagram's own logged-out gates are the strongest cheap signal**: an 18+ age-gate (S7) or "certain audiences" restriction (M8) is platform-assigned and visible without logging in. Four of twelve prospects carried one.
- **Supalink** (`supalink.ai`, usually behind a vanity `.vip` / `.fit` / `.com`) is an OF-funnel landing tool; its GFE copy ("Your dream girl", "What you're looking for", "Chat with me") is as good as an OF tile. Added to M2.
- **Resolve the link before deciding.** Five of the seven includes were only decidable by opening the bio link — the profile alone scored 2. The collector now records what each link resolves to.

**Misfires observed and how the rules were adjusted**
- Listicle presence alone (W2) produced several false positives (`@connerbobay`, `@noelle_best`, `@gabbyepstein`) → W2 demoted to Weak, never sufficient.
- "Has an OF link" alone would have included `@moana.17` → G3 added (OF link must be paired with adult-coded CTA).
- Brand/owner tags would have excluded `@sydneylint` and `@countrybadasstay` → exclude signals made non-vetoing; S4 cross-reference resolves the latter.
- Aggregator/studio accounts (`@officialbrattymilf`, `@1nternet.gf`) score high on surface keywords → G4 placed *first* in the decision tree.

---

## 6. Practical notes for a reviewer

- Always open the link tool or pointer handle when the score is 2; that step converts most "unclear" cases (Linktree pages are readable without login and are auto-titled "… OnlyFans Official" when an OF tile exists; Beacons pages are not fetchable — go to IG with the same handle and expect a ~50% miss).
- Highlight *names* are the single richest on-profile signal; read them before the bio.
- Handles drift for moderation reasons (extra underscore, `.xiii`, doubled letters). When a handle is dead, search the display name on the Linktree/Beacons page rather than guessing.
- Re-check tool-policy claims before publishing (whether Linktree tolerates adult tiles, whether "0nlyfans" spellings are penalised) — research sources contradicted each other and all were commercial.
