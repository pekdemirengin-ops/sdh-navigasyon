import streamlit as st
import os
import re
from pathlib import Path
from PIL import Image

# ==============================================================================
# ⚙️ SAYFA & MOBİL VIEWPORT YAPILANDIRMASI
# ==============================================================================
st.set_page_config(
    page_title="SDH Mobil Navigasyon", 
    page_icon="🏥", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 📱 MOBİL İYİLEŞTİRME VE KROKİ ZOOM STİLLERİ (CSS)
# ==============================================================================
st.markdown("""
    <style>
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    .stButton > button {
        width: 100% !important;
        min-height: 48px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        margin-bottom: 4px !important;
    }
    input, select {
        font-size: 16px !important;
    }
    .kroki-container {
        width: 100%;
        overflow: auto;
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        background-color: #fafafa;
        padding: 5px;
        margin-top: 10px;
    }
    .kroki-container img {
        transition: transform 0.25s ease;
        cursor: zoom-in;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 📌 QR KOD KONUM ALGILAMA
# ==============================================================================
query_params = st.query_params
baslangic_noktasi = query_params.get("konum", "Poliklinik Binası Ana Girişi (Zemin Kat)")

# ==============================================================================
# 🗄️ MERKEZİ VERİ TABANI (POLİKLİNİKLER VE DİĞER BİRİMLER)
# ==============================================================================
POLIKLINIKLER = {
    "Heyet Çocuk (Çözger) Poliklinik": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Girişten koridora girip sola ilerleyin. KBB odasının yanındaki odadır.",
        "kroki": "heyet_cozger_polk_yol_tarifi.png"
    },
    "Heyet Fizik Tedavi Poliklinik": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Girişten koridora ilerleyip sol tarafa yönelin. Ön merdivenlerin hemen yanında yer alır.",
        "kroki": "heyet_fizik_tedavi_polk_yol_tarifi.png"
    },
    "Heyet KBB Poliklinik": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Ana girişten girdikten sonra sola dönün. Ön merdivenleri geçince sağ taraftadır.",
        "kroki": "heyet_kbb_polk_yol_tarifi.png"
    },
    "Heyet Ortopedi Poliklinik": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Girişten koridora girip sola ilerleyin. KBB odasının yanındaki odadır.",
        "kroki": "heyet_ortopedi_polk_yol_tarifi.png"
    },
    "Heyet Çocuk Psikiyatri Poliklinik": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Girişten koridora girip sola ilerleyin. KBB odasının yanındaki odadır.",
        "kroki": "heyet_cocuk_psikiyatri_polk_yol_tarifi.png"
    },
    "Kan Alma Birimi": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Poliklinik binası girişinden girdikten sonra düz ilerleyip sağ taraftaki Kan Alma odasına geçebilirsiniz.",
        "kroki": "kan_alma_yol_tarifi.png"
    },
    "Sağlık Kurulu": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Ana girişten girdikten sonra sağa doğru ilerleyin. Koridorun sonundaki geniş alanda yer almaktadır.",
        "kroki": "saglık_kurulu_yol_tarifi.png"
    },
    "Sağlık Kurulu Kayıt Birimi": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Girişten hemen sonra düz devam edin, sol taraftaki bankoda yer almaktadır.",
        "kroki": "saglık_kurulu_kayıt_yol_tarifi.png"
    },
    "Ön Merdivenler": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Girişten girdikten sonra sola yönelin, koridor boyunca düz ilerleyerek ön merdivenlere ulaşabilirsiniz.",
        "kroki": "on_merdivenler_yol_tarifi.png"
    },
    "Arka Çıkış": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Koridordan sola ilerleyin, ön merdivenleri geçip sola dönerek arka çıkış kapısına ulaşabilirsiniz.",
        "kroki": "arka_cıkıs_yol_tarifi.png"
    },
    "Heyet Genel Cerrahi Poliklinik": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıktıktan sonra koridordan sağa yönelin. Koridorun solunda yer almaktadır.",
        "kroki": "heyet_genel_cerrahi_polk_yol_tarifi.png"
    },
    "Fizik Tedavi 2 Poliklinik": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Koridorda sağa doğru ilerleyin, koridorun sonuna doğru sağ tarafta kalmaktadır.",
        "kroki": "fizik_tedavi_polk2_yol_tarifi.png"
    },
    "Heyet Nöroloji Poliklinik": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Ana koridorda sağa doğru son noktaya kadar ilerleyin, sol taraftaki oda.",
        "kroki": "heyet_noroloji_polk_yol_tarifi.png"
    },
    "Görme Alanı Ölçüm Odası": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Koridorda düz devam edin, sağa dönmeden önceki sol hizada bulunan Alan Görme odasıdır.",
        "kroki": "gorme_alanı_yol_tarifi.png"
    },
    "Heyet Dahiliye Poliklinik": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Koridor boyunca sağa doğru ilerleyin. Sağ taraftaki odalardan biridir.",
        "kroki": "heyet_dahiliye_polk_yol_tarifi.png"
    },
    "Heyet Göğüs Hastalıkları Poliklinik": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıktıktan hemen sonra sol çaprazda yer almaktadır.",
        "kroki": "heyet_gogus_hastalıkları_polk_yol_tarifi.png"
    },
    "Heyet Göz Poliklinik": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıkıp sola dönün, en uçtaki sol odadır.",
        "kroki": "heyet_goz_polk_yol_tarifi.png"
    },
    "Konuşma Terapisti": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıkınca arka merdiven yönüne (sola) dönün, koridorun sonunda sol taraftadır.",
        "kroki": "konusma_terapisti_yol_tarifi.png"
    },
    "Heyet Kardiyoloji Poliklinik": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Ana koridorda sağa doğru sonuna kadar ilerleyin. Sağ taraftaki en son odadır.",
        "kroki": "heyet_kardiyoloji_polk_yol_tarifi.png"
    },
    "Heyet Üroloji Poliklinik": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıkıp sola dönün. Koridorun sonundaki sol oda.",
        "kroki": "heyet_uroloji_polk_yol_tarifi.png"
    },
    "İşitme Testi (Odio)": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Sağa doğru ilerleyin, test odası koridorun sağ tarafında kalmaktadır.",
        "kroki": "isitme_testi_birimi_yol_tarifi.png"
    },
    "Göz OCT Odası": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Koridorda sağa doğru ilerleyin, İşitme Testi odasının hemen yanında sağda yer alır.",
        "kroki": "goz_oct_yol_tarifi.png"
    },
    "Göz Ölçüm": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıkıp sola yönelin, ilk sol kapıdan girin.",
        "kroki": "goz_olcum_yol_tarifi.png"
    },
    "Nöroloji Poliklinik": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıktıktan sonra sağa dönün ve koridor boyunca ilerleyin. Sol tarafta kalmaktadır.",
        "kroki": "noroloji_polk_yol_tarifi.png"
    },
    "Heyet Psikiyatri Poliklinik": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıkıp sağ koridora ilerleyin, orta hizada yer alan psikiyatri poliklinikleridir.",
        "kroki": "heyet_psikiyatri_polk_yol_tarifi.png"
    },
    "Sabim Cimer Birimi": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıktıktan sonra arka merdiven yönüne (sola) dönün, koridoru takip edin.",
        "kroki": "sabim_cimer_yol_tarifi.png"
    },
    "Solunum Fonksiyon (SFT) Birimi": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Arka merdiven koridorunu geçip sola doğru ilerlediğinizde sol tarafta yer alır.",
        "kroki": "solunum_fonksiyon_yol_tarifi.png"
    }
}

DIGER_ALANLAR = {
    "Evrak Kayıt / Vezne": {
        "fancy": False, "kat": "zemin", 
        "tarif": "Zemin Kat - Ana girişten tam karşınızda.", 
        "kroki": "evrak_kayıt_vezne_yol_tarifi.png"
    },
    "Hasta Kayıt": {
        "fancy": False, "kat": "zemin", 
        "tarif": "Ana girişte sol tarafta yer alır.", 
        "kroki": "hasta_kayıt_yol_tarifi.png"
    },
    "Evde Sağlık Hizmetleri Birimi": {
        "fancy": False, "kat": "zemin", 
        "tarif": "Zemin Katta olup girişi binanın kuzey yönündedir.", 
        "kroki": "evde_saglık_hizmetleri_yol_tarifi"
    },
    "Röntgen / Görüntüleme (DİĞER BİNA)": {
        "fancy": True, "kat": "", 
        "tarif": "Diğer binadadır! Röntgen birimi bu binada değildir. Arka kapıdan çıkınca sola dönün, ardından sağa, ileride sağ tarafta yer alır.", 
        "kroki": "rontgen_yol_tarifi.png"
    },
    "Asansör": {
        "fancy": False, "kat": "zemin", 
        "tarif": "1. katta binanın tam orta kesiminde, zemin katta Hasta Kayıt bankosunun geçince sol tarafta yer alır.", 
        "kroki": "asansor_yol_tarifi.png"
    },
    "Emzirme Odası": {
        "fancy": False, "kat": "1kat", 
        "tarif": "1. Kat - Koridor boyunca sağa doğru ilerleyin. Sağ taraftaki odalardan biridir.", 
        "kroki": "emzirme_odası_yol_tarifi.png"
    },
    "Tuvaletler / Lavabolar": {
        "fancy": False, "kat": "zemin", 
        "tarif": "Zemin Katta: Ana girişten sonra sola dönün. Koridorun sonunda yer alır.", 
        "kroki": "tuvaletler_yol_tarifi.png"
    }
}

ES_ANLAMLILAR = {
    "kan": "Kan Alma Birimi", "kan alma": "Kan Alma Birimi", "tahlil": "Kan Alma Birimi", "laboratuvar": "Kan Alma Birimi",
    "wc": "Tuvaletler / Lavabolar", "lavabo": "Tuvaletler / Lavabolar", "tuvalet": "Tuvaletler / Lavabolar",
    "heyet": "Sağlık Kurulu", "rapor": "Sağlık Kurulu", "sağlık kurulu": "Sağlık Kurulu",
    "kulak": "Heyet KBB Poliklinik", "kbb": "Heyet KBB Poliklinik", "kulak burun boğaz": "Heyet KBB Poliklinik",
    "göz": "Heyet Göz Poliklinik", "kalp": "Heyet Kardiyoloji Poliklinik", "kardiyoloji": "Heyet Kardiyoloji Poliklinik",
    "çocuk": "Heyet Çocuk (Çözger) Poliklinik", "çözger": "Heyet Çocuk (Çözger) Poliklinik",
    "fizik": "Heyet Fizik Tedavi Poliklinik", "fizik tedavi": "Heyet Fizik Tedavi Poliklinik",
    "göğüs": "Heyet Göğüs Hastalıkları Poliklinik", "üroloji": "Heyet Üroloji Poliklinik",
    "cerrahi": "Heyet Genel Cerrahi Poliklinik", "genel cerrahi": "Heyet Genel Cerrahi Poliklinik",
    "röntgen": "Röntgen / Görüntüleme (DİĞER BİNA)", "film": "Röntgen / Görüntüleme (DİĞER BİNA)",
    "işitme": "İşitme Testi (Odio)", "odio": "İşitme Testi (Odio)", "işitme testi": "İşitme Testi (Odio)",
    "dahiliye": "Heyet Dahiliye Poliklinik", "nöroloji": "Heyet Nöroloji Poliklinik",
    "ortopedi": "Heyet Ortopedi Poliklinik", "psikiyatri": "Heyet Psikiyatri Poliklinik",
    "cimer": "Sabim Cimer Birimi", "sabim": "Sabim Cimer Birimi", "sft": "Solunum Fonksiyon (SFT) Birimi",
    "asansör": "Asansör", "vezne": "Evrak Kayıt / Vezne", "evrak kayıt": "Evrak Kayıt / Vezne",
    "hasta kayıt": "Hasta Kayıt"
}

# ==============================================================================
# 🧩 OTURUM DURUMU (SESSION STATE) BAŞLATMA
# ==============================================================================
if "secilen_birim" not in st.session_state:
    st.session_state["secilen_birim"] = "Seçim Yapınız..."
if "kategori" not in st.session_state:
    st.session_state["kategori"] = "🏥 Resmi Poliklinikler / Odalar"

# ==============================================================================
# 🛠️ YARDIMCI FONKSİYONLAR
# ==============================================================================
def otomatik_sesli_oku(metin):
    if metin and metin.strip():
        temiz_metin = metin.replace("1. Kat", "Birinci Kat").replace("'", "\\'").replace('"', '\\"')
        js_kodu = f"""
        <script>
            function konusData() {{
                try {{
                    if ('speechSynthesis' in window) {{
                        window.speechSynthesis.cancel();
                        var msg = new SpeechSynthesisUtterance('{temiz_metin}');
                        msg.lang = 'tr-TR';
                        msg.rate = 1.0;
                        window.speechSynthesis.speak(msg);
                    }}
                }} catch(e) {{}}
            }}
            setTimeout(konusData, 300);
            document.addEventListener('click', konusData, {{once: true}});
        </script>
        """
        st.components.v1.html(js_kodu, height=0)

def kroki_goster(kroki_dosya_adi):
    if not kroki_dosya_adi:
        return

    aranan_dosya = kroki_dosya_adi.strip()
    aranan_govde = Path(aranan_dosya).stem.lower()
    
    su_an = Path(__file__).resolve().parent
    calisma_dizini = Path.cwd()
    
    arama_dizinleri = [
        su_an,
        calisma_dizini,
        su_an / "hastane_navigasyon",
        calisma_dizini / "hastane_navigasyon",
        su_an / "krokiler",
        calisma_dizini / "krokiler"
    ]

    bulunan_dosya = None
    gecerli_uzantilar = {'.png', '.jpg', '.jpeg', '.webp'}
    bulunan_dosyalar_listesi = []

    for dizin in arama_dizinleri:
        if dizin.exists():
            try:
                for dosya in dizin.rglob("*"):
                    if dosya.is_file():
                        bulunan_dosyalar_listesi.append(dosya.name)
                        if dosya.suffix.lower() in gecerli_uzantilar:
                            if dosya.name.lower() == aranan_dosya.lower() or dosya.stem.lower() == aranan_govde:
                                bulunan_dosya = dosya
                                break
            except Exception:
                pass
        if bulunan_dosya:
            break

    if bulunan_dosya and bulunan_dosya.exists():
        try:
            import base64
            with open(bulunan_dosya, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode()
            
            uzanti = bulunan_dosya.suffix.lower().replace('.', '')
            if uzanti == 'jpg':
                uzanti = 'jpeg'
            img_data_uri = f"data:image/{uzanti};base64,{encoded_string}"
            dosya_id = bulunan_dosya.stem.replace(" ", "_").replace("-", "_")

            zoom_html = f"""
            <div style="text-align: center; margin-bottom: 4px; font-size: 12px; color: #555; font-weight: 500;">
                🔍 İki parmağınızla açarak büyütün, sürükleyerek gezinin (Çift dokunma sıfırlar)
            </div>
            <div id="box_{dosya_id}" style="width: 100%; height: 380px; overflow: hidden; border-radius: 12px; border: 2px solid #e0e0e0; background-color: #f9f9f9; position: relative; touch-action: none; display: flex; align-items: center; justify-content: center;">
                <img id="img_{dosya_id}" src="{img_data_uri}" style="max-width: 90%; max-height: 90%; object-fit: contain; transform: translate(0px, 0px) scale(1); will-change: transform; user-select: none; -webkit-user-drag: none;" />
            </div>
            <script>
            (function() {{
                const container = document.getElementById('box_{dosya_id}');
                const img = document.getElementById('img_{dosya_id}');
                
                let scale = 1, pointX = 0, pointY = 0;
                let startX = 0, startY = 0, initialDist = null, startScale = 1;
                let isDragging = false;

                function updateTransform() {{
                    img.style.transform = 'translate(' + pointX + 'px, ' + pointY + 'px) scale(' + scale + ')';
                }}

                // Mouse / Tek Parmak Sürükleme
                container.addEventListener('mousedown', function(e) {{
                    isDragging = true;
                    startX = e.clientX - pointX;
                    startY = e.clientY - pointY;
                }});
                window.addEventListener('mousemove', function(e) {{
                    if (!isDragging) return;
                    e.preventDefault();
                    pointX = e.clientX - startX;
                    pointY = e.clientY - startY;
                    updateTransform();
                }});
                window.addEventListener('mouseup', function() {{ isDragging = false; }});

                // Dokunmatik Ekran (Mobil - Tek ve İki Parmak)
                container.addEventListener('touchstart', function(e) {{
                    if (e.touches.length === 1) {{
                        isDragging = true;
                        startX = e.touches[0].clientX - pointX;
                        startY = e.touches[0].clientY - pointY;
                    }} else if (e.touches.length === 2) {{
                        isDragging = false;
                        initialDist = Math.hypot(
                            e.touches[0].clientX - e.touches[1].clientX,
                            e.touches[0].clientY - e.touches[1].clientY
                        );
                        startScale = scale;
                    }}
                }}, {{ passive: false }});

                container.addEventListener('touchmove', function(e) {{
                    if (isDragging && e.touches.length === 1) {{
                        e.preventDefault();
                        pointX = e.touches[0].clientX - startX;
                        pointY = e.touches[0].clientY - startY;
                        updateTransform();
                    }} else if (e.touches.length === 2 && initialDist !== null) {{
                        e.preventDefault();
                        let currentDist = Math.hypot(
                            e.touches[0].clientX - e.touches[1].clientX,
                            e.touches[0].clientY - e.touches[1].clientY
                        );
                        let factor = currentDist / initialDist;
                        scale = Math.min(Math.max(1, startScale * factor), 5);
                        updateTransform();
                    }}
                }}, {{ passive: false }});

                container.addEventListener('touchend', function(e) {{
                    if (e.touches.length < 2) initialDist = null;
                    if (e.touches.length === 0) isDragging = false;
                }});

                // Çift Tıklama / Çift Dokunma ile Sıfırlama
                let lastTap = 0;
                container.addEventListener('click', function(e) {{
                    let now = new Date().getTime();
                    if (now - lastTap < 300) {{
                        scale = 1;
                        pointX = 0;
                        pointY = 0;
                        updateTransform();
                    }}
                    lastTap = now;
                }});
            }})();
            </script>
            """
            st.components.v1.html(zoom_html, height=430)

        except Exception as e:
            st.error(f"⚠️ Görsel yüklenirken hata oluştu: {e}")
    else:
        st.warning(f"⚠️ Aranan Kroki Dosyası Bulunamadı: `{aranan_dosya}`")
        with st.expander("📂 Klasörde Tespit Edilen Dosyalar (Kontrol İçin)"):
            st.write(list(set(bulunan_dosyalar_listesi)) if bulunan_dosyalar_listesi else "Hiç dosya bulunamadı.")

def birim_sec(birim_adi):
    st.session_state["secilen_birim"] = birim_adi
    if birim_adi in DIGER_ALANLAR:
        st.session_state["kategori"] = "⚙️ Genel ve İdari Birimler"
    elif birim_adi in POLIKLINIKLER:
        st.session_state["kategori"] = "🏥 Resmi Poliklinikler / Odalar"

def akilli_arama_isle(gelen_metin):
    if not gelen_metin:
        return False
    temiz = re.sub(r'[^\w\s]', '', gelen_metin.lower()).strip()
    tum_birimler = {**POLIKLINIKLER, **DIGER_ALANLAR}

    if temiz in ES_ANLAMLILAR:
        birim_sec(ES_ANLAMLILAR[temiz])
        return True

    for birim in tum_birimler:
        if temiz == birim.lower():
            birim_sec(birim)
            return True

    for anahtar, hedef in ES_ANLAMLILAR.items():
        if anahtar in temiz or temiz in anahtar:
            birim_sec(hedef)
            return True

    kelimeler = temiz.split()
    en_iyi_eslesme = None
    max_ortak_kelime = 0

    for birim in tum_birimler:
        birim_kelimeleri = birim.lower().split()
        ortak = sum(1 for k in kelimeler if k in birim_kelimeleri)
        if ortak > max_ortak_kelime:
            max_ortak_kelime = ortak
            en_iyi_eslesme = birim

    if en_iyi_eslesme and max_ortak_kelime > 0:
        birim_sec(en_iyi_eslesme)
        return True
    return False

# ==============================================================================
# 🖥️ ARAYÜZ BAŞLIK VE KARŞILAMA
# ==============================================================================
st.title("🏥 SDH BARAJ YOLU EK BİNASI")
st.caption("📱 Mobil Sesli Dijital Yönlendirme Sistemi")
st.info(f"📍 **Bulunduğunuz Konum:** {baslangic_noktasi}")

# Açılışta Sesli Karşılama Mesajı (Tarayıcı etkileşim kilidini aşmak için buton tetiklemeli veya akıllı zamanlayıcılı)
if "karsilama_yapildi" not in st.session_state:
    st.session_state["karsilama_yapildi"] = True
    otomatik_sesli_oku("Seyhan Devlet Hastanesi Baraj Yolu Ek Hizmet Binası sesli dijital yönlendirme sistemine hoş geldiniz. Lütfen gitmek istediğiniz birimi seçiniz veya Konuş butonuna basarak konuşunuz.")

# Sesli arama parametresi kontrolü
if "ses_arama" in st.query_params:
    gelen_ses = st.query_params["ses_arama"]
    del st.query_params["ses_arama"]
    if gelen_ses:
        akilli_arama_isle(gelen_ses)

# ==============================================================================
# 🚀 HIZLI ERİŞİM BUTONLARI
# ==============================================================================
st.write("### 🚀 Sık Kullanılan Birimler")
col1, col2 = st.columns(2)

with col1:
    if st.button("🩸 KAN ALMA", use_container_width=True):
        birim_sec("Kan Alma Birimi")
        st.rerun()
    if st.button("📋 EVRAK KAYIT", use_container_width=True):
        birim_sec("Evrak Kayıt / Vezne")
        st.rerun()
    if st.button("🚻 WC / LAVABO", use_container_width=True):
        birim_sec("Tuvaletler / Lavabolar")
        st.rerun()
    if st.button("🗂️ HASTA KAYIT", use_container_width=True):
        birim_sec("Hasta Kayıt")
        st.rerun()

with col2:
    if st.button("🏥 SAĞLIK KURULU", use_container_width=True):
        birim_sec("Sağlık Kurulu")
        st.rerun()
    if st.button("🛗 ASANSÖR", use_container_width=True):
        birim_sec("Asansör")
        st.rerun()
    if st.button("📝 S.K. KAYIT", use_container_width=True):
        birim_sec("Sağlık Kurulu Kayıt Birimi")
        st.rerun()

# ==============================================================================
# 🎙️ SESLİ ARAMA (WEB SPEECH API - KESİN EŞLEŞME MİMARİSİ)
# ==============================================================================
st.write("---")
st.write("### 🔍 Birim Arama / Sesle Konuş")

col_input, col_mic = st.columns([3, 1])

with col_mic:
    st.components.v1.html("""
    <div style="text-align: center; font-family: sans-serif; padding-top: 5px;">
        <button id="mic-btn" onclick="sesliAramaBaslat()" style="background-color: #ff4b4b; color: white; border: none; padding: 12px 10px; font-size: 14px; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
            🎙️ Konuş
        </button>
        <p id="mic-status" style="margin-top: 4px; font-size: 10px; color: #666;"></p>
    </div>
    <script>
        const tarifVeritabani = {
            "heyet çocuk çözger poliklinik": "Birinci Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun ilerisinde sol tarafta görme alanının yanında yer alır.",
            "heyet fizik tedavi poliklinik": "Zemin Kat - Ana girişten girdikten sonra sola dönün.  Koridorun sol tarafında yer alır.",
            "heyet kbb poliklinik": "Zemin Kat - Ana girişten girdikten sonra sola dönün. Koridorun sağ tarafında Heyet Ortopedi Polikliniğin yanında yer alır.",
            "heyet ortopedi poliklinik": "Zemin Kat - Ana girişten girdikten sonra sola dönün. Koridorun sağ tarafında kulak burun boğaz polikliniğin yanında yer alır.",
            "heyet çocuk psikiyatri poliklinik": "Birinci Kat - Ana girişten girdikten sonra sola dönün. Ön merdivenleri çıkınca sola dönün. Sol tarafınızdaki küçük koridorun sonuna doğru ilerleyin veya arka merdivenlerden çıkınca sola dönün sağ tarafınızda yer alır.",
            "kan alma birimi": "Zemin Kat - Ana girişten girdikten sonra sağa dönün. Sağınızdaki ilk odadır.",
            "sağlık kurulu": "Zemin Kat - Ana girişten girdikten sonra sağa dönün Koridorun sonundaki geniş alanda yer almaktadır.",
            "sağlık kurulu kayıt birimi": "Zemin Kat - Girişten hemen sonra sola dönün. Sol taraftaki etrafı kapalı yerdir.",
            "ön merdivenler": "Zemin Kat - Girişten girdikten sonra sola dönün, koridorun sonuna doğru sol tarafta yer alır.",
            "arka çıkış": "Zemin Kat - Koridordan sola dönün. Ön merdivenleri geçip sola dönerek arka çıkış kapısına ulaşabilirsiniz.",
            "heyet genel cerrahi poliklinik": "Birinci Kat - Merdivenlerden çıktıysanız sağa, asansörden çıktıysanız sola dönün.Nöroloji polikliğinin yanında yer alır.",
            "heyet cildiye poliklinikleri": "Birinci Kat - Merdivenlerden çıkınca sağa dönün, asansörden çıkınca sola dönün. Heyet Nöroloji polikliniğinin karşısında yer alır.",
            "fizik tedavi 2 poliklinik": "Birinci Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun sonuna doğru sağ tarafta Heyet Dahiliye polikliniğin yanında yer alır.",
            "fizik tedavi 3 poliklinik": "Birinci Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun sonuna doğru sol tarafta Heyet Nöroloji polikliniğin yanında yer alır.",
            "heyet nöroloji poliklinik": "Birinci Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun sonuna doğru sol tarafta Heyet Kardiyoloji polikliğinin yanında yer alır.",
            "görme alanı ölçüm odası": "Birinci Kat -  Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun sonuna doğru sol tarafta Heyet Çözger polikliniğin yanında yer alır.",
            "heyet dahiliye poliklinik": "Birinci Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun sonunda sağ tarafta Fizik Tedavi 2 polikliniğin yanında yer alır.",
            "heyet göğüs hastalıkları poliklinik": "Birinci Kat - Merdivenlerden çıktıysanız karşınızda, asansörden çıktıysanız sola dönün. Nöroloji polikliniğin yanında yer alır.",
            "heyet göz poliklinik": "Birinci Kat - Merdivenlerden veya asansörden çıktıysanız sola dönün. Koridorun sonunda sağ tarafta, Göz Ölçüm odasının yanında yer alır.",
            "konuşma terapisti": "Birinci Kat - Ana girişten girdikten sonra sola dönün. Merdivenleri çıkınca sola dönün. Sol tarafınızdaki küçük koridorun sonuna doğru ilerleyin veya arka merdivenlerden çıkınca sola dönün. İleride Sol tarafınızda Sabim Cimer odasını geçince yer alır.",
            "heyet kardiyoloji poliklinik": "Birinci Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun sonunda sol tarafta Heyet Nöroloji polikliniğin yanında yer alır.",
            "heyet üroloji poliklinik": "Birinci Kat - Merdivenlerden veya asansörden çıktıysanız sola dönün. Koridorun sonunda sol tarafta, Heyet Göz polikliniğin karşısında yer alır",
            "işitme testi odio": "Birinci Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun ilerisinde sağ tarafta Emzirme odasının yanında yer alır.",
            "çocuk gelişim birimi": "Birinci Kat - Ana girişten girdikten sonra sola dönün. Merdivenleri çıkınca sola dönün. Sol tarafınızdaki küçük koridorun hemen sağında veya arka merdivenlerden çıkınca tam karşınızda tarafınızda yer alır.",
            "çocuk evde sağlık birimi": "Birinci Kat - Ana girişten girdikten sonra sola dönün. Ön merdivenleri çıkınca sola dönün. Sol tarafınızdaki küçük koridorun sonunda sağ tarafta veya arka merdivenlerden çıkınca sola dönün koridorun sonunda sağ tarafınızda yer alır.",
            "heyet psikolog": "Ana girişten girdikten sonra sola dönün. Ön merdivenleri çıkınca sola dönün. Sol tarafınızdaki küçük koridorun ilerisinde sol tarafta veya arka merdivenlerden çıkınca sola dönün koridorun solunda yer alır.",
            "göz oct odası": "Birinci Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun ilerisinde sağ tarafta Fizik Tedavi 2 polikliniğin yanında yer alır.",
            "göz ölçüm": "Birinci Kat - Merdivenlerden veya asansörden çıktıysanız sola dönün. Koridorun sağ tarafında, Heyet Göz polikliniğin yanında yer alır.",
            "nöroloji poliklinik 1": "Birinci Kat - Merdivenlerden çıktıysanız sağa, asansörden çıktıysanız sola dönün. Heyet Genel Cerrahi polikliniğin yanında yer alır.",
            "heyet psikiyatri poliklinikleri": "Birinci Kat - Merdivenlerden çıktıysanız sağa dönün ileride solda, asansörden çıktıysanız tam karşınızda yer alır.",
            "sabim cimer birimi": "Birinci Kat - Ana girişten girdikten sonra sola dönün. Ön merdivenleri çıkınca sola dönün. Sol tarafınızdaki küçük koridorun sonuna doğru ilerleyin veya arka merdivenlerden çıkınca sola dönün. Sol tarafınızda Heyet Psikolog odasını geçince yer alır.",
            "solunum fonksiyon sft birimi": "Birinci Kat - Ana girişten girdikten sonra sola dönün. Ön merdivenleri çıkınca sola dönün. Sol tarafınızdaki küçük koridorun sonuna doğru ilerleyin veya arka merdivenlerden çıkınca sola dönün. Sağ tarafınızda yer alır.",
            "evrak kayıt vezne": "Zemin Kat - Ana girişten girince tam karşınızda yer alır.",
            "hasta kayıt": "Ana girişte sol tarafta yer alır.",
            "evde sağlık hizmetleri birimi": "Zemin Katta olup girişi binanın kuzey yönündedir.",
            "röntgen görüntüleme diğer bina": "Röntgen birimi bu binada değildir. Arka kapıdan çıkınca sola dönün, 30 metre sonra sağa dönün, ileride sağ tarafta yer alır.",
            "asansör": "Zemin katta Hasta Kayıt bankosunu geçince sol tarafta, 1. katta binanın tam orta kesiminde yer alır.",
            "emzirme odası": "Birinci Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun ilerisinde sağ tarafta İşitme testi Odio odasının yanında yer alır. ",
            "tuvaletler lavabolar": "Zemin Katta - Ana girişten sonra sola dönün. Koridorun sonunda yer alır.",
            "ekg birimi": "Birinci kat - Merdivenlerden veya asansörden çıkınca sağa dönün. Heyet Psikiyatri poliklinikleri karşısında yer alır."
        };

        const esAnlamlilar = {
            "kan": "kan alma birimi", "tahlil": "kan alma birimi", "laboratuvar": "kan alma birimi",
            "wc": "tuvaletler lavabolar", "lavabo": "tuvaletler lavabolar", "tuvalet": "tuvaletler lavabolar",
            "heyet": "sağlık kurulu", "rapor": "sağlık kurulu",
            "kulak": "heyet kbb poliklinik", "kbb": "heyet kbb poliklinik",
            "göz": "heyet göz poliklinik", "kalp": "heyet kardiyoloji poliklinik", "kardiyoloji": "heyet kardiyoloji poliklinik",
            "çocuk": "heyet çocuk çözger poliklinik", "fizik": "heyet fizik tedavi poliklinik",
            "göğüs": "heyet göğüs hastalıkları poliklinik", "üroloji": "heyet üroloji poliklinik",
            "cerrahi": "heyet genel cerrahi poliklinik", "röntgen": "röntgen görüntüleme diğer bina",
            "film": "röntgen görüntüleme diğer bina", "işitme": "işitme testi odio",
            "odio": "işitme testi odio", "dahiliye": "heyet dahiliye poliklinik",
            "nöroloji": "heyet nöroloji poliklinik", "ortopedi": "heyet ortopedi poliklinik",
            "psikiyatri": "heyet psikiyatri poliklinik", "cimer": "sabim cimer birimi", "sft": "solunum fonksiyon sft birimi"
        };

        function sesliOkuyucu(metin) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance(metin);
                msg.lang = 'tr-TR';
                msg.rate = 1.0;
                window.speechSynthesis.speak(msg);
            }
        }

        function sesliAramaBaslat() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const statusEl = document.getElementById('mic-status');
            const btnEl = document.getElementById('mic-btn');

            if (!SpeechRecognition) {
                alert("Tarayıcınız sesli aramayı desteklemiyor.");
                return;
            }

            const recognition = new SpeechRecognition();
            recognition.lang = 'tr-TR';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.onstart = function() {
                btnEl.style.backgroundColor = '#28a745';
                btnEl.innerText = " Dinliyor...";
                statusEl.innerText = "Konuşun...";
            };

            recognition.onresult = function(event) {
                const speechResult = event.results[0][0].transcript.toLowerCase().replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").trim();
                statusEl.innerText = "Bulundu: " + speechResult;
                btnEl.style.backgroundColor = '#ff4b4b';
                btnEl.innerText = "🎙️ Konuş";
                
                let bulunanBirim = "";
                let tarif = "";

                if (esAnlamlilar[speechResult]) {
                    bulunanBirim = esAnlamlilar[speechResult];
                } else if (tarifVeritabani[speechResult]) {
                    bulunanBirim = speechResult;
                } else {
                    // Kelime skoru tabanlı en iyi eşleşmeyi bul
                    let kelimeler = speechResult.split(" ");
                    let maxOrtak = 0;
                    for (let birim in tarifVeritabani) {
                        let birimKelimeleri = birim.split(" ");
                        let ortak = kelimeler.filter(k => birimKelimeleri.includes(k)).length;
                        if (ortak > maxOrtak) {
                            maxOrtak = ortak;
                            bulunanBirim = birim;
                        }
                    }
                }

                if (bulunanBirim && tarifVeritabani[bulunanBirim]) {
                    tarif = bulunanBirim + " için yol tarifi. " + tarifVeritabani[bulunanBirim];
                    sesliOkuyucu(tarif);
                } else {
                    sesliOkuyucu("Aradığınız birim sistemde bulunamadı. Lütfen tekrar deneyin.");
                }

                const url = new URL(window.parent.location.href);
                url.searchParams.set('ses_arama', speechResult);
                window.parent.location.href = url.toString();
            };

            recognition.onerror = function(event) {
                btnEl.style.backgroundColor = '#ff4b4b';
                btnEl.innerText = "🎙️ Konuş";
                statusEl.innerText = "Hata: " + event.error;
            };

            recognition.onend = function() {
                btnEl.style.backgroundColor = '#ff4b4b';
                btnEl.innerText = "🎙️ Konuş";
            };

            try {
                recognition.start();
            } catch(e) {
                statusEl.innerText = "İzin hatası.";
            }
        }
    </script>
    """, height=70)

with col_input:
    metin_input = st.text_input("Birim arayın:", placeholder="Örn: Dahiliye, Kan, Röntgen...", key="arama_input", label_visibility="collapsed")

if metin_input and metin_input != st.session_state.get("son_metin", ""):
    st.session_state["son_metin"] = metin_input
    if akilli_arama_isle(metin_input):
        st.rerun()

# ==============================================================================
# 🗂️ KATEGORİ VE LİSTELEME
# ==============================================================================
st.write("---")
kategori = st.radio(
    "Kategori", 
    ["🏥 Resmi Poliklinikler / Odalar", "⚙️ Genel ve İdari Birimler"], 
    key="kategori",
    horizontal=True, 
    label_visibility="collapsed"
)

if "Poliklinikler" in kategori:
    liste = ["Seçim Yapınız..."] + list(POLIKLINIKLER.keys())
    secili_val = st.session_state.get("secilen_birim", "Seçim Yapınız...")
    idx = liste.index(secili_val) if secili_val in liste else 0
    
    secim = st.selectbox("POLİKLİNİK SEÇİNİZ:", liste, index=idx, key="sb_polk")
    if secim != st.session_state.get("secilen_birim") and secim != "Seçim Yapınız...":
        st.session_state["secilen_birim"] = secim
        st.rerun()
else:
    liste = ["Seçim Yapınız..."] + list(DIGER_ALANLAR.keys())
    secili_val = st.session_state.get("secilen_birim", "Seçim Yapınız...")
    idx = liste.index(secili_val) if secili_val in liste else 0
    
    secim = st.selectbox("DİĞER BİRİMLERİ SEÇİNİZ:", liste, index=idx, key="sb_diger")
    if secim != st.session_state.get("secilen_birim") and secim != "Seçim Yapınız...":
        st.session_state["secilen_birim"] = secim
        st.rerun()

# ==============================================================================
# 🎯 SONUÇ GÖSTERİMİ, SESLENDİRME & KROKİ
# ==============================================================================
aktif_secim = st.session_state["secilen_birim"]

if aktif_secim != "Seçim Yapınız...":
    tum_liste = {**POLIKLINIKLER, **DIGER_ALANLAR}
    if aktif_secim in tum_liste:
        bilgi = tum_liste[aktif_secim]
        
        if bilgi['fancy']:
            st.error(f"🎯 **Hedef:** {aktif_secim}")
            st.error(f"🚶 **Yönlendirme:** {bilgi['tarif']}")
            otomatik_sesli_oku(bilgi['tarif'])
        else:
            st.success(f"🎯 **Hedef:** {aktif_secim}")
            st.warning(f"🚶 **Yol Tarifi:** {bilgi['tarif']}")
            otomatik_sesli_oku(f"{aktif_secim} için yol tarifi. {bilgi['tarif']}")
            
        if bilgi.get('kroki'):
                kroki_goster(bilgi['kroki'])
     
st.caption("🤖 Barajyolu Ek Hizmet Binası Mobil Dijital Yönlendirme Sistemi (Engin PEKDEMİR)")

