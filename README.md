# getdebi.com

Debi'nin tanitim sitesi. Kaynak tek dosya, bagimlilik yok.

    index.html           sitenin tamami (stil ve betik dahil) — KAYNAK
    <sayfa>/index.html   alt sayfalar (/platformlar/ gibi) — URETILIR, elle duzenleme
    tools/sayfalar.py    alt sayfalari index.html'den uretir
    sitemap.xml          butun sayfa adresleri
    CNAME                GitHub Pages'in ozel alan adi dosyasi

index.html'i her duzenleyisten sonra:

    python tools/sayfalar.py
    python -m unittest discover -s tests

Test, alt sayfalar guncel degilse duser.

Sayfa gecisleri tarayicida yapiliyor ama her sayfanin gercek adresi var
(eskiden #/platformlar idi; Google yalnizca ana sayfayi goruyordu). Eski #/
baglantilari acilinca yeni adrese cevriliyor. Dosyalar koke gore isteniyor
(/fonts/..., /mobil-...webp): alt sayfadan goreli yol bozulur.

Servisin kendisi ayri bir depoda: servis-panosu-servis
