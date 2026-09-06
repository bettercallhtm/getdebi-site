# Debi Site Copy Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild Debi's static website around a warm, money-first sales narrative, shorten the FAQ, and make the desktop/mobile product relationship visible with real app imagery.

**Architecture:** Keep the existing dependency-free single-page static site and hash router. Add standard-library contract tests around routes, copy constraints, FAQ length, image accessibility, and unsupported claims; then replace the existing page copy and selected layouts without introducing a framework.

**Tech Stack:** HTML5, CSS, vanilla JavaScript, Python 3 standard-library `unittest`

**Spec:** `docs/superpowers/specs/2026-09-06-debi-site-copy-and-report-redesign-design.md`

## Global Constraints

- The site remains dependency-free and build-free.
- No analytics, tracking, or new third-party runtime dependency is added.
- Lead with financial loss and business outcome; move mechanisms later.
- Use "İlk ay ücretsiz; ilk 7 gün yalnızca ölçüm" consistently.
- Do not promise zero penalties, guaranteed profit, or that every restaurant is penalized every month.
- Keep the phone app read-only: decisions happen on the restaurant computer.
- FAQ contains at most 10 questions.
- Do not push; show the finished local site to the user first.

---

### Task 1: Add static-site content contracts

**Files:**
- Create: `tests/test_site.py`
- Test: `tests/test_site.py`

**Interfaces:**
- Consumes: `index.html` and local image paths.
- Produces: `python -m unittest tests.test_site -v` as the site regression command.

- [ ] **Step 1: Write tests that describe the approved structure**

Create `tests/test_site.py` with standard-library tests that load `index.html` and assert:

```python
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")


class SiteContracts(unittest.TestCase):
    def test_money_first_message_and_platforms_are_visible(self):
        self.assertIn("Yoğun saatlerin cezası kârınızdan çıkmasın", HTML)
        for name in ("Trendyol Go", "GetirYemek", "Yemeksepeti"):
            self.assertIn(name, HTML)

    def test_trial_language_is_consistent(self):
        self.assertIn("İlk ay ücretsiz", HTML)
        self.assertIn("ilk 7 gün yalnızca ölç", HTML.lower())

    def test_faq_has_at_most_ten_questions(self):
        faq = re.search(
            r'<section class="page" data-page="/sss">(.*?)</section>',
            HTML,
            re.S,
        ).group(1)
        self.assertLessEqual(len(re.findall(r"<details>", faq)), 10)

    def test_unsupported_guarantees_are_absent(self):
        lowered = HTML.lower()
        for claim in ("cezaları sıfırlar", "kesin kazanç", "her ay mutlaka ceza"):
            self.assertNotIn(claim, lowered)

    def test_mobile_images_exist_and_have_alt_text(self):
        sources = re.findall(r'<img[^>]+src="([^"]*mobil-[^"]+)"[^>]+alt="([^"]+)"', HTML)
        self.assertTrue(sources)
        for src, alt in sources:
            self.assertTrue((ROOT / src).is_file(), src)
            self.assertTrue(alt.strip())
```

- [ ] **Step 2: Run tests and verify they fail for the old site**

Run: `python -m unittest tests.test_site -v`

Expected: failures for the new hero sentence, FAQ count, and missing mobile imagery.

- [ ] **Step 3: Commit the failing content contracts**

```bash
git add tests/test_site.py
git commit -m "test: define Debi site content contracts"
```

### Task 2: Rebuild the home page and navigation

**Files:**
- Modify: `index.html:31-710`
- Create: `mobil-optimizasyon.png`
- Create: `mobil-olaylar.png`
- Test: `tests/test_site.py`

**Interfaces:**
- Consumes: existing hash-router page objects and images from `C:\Users\Dell\debi-mobil\magaza-gorselleri`.
- Produces: a revised home page using the existing `.page` router contract and two local mobile assets.

- [ ] **Step 1: Copy the approved mobile screenshots**

Copy without altering source files:

```text
C:\Users\Dell\debi-mobil\magaza-gorselleri\01-optimizasyon.png -> mobil-optimizasyon.png
C:\Users\Dell\debi-mobil\magaza-gorselleri\04-olaylar.png -> mobil-olaylar.png
```

- [ ] **Step 2: Replace the home-page content in `index.html`**

Keep `data-page="/"` and use this content order:

1. Hero: "Yoğun saatlerin cezası kârınızdan çıkmasın."
2. Support copy naming Trendyol Go, GetirYemek, and Yemeksepeti.
3. CTA "1 ay ücretsiz deneyin" plus note "İlk 7 gün yalnızca ölçüm."
4. Three steps titled "Siparişleri tek yükte görür", "Yoğunluğu erken yakalar", and "Yük düşünce normale döner".
5. A money-loss block covering late orders, cancellations/refunds, and stores left closed.
6. A desktop/phone block titled "Karar bilgisayarda, durum telefonda" with the two real screenshots and explicit read-only sentence.
7. A compact compatibility summary linking to `#/platformlar`.
8. A four-stage first-month sequence: 7-day measurement, report, threshold approval, optional live mode.
9. A compact privacy/safety proof linking to `#/guvenlik`.
10. Example-report CTA and final trial CTA.

Remove the old long “Ceza nereden geliyor” narrative and the phone app's store-status text. Preserve the current contact form target and theme behavior.

- [ ] **Step 3: Add responsive CSS for the new sections**

Add focused classes for:

```css
.hero-proof { display:grid; gap:24px; align-items:center; }
.outcome-grid { display:grid; gap:12px; }
.product-pair { display:grid; gap:24px; align-items:center; }
.phone-shots { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }
.phone-shots img { width:100%; height:auto; border-radius:18px; border:1px solid var(--line); }
@media (min-width:820px) {
  .hero-proof,.product-pair { grid-template-columns:minmax(0,1.05fr) minmax(280px,.95fr); }
  .outcome-grid { grid-template-columns:repeat(3,1fr); }
}
```

Use existing color tokens and typography. Ensure screenshots never force horizontal scrolling.

- [ ] **Step 4: Simplify the page list and preserve old routes**

Keep visible navigation entries for `/nasil-calisir`, `/platformlar`, `/guvenlik`, and `/sss`, plus the trial CTA. Hide `/neden` and `/iletisim` from top navigation while keeping their URLs reachable until redirect behavior is verified. Add explicit router aliases only if removing their sections:

```javascript
const aliases = { "/neden": "/", "/iletisim": "/deneme" };
path = aliases[path] || path;
```

- [ ] **Step 5: Run the content contracts**

Run: `python -m unittest tests.test_site -v`

Expected: all Task 1 tests pass except any FAQ-specific test pending Task 3.

- [ ] **Step 6: Commit the home-page redesign**

```bash
git add index.html mobil-optimizasyon.png mobil-olaylar.png tests/test_site.py
git commit -m "feat: rebuild Debi home page around restaurant outcomes"
```

### Task 3: Rewrite supporting pages and shorten the FAQ

**Files:**
- Modify: `index.html:482-1380`
- Modify: `tests/test_site.py`

**Interfaces:**
- Consumes: the approved voice and information architecture in the spec.
- Produces: concise pages at the existing `/nasil-calisir`, `/platformlar`, `/guvenlik`, `/sss`, and `/deneme` routes.

- [ ] **Step 1: Add route and terminology assertions**

Extend `tests/test_site.py`:

```python
    def test_required_pages_remain_available(self):
        for path in ("/", "/nasil-calisir", "/platformlar", "/guvenlik", "/sss", "/deneme"):
            self.assertIn(f'data-page="{path}"', HTML)

    def test_phone_responsibility_is_unambiguous(self):
        self.assertIn("Karar bilgisayarda, durum telefonda", HTML)
        self.assertRegex(HTML, r"Telefon[^<]{0,160}(yalnızca|sadece)[^<]{0,80}(izler|gösterir)")
```

- [ ] **Step 2: Run the new tests and confirm the responsibility test fails**

Run: `python -m unittest tests.test_site.SiteContracts.test_phone_responsibility_is_unambiguous -v`

Expected: FAIL until the exact approved responsibility language is present.

- [ ] **Step 3: Rewrite `Nasıl Çalışır`**

Use five short sections: one combined order count, early threshold, progressive time changes, optional short pause, and automatic recovery. Keep `%34/%67/%100` only in an expandable or secondary detail, not in the opening explanation. State that employees can still override Debi from the computer.

- [ ] **Step 4: Rewrite `Platformlar`**

Use plain rows for customer-facing name, readiness, what Debi can see, and what Debi can change. Explain the official GetirYemek-to-Uber Eats Trendyol Go transition without presenting “Uber Eats Trendyol Go” as one unexplained brand name. Preserve truthful status differences for Yemeksepeti and custom/POS sources and add a visible update date of `6 Eylül 2026`.

- [ ] **Step 5: Rewrite `Güvenlik ve Veriler`**

Lead with 5–7 short guarantees, then visually separate the full privacy policy. Keep local storage, customer-data filtering, password reset, computer restart/reopen behavior, and no analytics claims. Use the same-network phone requirement as the default; remove unsupported off-site access language.

- [ ] **Step 6: Replace the FAQ with ten questions**

Use exactly the ten questions listed in the spec. Keep answers to one or two short paragraphs where possible. Merge “platform busy mode” and “employee can do it” into the first answer. Do not repeat full privacy-policy prose in the FAQ.

- [ ] **Step 7: Normalize the trial page**

Use “İlk ay ücretsiz; ilk 7 gün yalnızca ölçüm” as the opening. Show four numbered stages and preserve the existing form, its field names, validation, and submission endpoint.

- [ ] **Step 8: Run all site tests**

Run: `python -m unittest tests.test_site -v`

Expected: PASS.

- [ ] **Step 9: Commit the supporting-page rewrite**

```bash
git add index.html tests/test_site.py
git commit -m "feat: shorten Debi pages and FAQ"
```

### Task 4: Verify the finished local site

**Files:**
- Modify if required: `index.html`
- Test: `tests/test_site.py`

**Interfaces:**
- Consumes: finished static files from Tasks 1–3.
- Produces: a locally reviewable site with no console errors or broken routes.

- [ ] **Step 1: Run automated checks**

Run:

```text
python -m unittest tests.test_site -v
git diff --check
```

Expected: tests pass and `git diff --check` prints no errors.

- [ ] **Step 2: Serve the site locally**

Run `python -m http.server 8765` from `C:\Users\Dell\getdebi-site` and keep the server bound only for local review.

- [ ] **Step 3: Review responsive states**

Open `http://127.0.0.1:8765/` and inspect at approximately 360 px, 768 px, and 1440 px widths. Verify navigation, hero, phone screenshots, forms, and no horizontal overflow.

- [ ] **Step 4: Review themes and routes**

Verify light/dark theme and visit `#/nasil-calisir`, `#/platformlar`, `#/guvenlik`, `#/sss`, `#/deneme`, `#/neden`, and `#/iletisim`. Check browser console for errors.

- [ ] **Step 5: Present the local result without pushing**

Open the local site for the user, list changed files and test results, and ask for copy/layout feedback. Do not push or publish.

