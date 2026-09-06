# Debi Report Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn Debi's observation report into a one-page business decision document and keep the website example identical to the desktop application's real report output.

**Architecture:** Extend `ozetle()` with presentation-neutral day/hour and threshold-duration summaries derived from existing events. Render those values in a redesigned self-contained HTML report, retain HTML escaping and existing exposure calculations, and regenerate the website example from the same generator.

**Tech Stack:** Python 3 standard library, `unittest`, self-contained HTML/CSS/SVG

**Spec:** `C:\Users\Dell\getdebi-site\docs\superpowers\specs\2026-09-06-debi-site-copy-and-report-redesign-design.md`

## Global Constraints

- Do not change the decision engine, providers, installer, or mobile API.
- Preserve existing exposure and density-period calculations.
- Separate measured facts, calculated risk, and untested live-mode scenarios.
- Never call observation-mode exposure “earned”, “saved”, or “prevented” money.
- Keep the report self-contained, printable, and safe for untrusted business names.
- Missing data must render as unavailable, not as an invented zero.
- Regenerate the website example from the real report generator.
- Do not push; show the finished report to the user first.

---

### Task 1: Add report-summary contracts

**Files:**
- Modify: `C:\Users\Dell\servis-panosu-servis\tests\test_logic.py:2032-2190`
- Modify: `C:\Users\Dell\servis-panosu-servis\app\rapor.py:111-192`

**Interfaces:**
- Consumes: event dictionaries containing `_an`, `kind`, `open_orders`, `level`, and optional `exposure`.
- Produces: `ozetle()` keys `gun_saat_yuku`, `esik_ustu_saniye`, `en_riskli_donemler`, and `platform_adlari` in addition to existing keys.

- [ ] **Step 1: Write failing summary tests**

Add tests with events on two different days/hours and assert:

```python
    def test_rapor_gun_saat_yuku_ve_esik_ustu_sureyi_uretir(self):
        pzt = datetime.datetime(2026, 8, 24, 20, 0, tzinfo=datetime.timezone.utc)
        sal = datetime.datetime(2026, 8, 25, 13, 0, tzinfo=datetime.timezone.utc)
        olaylar = [
            {"ts": pzt.isoformat(), "kind": "shadow_level", "level": 2,
             "open_orders": 14, "_an": pzt},
            {"ts": (pzt + datetime.timedelta(minutes=5)).isoformat(),
             "kind": "shadow_close", "level": 3, "open_orders": 16,
             "exposure": 300, "_an": pzt + datetime.timedelta(minutes=5)},
            {"ts": sal.isoformat(), "kind": "shadow_level", "level": 1,
             "open_orders": 12, "_an": sal},
        ]
        sonuc = ozetle(olaylar, {**config_module.DEFAULTS, "max_open_orders": 12})
        self.assertEqual(sonuc["gun_saat_yuku"][(0, 20)], 16)
        self.assertEqual(sonuc["gun_saat_yuku"][(1, 13)], 12)
        self.assertGreaterEqual(sonuc["esik_ustu_saniye"], 0)
        self.assertEqual(sonuc["en_riskli_donemler"][0]["tepe"], 300)
```

Add a config test asserting enabled provider display names are returned and an empty-provider config returns an empty list.

- [ ] **Step 2: Run focused tests and verify missing-key failures**

Run: `python -m unittest tests.test_logic.RaporTests.test_rapor_gun_saat_yuku_ve_esik_ustu_sureyi_uretir -v`

Expected: FAIL because the new summary keys do not exist.

- [ ] **Step 3: Implement presentation-neutral summaries**

In `ozetle()`:

- aggregate maximum `open_orders` by `(weekday, hour)` into `gun_saat_yuku`;
- expose the existing `donem_listesi` sorted by `tepe` as at most three `en_riskli_donemler` records;
- derive enabled provider names from `cfg["providers"]` without exposing secrets;
- compute `esik_ustu_saniye` only from consecutive event timestamps while load is at or above `max_open_orders`, capping a single gap at the configured polling cadence so missing logs do not inflate duration.

Keep all existing return keys unchanged.

- [ ] **Step 4: Run the report test class**

Run: `python -m unittest tests.test_logic.RaporTests -v`

Expected: PASS.

- [ ] **Step 5: Commit the summary extension**

```bash
git add app/rapor.py tests/test_logic.py
git commit -m "feat: add decision-ready report summaries"
```

### Task 2: Redesign the HTML report

**Files:**
- Modify: `C:\Users\Dell\servis-panosu-servis\app\rapor.py:195-430`
- Modify: `C:\Users\Dell\servis-panosu-servis\tests\test_logic.py:2081-2189`

**Interfaces:**
- Consumes: the enriched `ozetle()` mapping from Task 1.
- Produces: `_yogunluk_haritasi(o) -> str` and redesigned `html_rapor(o, isletme="") -> str`.

- [ ] **Step 1: Replace old-label assertions with decision-report assertions**

Add or update tests so observation-mode HTML must contain:

```python
self.assertIn("7 günlük yalnızca izleme raporu", sayfa)
self.assertIn("ÖLÇÜLDÜ", sayfa)
self.assertIn("HESAPLANDI", sayfa)
self.assertIn("SENARYO", sayfa)
self.assertIn("Müdahalesiz akışta kapatma eşiğine ulaşan dönem", sayfa)
self.assertIn("Önerilen başlangıç ayarı", sayfa)
self.assertNotIn("Kapatma gerekirdi", sayfa)
self.assertNotIn("Yalnızca süre optimizasyonu yeterdi", sayfa)
self.assertNotIn("canlıya geçin", sayfa.lower())
```

Keep the existing complete-document and HTML-escaping assertions.

- [ ] **Step 2: Run the updated HTML tests and verify they fail**

Run: `python -m unittest tests.test_logic.RaporTests -v`

Expected: failures for the new headings and removed labels.

- [ ] **Step 3: Implement the day/hour heat map**

Replace `_yuk_grafigi()` with `_yogunluk_haritasi(o)`. Render a seven-row by 24-column inline SVG or CSS grid using `gun_saat_yuku`; use neutral, warning, and threshold colors based on `devreye_girme_esigi`. Include day labels, three-hour tick labels, an accessible `aria-label`, and a legend whose colors exactly match the rendered cells. Return a plain “Yeterli gün/saat verisi yok” block when the mapping is empty.

- [ ] **Step 4: Rebuild `html_rapor()` in the approved order**

Render:

1. title, date range, provider coverage, and “7 günlük yalnızca izleme raporu” label;
2. one-sentence result using `mudahale_donemi` and `kapatma_donemi`;
3. an `ÖLÇÜLDÜ` group for peak load, period count, threshold time, and busy times;
4. a `HESAPLANDI` money-risk card with tariff/formula explanation;
5. a `SENARYO` block using “süre kademesi aralığında kalan dönem” and “müdahalesiz akışta kapatma eşiğine ulaşan dönem”;
6. the heat map and three highest-risk periods;
7. a concise “Bu raporun söylemediği” block;
8. “Önerilen başlangıç ayarı” showing threshold, throttle steps as levels, and close enabled/disabled;
9. a next-review prompt rather than an automatic live-mode instruction.

Use an A4-friendly print stylesheet, preserve one self-contained HTML file, and keep exact money figures labeled as calculated risk.

- [ ] **Step 5: Keep the plain-text report semantically aligned**

Update `metin(o)` to use the same measured/calculated/scenario distinctions and remove “süre yetmezdi” as a proven result. Preserve error-count output.

- [ ] **Step 6: Run report tests and the full suite**

Run:

```text
python -m unittest tests.test_logic.RaporTests -v
python -m unittest tests.test_logic -v
```

Expected: PASS.

- [ ] **Step 7: Commit the report redesign**

```bash
git add app/rapor.py tests/test_logic.py
git commit -m "feat: redesign Debi observation report"
```

### Task 3: Regenerate and synchronize the website example

**Files:**
- Modify if required: `C:\Users\Dell\servis-panosu-servis\app\ornek_rapor.py:220-254`
- Regenerate: `C:\Users\Dell\getdebi-site\ornek-rapor.html`
- Modify: `C:\Users\Dell\getdebi-site\tests\test_site.py`

**Interfaces:**
- Consumes: `app.ornek_rapor.rapor_uret()` and the redesigned `html_rapor()`.
- Produces: the website's committed example report generated from the same desktop code.

- [ ] **Step 1: Add a site test for report synchronization markers**

Extend `tests/test_site.py` to load `ornek-rapor.html` and assert:

```python
REPORT = (ROOT / "ornek-rapor.html").read_text(encoding="utf-8")

def test_example_report_uses_decision_report_structure(self):
    for text in ("7 günlük yalnızca izleme raporu", "ÖLÇÜLDÜ", "HESAPLANDI", "SENARYO"):
        self.assertIn(text, REPORT)
    self.assertIn("ÖRNEK", REPORT)
```

- [ ] **Step 2: Run the site report test and verify it fails**

Run from `C:\Users\Dell\getdebi-site`: `python -m unittest tests.test_site -v`

Expected: FAIL because the old example report lacks the new structure.

- [ ] **Step 3: Regenerate the example from the desktop repository**

Run from `C:\Users\Dell\servis-panosu-servis`:

```text
python -m app.ornek_rapor C:\Users\Dell\getdebi-site\ornek-rapor.html --gun 7 --tohum 11 --isletme "Örnek Restoran"
```

If the example banner insertion anchor changed, update `app/ornek_rapor.py` to insert the banner immediately inside `<body>` using a stable marker emitted by `html_rapor()` rather than searching for layout-specific markup.

- [ ] **Step 4: Run both repositories' relevant tests**

Run:

```text
python -m unittest tests.test_logic.RaporTests -v
python -m unittest tests.test_site -v
```

Expected: PASS in their respective working directories.

- [ ] **Step 5: Commit the synchronized example in each repository**

In `servis-panosu-servis`:

```bash
git add app/ornek_rapor.py
git commit -m "fix: keep example report generation stable"
```

Skip this commit if `app/ornek_rapor.py` did not change.

In `getdebi-site`:

```bash
git add ornek-rapor.html tests/test_site.py
git commit -m "feat: publish redesigned Debi example report"
```

### Task 4: Visual and print verification

**Files:**
- Modify if required: `C:\Users\Dell\servis-panosu-servis\app\rapor.py`
- Regenerate after any fix: `C:\Users\Dell\getdebi-site\ornek-rapor.html`

**Interfaces:**
- Consumes: final self-contained example report.
- Produces: a readable desktop/mobile report and an A4 print preview without clipped content.

- [ ] **Step 1: Serve the website locally and open the example report**

Use the site's local HTTP server and open `http://127.0.0.1:8765/ornek-rapor.html`.

- [ ] **Step 2: Inspect desktop, phone, and print presentation**

Check approximately 360 px and 1200 px widths, then browser print preview. Verify heat-map labels, money-risk qualification, section hierarchy, no horizontal overflow, and A4-friendly pagination.

- [ ] **Step 3: Regenerate after any source fix**

Never hand-edit only the generated `ornek-rapor.html`. Make fixes in `app/rapor.py` or `app/ornek_rapor.py`, rerun the generator, and rerun both test suites.

- [ ] **Step 4: Present the result without pushing**

Open the local example report beside the local home page, summarize tests and remaining limitations, and wait for explicit user approval before any push.

