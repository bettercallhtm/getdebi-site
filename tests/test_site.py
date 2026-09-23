import importlib.util
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location("sayfalar", ROOT / "tools" / "sayfalar.py")
sayfalar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sayfalar)


def site_html():
    return (ROOT / "index.html").read_text(encoding="utf-8")


def page(html, route):
    match = re.search(
        rf'<section class="page(?: active)?" data-page="{re.escape(route)}">(.*?)'
        rf'(?=<section class="page(?: active)?" data-page=|</main>)',
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
                self.assertTrue((ROOT / source.lstrip("/")).is_file())
                self.assertTrue(alt.strip())

    def test_fonts_are_self_hosted(self):
        # Google Fonts her ziyaretçinin IP adresini Google'a gönderiyordu;
        # gizlilik politikası bunu söylemiyordu. Yazı tipleri yerelde kalmalı.
        for name in ("index.html", "ornek-rapor.html"):
            with self.subTest(file=name):
                text = (ROOT / name).read_text(encoding="utf-8")
                self.assertNotIn("fonts.googleapis.com", text)
                self.assertNotIn("fonts.gstatic.com", text)
        fonts = re.findall(r"url\(/?(fonts/[^)]+\.woff2)\)", site_html())
        self.assertEqual(len(fonts), 4, "@font-face kuralları bulunamadı")
        for source in fonts:
            with self.subTest(font=source):
                self.assertTrue((ROOT / source).is_file())
        for family in ("plus-jakarta-sans", "jetbrains-mono"):
            self.assertTrue((ROOT / "fonts" / f"{family}-OFL.txt").is_file())

    def test_customer_copy_avoids_retired_words(self):
        # Ürün dili: bu kelimeler müşteri yüzeyinde kullanılmıyor ("yavaşlatma"
        # olumsuz çağrışım yapıyor; diğerleri yazılım jargonu). Yerine: süre
        # optimizasyonu / süreleri uzatmak, izleme modu, ayar, risk, son karar.
        yasak = ("yavaşlat", "fren", "gölge mod", "gölge hafta", "kaldıraç",
                 "maruziyet", "kontrolcü", "webhook", "onboarding", "endpoint")
        for name in ("index.html", "ornek-rapor.html"):
            text = (ROOT / name).read_text(encoding="utf-8").lower()
            for kelime in yasak:
                with self.subTest(file=name, kelime=kelime):
                    self.assertNotIn(kelime, text)

    # ---- gerçek sayfa adresleri ----

    def test_generated_pages_are_up_to_date(self):
        # index.html düzenlenip tools/sayfalar.py çalıştırılmazsa alt sayfalar
        # eski içerikle yayına çıkar. Bu test onu yakalıyor.
        html = site_html()
        for yol in sayfalar.ACIKLAMALAR:
            with self.subTest(page=yol):
                dosya = sayfalar.hedef(yol)
                self.assertTrue(dosya.is_file(), f"{dosya} yok: python tools/sayfalar.py")
                self.assertEqual(dosya.read_text(encoding="utf-8"),
                                 sayfalar.uret(html, yol),
                                 "güncel değil: python tools/sayfalar.py")

    def test_each_page_has_own_address_title_and_open_section(self):
        for yol in sayfalar.ACIKLAMALAR:
            with self.subTest(page=yol):
                text = sayfalar.hedef(yol).read_text(encoding="utf-8")
                self.assertIn(f'<link rel="canonical" href="https://getdebi.com{yol}/">', text)
                self.assertNotIn("<title>Debi — ", text)
                acik = re.findall(r'<section class="page active" data-page="([^"]+)"', text)
                self.assertEqual(acik, [yol])
        home = re.findall(r'<section class="page active" data-page="([^"]+)"', site_html())
        self.assertEqual(home, ["/"])

    def test_internal_links_use_real_addresses(self):
        html = site_html()
        self.assertNotIn('href="#/', html)
        self.assertNotIn('"#" + p.path', html)
        # Alt sayfadan açılınca göreli yol bozulur: dosyalar kökten istenmeli.
        for rel in re.findall(r'(?:src|href)="([^"/#:][^":]*\.(?:webp|png|html|woff2))"', html):
            self.fail(f"göreli yol: {rel}")

    def test_sitemap_lists_every_page(self):
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        for yol in ["/", *(f"{y}/" for y in sayfalar.ACIKLAMALAR)]:
            with self.subTest(page=yol):
                self.assertIn(f"<loc>https://getdebi.com{yol}</loc>", sitemap)

    def test_third_party_requests_match_privacy_policy(self):
        # Gizlilik politikası "sayaç ve form iletim hizmeti dışında site başka
        # bir hizmete bağlanmaz" diyor. Yeni bir dış kaynak eklenirse bu test
        # düşer; politikayı da güncellemeden geçirme.
        izinli = {"static.cloudflareinsights.com", "api.web3forms.com"}
        desen = r'(?:src=["\']|fetch\(["\']|url\()(https?://[^"\')]+)'
        for name in ("index.html", "ornek-rapor.html"):
            text = (ROOT / name).read_text(encoding="utf-8")
            for url in re.findall(desen, text):
                with self.subTest(file=name, url=url):
                    self.assertIn(re.match(r"https?://([^/]+)", url).group(1), izinli)
        policy = site_html()
        self.assertIn("Cloudflare Web Analytics", policy)
        self.assertIn("çerez kullanmaz", policy)

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
