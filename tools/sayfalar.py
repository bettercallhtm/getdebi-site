"""Alt sayfaların gerçek adreslerini üretir: /platformlar/index.html gibi.

    python tools/sayfalar.py            üret (index.html'i her düzenleyişten sonra)
    python tools/sayfalar.py --kontrol  güncel mi; değilse çıkış kodu 1

**Neden.** Site tek dosya (index.html) ve sayfalar arasında JavaScript ile
geçiliyor. Eskiden adresler #/platformlar biçimindeydi; arama motorları "#"
sonrasını ayrı sayfa saymadığı için Google yalnızca ana sayfayı görüyordu.
GitHub Pages sunucu tarafında yönlendirme yapmıyor; her adresin gerçek bir
dosyası olmalı. Bu betik index.html'in kopyalarını üretiyor, her birinde:

  * o sayfanın başlığı, açıklaması, kanonik adresi ve paylaşım etiketleri,
  * o sayfanın bölümü baştan açık (JavaScript çalışmadan da doğru içerik).

**Kaynak index.html.** Üretilen dosyaları elle düzenleme; bir sonraki
üretimde ezilir. tests/test_site.py kopyaların güncel olduğunu denetliyor.
"""

import re
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
SITE = "https://getdebi.com"

# Arama sonucunda görünen açıklama; her sayfanın kendi giriş metninden.
# /neden bilerek yok: sitede gizli ve emekliye ayrılmış bir sayfa.
ACIKLAMALAR = {
    "/nasil-calisir": (
        "Debi bütün kanallardaki açık siparişleri tek yük olarak görür. "
        "Yoğunluk başlayınca önce süreleri ayarlar; mağazayı kısa süre "
        "durdurmak son seçenektir."
    ),
    "/platformlar": (
        "Uber Eats, GetirYemek, Yemeksepeti ve Migros Yemek siparişleri aynı "
        "mutfakta toplanır. Debi her platformda o platformun izin verdiği "
        "ayarı kullanır."
    ),
    "/guvenlik": (
        "Debi işletmenizdeki bilgisayarda çalışır ve müşteri bilgilerini "
        "kaydetmez; telefon uygulaması mağazanızı yönetemez. Güvenlik ve "
        "gizlilik politikası."
    ),
    "/sss": (
        "Debi hakkında sık sorulanlar: mağazayı kapatır mı, kurulum için ne "
        "gerekir, ücretsiz ay nasıl ilerler, Uber Eats Yoğun Modu'ndan farkı ne."
    ),
    "/deneme": (
        "İlk 7 gün Debi hiçbir ayarı değiştirmeden işletmenizi izler; yoğun "
        "saatleri ve ceza riskini tek sayfalık raporda görürsünüz. İlk ay ücretsiz."
    ),
    "/iletisim": (
        "Sorularınız, fiyat ve ücretsiz deneme için Debi ile iletişime geçin: "
        "info@getdebi.com."
    ),
}

URETILDI = ("<!-- ÜRETİLDİ: tools/sayfalar.py — bu dosyayı düzenleme; "
            "index.html'i düzenleyip betiği çalıştır. -->")


def basliklar(html):
    """PAGES dizisinden {yol: başlık}. Başlık JavaScript'in yazdığıyla aynı olsun."""
    blok = re.search(r"var PAGES = \[(.*?)\];", html, re.S).group(1)
    return {
        yol: baslik
        for yol, baslik in re.findall(r'path:"([^"]+)"[^}]*?title:"([^"]+)"', blok)
    }


def _degistir(html, desen, yeni, yol):
    sonuc, adet = re.subn(desen, lambda _: yeni, html, count=1)
    if adet != 1:
        raise SystemExit(f"{yol}: index.html'de beklenen etiket yok: {desen}")
    return sonuc


def _nitelik(metin):
    return metin.replace("&", "&amp;").replace('"', "&quot;")


def uret(html, yol):
    """index.html içeriğinden `yol` sayfasının dosyasını üretir."""
    baslik = f"{basliklar(html)[yol]} · Debi"
    aciklama = _nitelik(ACIKLAMALAR[yol])
    adres = f"{SITE}{yol}/"

    html = _degistir(html, r"<title>[^<]*</title>", f"<title>{baslik}</title>", yol)
    html = _degistir(html, r'<meta name="description" content="[^"]*">',
                     f'<meta name="description" content="{aciklama}">', yol)
    html = _degistir(html, r'<link rel="canonical" href="[^"]*">',
                     f'<link rel="canonical" href="{adres}">', yol)
    html = _degistir(html, r'<meta property="og:url" content="[^"]*">',
                     f'<meta property="og:url" content="{adres}">', yol)
    html = _degistir(html, r'<meta property="og:title" content="[^"]*">',
                     f'<meta property="og:title" content="{_nitelik(baslik)}">', yol)
    html = _degistir(html, r'<meta property="og:description" content="[^"]*">',
                     f'<meta property="og:description" content="{aciklama}">', yol)
    html = _degistir(html, r'<section class="page active" data-page="/">',
                     '<section class="page" data-page="/">', yol)
    html = _degistir(html, rf'<section class="page" data-page="{re.escape(yol)}">',
                     f'<section class="page active" data-page="{yol}">', yol)
    html = _degistir(html, r"<!doctype html>", "<!doctype html>\n" + URETILDI, yol)
    return html


def hedef(yol):
    return KOK / yol.strip("/") / "index.html"


def main(argv):
    kaynak = (KOK / "index.html").read_text(encoding="utf-8")
    eksik = set(ACIKLAMALAR) - set(basliklar(kaynak))
    if eksik:
        raise SystemExit(f"PAGES'te olmayan sayfa: {sorted(eksik)}")

    kontrol = "--kontrol" in argv
    eski = []
    for yol in ACIKLAMALAR:
        icerik = uret(kaynak, yol)
        dosya = hedef(yol)
        if kontrol:
            if not dosya.exists() or dosya.read_text(encoding="utf-8") != icerik:
                eski.append(str(dosya.relative_to(KOK)))
            continue
        dosya.parent.mkdir(exist_ok=True)
        dosya.write_text(icerik, encoding="utf-8", newline="\n")
        print(f"yazıldı: {dosya.relative_to(KOK)}")
    if eski:
        print("Güncel değil (python tools/sayfalar.py çalıştır):", ", ".join(eski))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
