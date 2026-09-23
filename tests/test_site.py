import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def site_html():
    return (ROOT / "index.html").read_text(encoding="utf-8")


def page(html, route):
    match = re.search(
        rf'<section class="page" data-page="{re.escape(route)}">(.*?)'
        rf'(?=<section class="page" data-page=|</main>)',
        html,
        re.S,
    )
    if not match:
        raise AssertionError(f"Sayfa rotası bulunamadı: {route}")
    return match.group(1)


class SiteContracts(unittest.TestCase):
    def test_required_pages_are_available(self):
        html = site_html()
        for route in (
            "/",
            "/nasil-calisir",
            "/platformlar",
            "/guvenlik",
            "/sss",
            "/deneme",
        ):
            with self.subTest(route=route):
                self.assertIn(f'data-page="{route}"', html)

    def test_faq_stays_short_enough_to_scan(self):
        faq = page(site_html(), "/sss")
        self.assertLessEqual(len(re.findall(r"<details>", faq)), 12)

    def test_faq_answers_staff_and_uber_eats_busy_mode_objections(self):
        faq = page(site_html(), "/sss")
        self.assertIn("Bunu bir çalışanım yapamaz mı?", faq)
        self.assertIn("Uber Eats Yoğun Modu bu işi yapamaz mı?", faq)

    def test_public_brand_name_is_uber_eats(self):
        html = site_html()
        self.assertIn("Uber Eats", html)
        self.assertNotIn("Trendyol Go", html)
        report = (ROOT / "ornek-rapor.html").read_text(encoding="utf-8")
        self.assertIn("Uber Eats", report)
        self.assertNotIn("trendyol", report.lower())

    def test_customer_facing_level_names_start_with_capitals(self):
        html = site_html()
        for label in ("Normal", "Hafif", "Orta", "Güçlü", "Duraklat"):
            self.assertRegex(html, rf">{label}<")

    def test_homepage_contains_capacity_comparison_chart(self):
        home = page(site_html(), "/")
        self.assertIn("Debi yokken", home)
        self.assertIn("Debi devrede", home)
        self.assertIn(">Ceza bölgesi<", home)
        self.assertIn("Devreye girme eşiği 12", home)
        self.assertIn('class="fig capacity-chart"', home)

    def test_contact_page_has_no_personal_name_or_phone(self):
        # Kişisel isim ve telefon kaldırıldı (profesyonel dursun); iletişim
        # e-posta üzerinden. Hassas değeri dosyaya GÖMMEDEN yapısal yokluğu
        # sınıyoruz (aksi halde geçmiş-temizleme script'i bu satırı da bozar):
        # hiç "tel:" linki ve "Telefon ·" kanal etiketi olmamalı.
        html = site_html()
        self.assertNotIn("tel:", html)
        self.assertNotIn("Telefon ·", html)  # "Telefon ·" kanal basligi
        contact = page(html, "/iletisim")
        self.assertIn("info@getdebi.com", contact)

    def test_phone_screenshots_are_local_and_accessible(self):
        sources = re.findall(
            r'<img[^>]+src="([^"]*mobil-[^"]+)"[^>]+alt="([^"]+)"',
            site_html(),
        )
        self.assertGreaterEqual(len(sources), 2)
        for source, alt in sources:
            with self.subTest(source=source):
                self.assertTrue((ROOT / source).is_file())
                self.assertTrue(alt.strip())

    def test_fonts_are_self_hosted(self):
        # Google Fonts her ziyaretçinin IP adresini Google'a gönderiyordu;
        # gizlilik politikası bunu söylemiyordu. Yazı tipleri yerelde kalmalı.
        for name in ("index.html", "ornek-rapor.html"):
            with self.subTest(file=name):
                text = (ROOT / name).read_text(encoding="utf-8")
                self.assertNotIn("fonts.googleapis.com", text)
                self.assertNotIn("fonts.gstatic.com", text)
        for source in re.findall(r"url\((fonts/[^)]+\.woff2)\)", site_html()):
            with self.subTest(font=source):
                self.assertTrue((ROOT / source).is_file())
        for family in ("plus-jakarta-sans", "jetbrains-mono"):
            self.assertTrue((ROOT / "fonts" / f"{family}-OFL.txt").is_file())

    def test_phone_screenshots_share_the_same_top_edge(self):
        html = site_html()
        self.assertNotRegex(
            html,
            r"\.phone-shots figure:nth-child\(2\)\s*\{[^}]*margin-top",
        )

    def test_visible_navigation_excludes_only_retired_why_page(self):
        html = site_html()
        pages_block = re.search(r"var PAGES = \[(.*?)\];", html, re.S).group(1)
        why_row = re.search(r'\{path:"/neden".*?\}', pages_block, re.S).group(0)
        contact_row = re.search(
            r'\{path:"/iletisim".*?\}', pages_block, re.S
        ).group(0)
        self.assertIn("gizli:true", why_row)
        self.assertNotIn("gizli:true", contact_row)

    def test_example_report_separates_facts_from_scenario(self):
        report = (ROOT / "ornek-rapor.html").read_text(encoding="utf-8")
        for marker in (
            "Kayıtlardan",
            "Tarifenizle",
            "Debi açık olsaydı",
            "Mutfak en çok ne zaman zorlandı?",
            "Bu rakamları nasıl okumalı?",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, report)


if __name__ == "__main__":
    unittest.main()
