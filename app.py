import streamlit as st
import os
import re
import unicodedata
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
# 📱 MOBİL İYİLEŞTİRME STİLLERİ (CSS)
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
    "Heyet Göz Poliklinik": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Merdivenlerden veya asansörden çıktıysanız sola dönün. Koridorun sonunda sağ tarafta, Göz Ölçüm odasının yanında yer alır.",
        "kroki": "heyet_goz_polk_yol_tarifi.png"
    },
    "Göz Ölçüm": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Merdivenlerden veya asansörden çıktıysanız sola dönün. Koridorun sağ tarafında, Heyet Göz polikliğinin yanında yer alır.",
        "kroki": "goz_olcum_yol_tarifi.png"
    },
    "Heyet Göğüs Hastalıkları Poliklinik": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Merdivenlerden çıktıysanız karşınızda, asansörden çıktıysanız sola dönün. Nöroloji polikliğinin yanında yer alır.",
        "kroki": "heyet_gogus_hastaliklari_polk_yol_tarifi.png"
    },
    "Nöroloji Poliklinik 1": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Merdivenlerden çıktıysanız sağa, asansörden çıktıysanız sola dönün. Heyet Genel Cerrahi polikliğinin yanında yer alır.",
        "kroki": "noroloji_polk_yol_tarifi.png"
    },
    "Heyet Genel Cerrahi Poliklinik": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Merdivenlerden çıktıysanız sağa, asansörden çıktıysanız sola dönün. Nöroloji polikliğinin yanında yer alır.",
        "kroki": "heyet_genel_cerrahi_polk_yol_tarifi.png"
    },
    "Heyet Psikiyatri Poliklinikleri": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Merdivenlerden çıktıysanız sağa dönün ileride solda, asansörden çıktıysanız tam karşınızda yer alır.",
        "kroki": "heyet_psikiyatri_polk_yol_tarifi.png"
    },
    "Heyet Çocuk (Çözger) Poliklinik": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun ilerisinde sol tarafta görme alanının yanında yer alır.",
        "kroki": "heyet_cozger_polk_yol_tarifi.png"
    },
    "Görme Alanı Ölçüm Odası": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun sonuna doğru sol tarafta Heyet Çözger polikliğinin yanında yer alır.",
        "kroki": "gorme_alani_yol_tarifi.png"
    },
    "Fizik Tedavi 3 Poliklinik": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun sonuna doğru sol tarafta Heyet Nöroloji polikliğinin yanında yer alır.",
        "kroki": "fizik_tedavi_polk3_yol_tarifi.png"
    },
    "Heyet Nöroloji Poliklinik": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun sonuna doğru sol tarafta Heyet Kardiyoloji polikliğinin yanında yer alır.",
        "kroki": "heyet_noroloji_polk_yol_tarifi.png"
    },
    "Heyet Kardiyoloji Poliklinik": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun sonunda sol tarafta Heyet Nöroloji polikliğinin yanında yer alır.",
        "kroki": "heyet_kardiyoloji_polk_yol_tarifi.png"
    },
    "Heyet Dahiliye Poliklinik": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun sonunda sağ tarafta Fizik Tedavi 2 polikliğinin yanında yer alır.",
        "kroki": "heyet_dahiliye_polk_yol_tarifi.png"
    },
    "Fizik Tedavi 2 Poliklinik": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun sonuna doğru sağ tarafta Heyet Dahiliye polikliğinin yanında yer alır.",
        "kroki": "fizik_tedavi_polk2_yol_tarifi.png"
    },
    "Göz OCT Odası": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun ilerisinde sağ tarafta Fizik Tedavi 2 polikliğinin yanında yer alır.",
        "kroki": "goz_oct_yol_tarifi.png"
    },
    "İşitme Testi (Odio)": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun ilerisinde sağ tarafta Emzirme odasının yanında yer alır.",
        "kroki": "isitme_testi_birimi_yol_tarifi.png"
    },
    "Emzirme Odası": {
        "fancy": False, "kat": "1", 
        "tarif": "1. Kat - Merdivenlerden veya asansörden çıkınca sağa dönün, koridorun ilerisinde sağ tarafta İşitme testi Odio odasının yanında yer alır.", 
        "kroki": "emzirme_odasi_yol_tarifi.png"
    },
    "Ekg Birimi": {
        "fancy": False, "kat": "1", 
        "tarif": "1. Kat - Merdivenlerden veya asansörden çıkınca sağa dönün. Heyet Psikiyatri poliklinikleri karşısında yer alır.", 
        "kroki": "ekg_yol_tarifi.png"
    },
    "Heyet Cildiye Poliklinikleri": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Merdivenlerden çıkınca sağa dönün, asansörden çıkınca sola dönün. Heyet Nöroloji polikliniğinin karşısında yer alır.",
        "kroki": "heyet_cildiye_polk_yol_tarifi.png"
    },
    "Heyet Üroloji Poliklinik": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Merdivenlerden veya asansörden çıktıysanız sola dönün. Koridorun sonunda sol tarafta, Heyet Göz polikliğinin karşısında yer alır.",
        "kroki": "heyet_uroloji_polk_yol_tarifi.png"
    },
    "Çocuk Gelişim Birimi": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Ana girişten girdikten sonra sola dönün. Merdivenleri çıkınca sola dönün. Sol tarafınızdaki küçük koridorun hemen sağında veya arka merdivenlerden çıkınca tam karşınızda yer alır.",
        "kroki": "cocuk_gelisim_yol_tarifi.png"
    },
    "Solunum Fonksiyon (SFT) Birimi": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Ana girişten girdikten sonra sola dönün. Ön merdivenleri çıkınca sola dönün. Sol tarafınızdaki küçük koridorun doğru ilerleyin veya arka merdivenlerden çıkınca sola dönün. Sağ tarafınızda yer alır.",
        "kroki": "solunum_fonksiyon_yol_tarifi.png"
    },
    "Heyet Çocuk Psikiyatri Poliklinik": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Ana girişten girdikten sonra sola dönün. Ön merdivenleri çıkınca sola dönün. Sol tarafınızdaki küçük koridorun sonuna doğru ilerleyin veya arka merdivenlerden çıkınca sola dönün sağ tarafınızda yer alır.",
        "kroki": "heyet_cocuk_psikiyatri_polk_yol_tarifi.png"
    },
    "Çocuk Evde Sağlık Birimi": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Ana girişten girdikten sonra sola dönün. Ön merdivenleri çıkınca sola dönün. Sol tarafınızdaki küçük koridorun sonunda sağ tarafta veya arka merdivenlerden çıkınca sola dönün koridorun sonunda sağ tarafınızda yer alır.",
        "kroki": "cocuk_evde_bakim_yol_tarifi.png"
    },
    "Konuşma Terapisti": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Ana girişten girdikten sonra sola dönün. Merdivenleri çıkınca sola dönün. Sol tarafınızdaki küçük koridorun sonuna doğru ilerleyin veya arka merdivenlerden çıkınca sola dönün. İleride Sol tarafınızda Sabim Cimer odasını geçince yer alır.",
        "kroki": "konusma_terapisti_yol_tarifi.png"
    },
    "Sabim Cimer Birimi": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Ana girişten girdikten sonra sola dönün. Ön merdivenleri çıkınca sola dönün. Sol tarafınızdaki küçük koridorun sonuna doğru ilerleyin veya arka merdivenlerden çıkınca sola dönün. Sol tarafınızda Heyet Psikolog odasını geçince yer alır.",
        "kroki": "sabim_cimer_yol_tarifi.png"
    },
    "Heyet Psikolog": {
        "fancy": False, "kat": "1",
        "tarif": "1. Kat - Ana girişten girdikten sonra sola dönün. Ön merdivenleri çıkınca sola dönün. Sol tarafınızdaki küçük koridorun ilerisinde sol tarafta veya arka merdivenlerden çıkınca sola dönün koridorun solunda yer alır.",
        "kroki": "heyet_psikolog_yol_tarifi.png"
    },
    "Heyet Fizik Tedavi Poliklinik": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Ana girişten girdikten sonra sola dönün. Koridorun sol tarafında yer alır.",
        "kroki": "heyet_fizik_tedavi_polk_yol_tarifi.png"
    },
    "Heyet Kulak Burun Boğaz Poliklinik": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Ana girişten girdikten sonra sola dönün. Koridorun sağ tarafında Heyet Ortopedi Polikliniğin yanında yer alır.",
        "kroki": "heyet_kbb_polk_yol_tarifi.png"
    },
    "Heyet Ortopedi Poliklinik": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Ana girişten girdikten sonra sola dönün. Koridorun sağ tarafında kulak burun boğaz polikliğinin yanında yer alır.",
        "kroki": "heyet_ortopedi_polk_yol_tarifi.png"
    },
    "Kan Alma Birimi": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Ana girişten girdikten sonra sağa dönün. Sağınızdaki ilk odadır.",
        "kroki": "kan_alma_yol_tarifi.png"
    },
    "Sağlık Kurulu": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Ana girişten girdikten sonra sağa dönün. Koridorun sonundaki geniş alanda yer almaktadır.",
        "kroki": "saglik_kurulu_yol_tarifi.png"
    },
    "Sağlık Kurulu Kayıt Birimi": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Girişten hemen sonra sola dönün. Sol taraftaki etrafı kapalı yerdir.",
        "kroki": "saglik_kurulu_kayit_yol_tarifi.png"
    },
    "Ön Merdivenler": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Girişten girdikten sonra sola dönün, koridorun sonuna doğru sol tarafta yer alır.",
        "kroki": "on_merdivenler_yol_tarifi.png"
    },
    "Arka Çıkış": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Koridordan sola dönün. Ön merdivenleri geçip sola dönerek arka çıkış kapısına ulaşabilirsiniz.",
        "kroki": "arka_cikis_yol_tarifi.png"
    }
}

DIGER_ALANLAR = {
    "Evrak Kayıt / Vezne": {
        "fancy": False, "kat": "zemin", 
        "tarif": "Zemin Kat - Ana girişten tam karşınızda.", 
        "kroki": "evrak_kayit_vezne_yol_tarifi.png"
    },
    "Hasta Kayıt": {
        "fancy": False, "kat": "zemin", 
        "tarif": "Zemin Kat - Ana girişte sol tarafta yer alır.", 
        "kroki": "hasta_kayit_yol_tarifi.png"
    },
    "Evde Sağlık Hizmetleri Birimi": {
        "fancy": False, "kat": "zemin", 
        "tarif": "Zemin Katta olup girişi binanın kuzey yönündedir.", 
        "kroki": "evde_saglik_hizmetleri_yol_tarifi.png"
    },
    "Röntgen / Görüntüleme (DİĞER BİNA)": {
        "fancy": True, "kat": "", 
        "tarif": "Röntgen birimi bu binada değildir. Arka kapıdan çıkınca sola dönün, 30 metre sonra sağa dönün, ileride sağ tarafta yer alır.", 
        "kroki": "rontgen_yol_tarifi.png"
    },
    "Asansör": {
        "fancy": False, "kat": "zemin", 
        "tarif": "Zemin katta Hasta Kayıt bankosunu geçince sol tarafta, 1. katta binanın tam orta kesiminde yer alır.", 
        "kroki": "asansor_yol_tarifi.png"
    },
    "Tuvaletler / Lavabolar": {
        "fancy": False, "kat": "zemin", 
        "tarif": "Zemin Katta: Ana girişten sonra sola dönün. Koridorun sonunda yer alır.", 
        "kroki": "tuvaletler_yol_tarifi.png"
    }
}

ES_ANLAMLILAR = {
    "kan": "Kan Alma Birimi", "tahlil": "Kan Alma Birimi", "laboratuvar": "Kan Alma Birimi",
    "wc": "Tuvaletler / Lavabolar", "lavabo": "Tuvaletler / Lavabolar", "tuvalet": "Tuvaletler / Lavabolar",
    "heyet": "Sağlık Kurulu", "rapor": "Sağlık Kurulu",
    "kulak": "Heyet Kulak Burun Boğaz Poliklinik", "kbb": "Heyet Kulak Burun Boğaz Poliklinik",
    "goz": "Heyet Göz Poliklinik", "kalp": "Heyet Kardiyoloji Poliklinik", "kardiyoloji": "Heyet Kardiyoloji Poliklinik",
    "cocuk": "Heyet Çocuk (Çözger) Poliklinik", "fizik": "Heyet Fizik Tedavi Poliklinik",
    "gogus": "Heyet Göğüs Hastalıkları Poliklinik", "uroloji": "Heyet Üroloji Poliklinik",
    "cerrahi": "Heyet Genel Cerrahi Poliklinik", "rontgen": "Röntgen / Görüntüleme (DİĞER BİNA)",
    "film": "Röntgen / Görüntüleme (DİĞER BİNA)", "isitme": "İşitme Testi (Odio)",
    "odio": "İşitme Testi (Odio)", "dahiliye": "Heyet Dahiliye Poliklinik",
    "noroloji": "Heyet Nöroloji Poliklinik", "nöroloji": "Heyet Nöroloji Poliklinik", 
    "ortopedi": "Heyet Ortopedi Poliklinik",
    "psikiyatri": "Heyet Psikiyatri Poliklinikleri", "cimer": "Sabim Cimer Birimi", 
    "sft": "Solunum Fonksiyon (SFT) Birimi",
    "ekg": "Ekg Birimi"
}

# ==============================================================================
# 🧩 OTURUM DURUMU (SESSION STATE) BAŞLATMA
# ==============================================================================
if "secilen_birim" not in st.session_state:
    st.session_state["secilen_birim"] = "Seçim Yapınız..."
if "kategori_secimi" not in st.session_state:
    st.session_state["kategori_secimi"] = "🏥 Resmi Poliklinikler / Odalar"
if "son_metin" not in st.session_state:
    st.session_state["son_metin"] = ""

# ==============================================================================
# 🛠️ YARDIMCI FONKSİYONLAR
# ==============================================================================
def normalize_text(text):
    """Türkçe karakterleri ve özel karakterleri normalize eder"""
    text = text.lower().strip()
    text = text.replace("ı", "i").replace("ş", "s").replace("ç", "c")
    text = text.replace("ğ", "g").replace("ü", "u").replace("ö", "o")
    text = re.sub(r'[^\w\s]', '', text)
    return text

def otomatik_sesli_oku(metin):
    if metin and metin.strip():
        temiz_metin = metin.replace("1. Kat", "Birinci Kat").replace("'", "\\'").replace('"', '\\"')
        # Benzersiz bir element ID'si kullanarak tekrarları önle
        import hashlib
        metin_id = hashlib.md5(metin.encode()).hexdigest()[:8]
        js_kodu = f"""
        <div id="tts-{metin_id}"></div>
        <script>
            (function() {{
                var container = document.getElementById('tts-{metin_id}');
                if (!container || container.dataset.played === 'true') return;
                container.dataset.played = 'true';
                
                function konusData() {{
                    if ('speechSynthesis' in window) {{
                        window.speechSynthesis.cancel();
                        var msg = new SpeechSynthesisUtterance('{temiz_metin}');
                        msg.lang = 'tr-TR';
                        msg.rate = 0.95;
                        window.speechSynthesis.speak(msg);
                    }}
                }}
                setTimeout(konusData, 500);
            }})();
        </script>
        """
        st.components.v1.html(js_kodu, height=0)

def kroki_goster(kroki_dosya_adi):
    if not kroki_dosya_adi:
        return

    aranan_tam = normalize_text(kroki_dosya_adi)
    aranan_govde = Path(aranan_tam).stem
    
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

    for dizin in arama_dizinleri:
        if dizin.exists():
            try:
                for dosya in dizin.rglob("*"):
                    if dosya.is_file() and dosya.suffix.lower() in gecerli_uzantilar:
                        dosya_adi_norm = normalize_text(dosya.name)
                        dosya_govde_norm = normalize_text(dosya.stem)
                        
                        if dosya_adi_norm == aranan_tam or dosya_govde_norm == aranan_govde:
                            bulunan_dosya = dosya
                            break
                        
                        if aranan_govde in dosya_govde_norm or dosya_govde_norm in aranan_govde:
                            bulunan_dosya = dosya
                            break
            except Exception:
                pass
        if bulunan_dosya:
            break

    if bulunan_dosya:
        try:
            image = Image.open(bulunan_dosya)
            st.image(image, caption=f"🗺️ {st.session_state['secilen_birim']} Krokisi", use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Görsel açılamadı ({bulunan_dosya.name}): {e}")
    else:
        st.info(f"ℹ️ Kroki dosyası bulunamadı: `{kroki_dosya_adi}`")

def birim_sec(birim_adi):
    st.session_state["secilen_birim"] = birim_adi
    if birim_adi in DIGER_ALANLAR:
        st.session_state["kategori_secimi"] = "⚙️ Genel ve İdari Birimler"
    elif birim_adi in POLIKLINIKLER:
        st.session_state["kategori_secimi"] = "🏥 Resmi Poliklinikler / Odalar"

def akilli_arama_isle(gelen_metin):
    if not gelen_metin:
        return
    temiz = normalize_text(gelen_metin)
    tum_birimler = {**POLIKLINIKLER, **DIGER_ALANLAR}

    # 1. Tam eş anlamlı kelime kontrolü
    if temiz in ES_ANLAMLILAR:
        birim_sec(ES_ANLAMLILAR[temiz])
        return

    # 2. Tam birim adı eşleşmesi
    for birim in tum_birimler:
        if temiz == normalize_text(birim):
            birim_sec(birim)
            return

    # 3. Kelime bazlı en iyi eşleşme (Skorlama mantığı)
    kelimeler = temiz.split()
    en_iyi_eslesme = None
    max_ortak_kelime = 0

    for birim in tum_birimler:
        birim_kelimeleri = normalize_text(birim).split()
        ortak = sum(1 for k in kelimeler if k in birim_kelimeleri)
        if ortak > max_ortak_kelime:
            max_ortak_kelime = ortak
            en_iyi_eslesme = birim

    if en_iyi_eslesme and max_ortak_kelime > 0:
        birim_sec(en_iyi_eslesme)
        return

    # 4. Kısmi eş anlamlı kelime arama
    for k in kelimeler:
        if k in ES_ANLAMLILAR:
            birim_sec(ES_ANLAMLILAR[k])
            return

    st.toast(f"❌ '{gelen_metin}' için sonuç bulunamadı.", icon="⚠️")

# ==============================================================================
# 🖥️ ARAYÜZ BAŞLIK VE KARŞILAMA
# ==============================================================================
st.title("🏥 SDH BARAJ YOLU EK BİNASI")
st.caption("📱 Mobil Sesli Dijital Yönlendirme Sistemi")
st.info(f"📍 **Bulunduğunuz Konum:** {baslangic_noktasi}")

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
# 🎙️ SESLİ ARAMA (WEB SPEECH API)
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
            "heyet goz poliklinik": "Birinci Kat - Merdivenlerden veya asansorden ciktinizsa sola donun. Koridorun sonunda sag tarafta, Goz Olcum odasinin yaninda yer alir.",
            "goz olcum": "Birinci Kat - Merdivenlerden veya asansorden ciktinizsa sola donun. Koridorun sag tarafinda, Heyet Goz polikliniginin yaninda yer alir.",
            "heyet gogus hastaliklari poliklinik": "Birinci Kat - Merdivenlerden ciktinizsa karsinizda, asansorden ciktinizsa sola donun. Noroloji polikliniginin yaninda yer alir.",
            "noroloji poliklinik 1": "Birinci Kat - Merdivenlerden ciktinizsa saga, asansorden ciktinizsa sola donun. Heyet Genel Cerrahi polikliniginin yaninda yer alir.",
            "heyet genel cerrahi poliklinik": "Birinci Kat - Merdivenlerden ciktinizsa saga, asansorden ciktinizsa sola donun. Noroloji polikliniginin yaninda yer alir.",
            "heyet psikiyatri poliklinikleri": "Birinci Kat - Merdivenlerden ciktinizsa saga donun ileride solda, asansorden ciktinizsa tam karsinizda yer alir.",
            "heyet cocuk cozger poliklinik": "Birinci Kat - Merdivenlerden veya asansorden cikinca saga donun, koridorun ilerisinde sol tarafta gorme alaninin yaninda yer alir.",
            "gorme alani olcum odasi": "Birinci Kat - Merdivenlerden veya asansorden cikinca saga donun, koridorun sonuna dogru sol tarafta Heyet Cozger polikliniginin yaninda yer alir.",
            "fizik tedavi 3 poliklinik": "Birinci Kat - Merdivenlerden veya asansorden cikinca saga donun, koridorun sonuna dogru sol tarafta Heyet Noroloji polikliniginin yaninda yer alir.",
            "heyet noroloji poliklinik": "Birinci Kat - Merdivenlerden veya asansorden cikinca saga donun, koridorun sonuna dogru sol tarafta Heyet Kardiyoloji polikliniginin yaninda yer alir.",
            "heyet kardiyoloji poliklinik": "Birinci Kat - Merdivenlerden veya asansorden cikinca saga donun, koridorun sonunda sol tarafta Heyet Noroloji polikliniginin yaninda yer alir.",
            "heyet dahiliye poliklinik": "Birinci Kat - Merdivenlerden veya asansorden cikinca saga donun, koridorun sonunda sag tarafta Fizik Tedavi 2 polikliniginin yaninda yer alir.",
            "fizik tedavi 2 poliklinik": "Birinci Kat - Merdivenlerden veya asansorden cikinca saga donun, koridorun sonuna dogru sag tarafta Heyet Dahiliye polikliniginin yaninda yer alir.",
            "goz oct odasi": "Birinci Kat - Merdivenlerden veya asansorden cikinca saga donun, koridorun ilerisinde sag tarafta Fizik Tedavi 2 polikliniginin yaninda yer alir.",
            "isitme testi odio": "Birinci Kat - Merdivenlerden veya asansorden cikinca saga donun, koridorun ilerisinde sag tarafta Emzirme odasinin yaninda yer alir.",
            "emzirme odasi": "Birinci Kat - Merdivenlerden veya asansorden cikinca saga donun, koridorun ilerisinde sag tarafta Isitme testi Odio odasinin yaninda yer alir.",
            "ekg birimi": "Birinci Kat - Merdivenlerden veya asansorden cikinca saga donun. Heyet Psikiyatri poliklinikleri karsisinda yer alir.",
            "heyet cildiye poliklinikleri": "Birinci Kat - Merdivenlerden cikinca saga donun, asansorden cikinca sola donun. Heyet Noroloji polikliniginin karsisinda yer alir.",
            "heyet uroloji poliklinik": "Birinci Kat - Merdivenlerden veya asansorden ciktinizsa sola donun. Koridorun sonunda sol tarafta, Heyet Goz polikliniginin karsisinda yer alir.",
            "cocuk gelisim birimi": "Birinci Kat - Ana giristen girdikten sonra sola donun. Merdivenleri cikinca sola donun. Sol tarafinizdaki kucuk koridorun hemen saginda veya arka merdivenlerden cikinca tam karsinizda yer alir.",
            "solunum fonksiyon sft birimi": "Birinci Kat - Ana giristen girdikten sonra sola donun. On merdivenleri cikinca sola donun. Sol tarafinizdaki kucuk koridorun dogru ilerleyin veya arka merdivenlerden cikinca sola donun. Sag tarafinizda yer alir.",
            "heyet cocuk psikiyatri poliklinik": "Birinci Kat - Ana giristen girdikten sonra sola donun. On merdivenleri cikinca sola donun. Sol tarafinizdaki kucuk koridorun sonuna dogru ilerleyin veya arka merdivenlerden cikinca sola donun sag tarafinizda yer alir.",
            "cocuk evde saglik birimi": "Birinci Kat - Ana giristen girdikten sonra sola donun. On merdivenleri cikinca sola donun. Sol tarafinizdaki kucuk koridorun sonunda sag tarafta veya arka merdivenlerden cikinca sola donun koridorun sonunda sag tarafinizda yer alir.",
            "konusma terapisti": "Birinci Kat - Ana giristen girdikten sonra sola donun. Merdivenleri cikinca sola donun. Sol tarafinizdaki kucuk koridorun sonuna dogru ilerleyin veya arka merdivenlerden cikinca sola donun. Ileride Sol tarafinizda Sabim Cimer odasini gecince yer alir.",
            "sabim cimer birimi": "Birinci Kat - Ana giristen girdikten sonra sola donun. On merdivenleri cikinca sola donun. Sol tarafinizdaki kucuk koridorun sonuna dogru ilerleyin veya arka merdivenlerden cikinca sola donun. Sol tarafinizda Heyet Psikolog odasini gecince yer alir.",
            "heyet psikolog": "Birinci Kat - Ana giristen girdikten sonra sola donun. On merdivenleri cikinca sola donun. Sol tarafinizdaki kucuk koridorun ilerisinde sol tarafta veya arka merdivenlerden cikinca sola donun koridorun solunda yer alir.",
            "heyet fizik tedavi poliklinik": "Zemin Kat - Ana giristen girdikten sonra sola donun. Koridorun sol tarafinda yer alir.",
            "heyet kbb poliklinik": "Zemin Kat - Ana giristen girdikten sonra sola donun. Koridorun sag tarafinda Heyet Ortopedi Poliklinigin yaninda yer alir.",
            "heyet ortopedi poliklinik": "Zemin Kat - Ana giristen girdikten sonra sola donun. Koridorun sag tarafinda kulak burun bogaz polikliniginin yaninda yer alir.",
            "kan alma birimi": "Zemin Kat - Ana giristen girdikten sonra saga donun. Saginizdaki ilk odadir.",
            "saglik kurulu": "Zemin Kat - Ana giristen girdikten sonra saga donun. Koridorun sonundaki genis alanda yer almaktadir.",
            "saglik kurulu kayit birimi": "Zemin Kat - Girişten hemen sonra sola donun. Sol taraftaki etrafi kapali yerdir.",
            "on merdivenler": "Zemin Kat - Girişten girdikten sonra sola donun, koridorun sonuna dogru sol tarafta yer alir.",
            "arka cikis": "Zemin Kat - Koridordan sola donun. On merdivenleri gecip sola donerek arka cikis kapisina ulasabilirsiniz.",
            "evrak kayit vezne": "Zemin Kat - Ana giristen girince tam karsinizda yer alir.",
            "hasta kayit": "Zemin Kat - Ana giriste sol tarafta yer alir.",
            "evde saglik hizmetleri birimi": "Zemin Katta olup girisi binanin kuzey yonundedir.",
            "rontgen goruntuleme diger bina": "Rontgen birimi bu binada degildir. Arka kapidan cikinca sola donun, 30 metre sonra saga donun, ileride sag tarafta yer alir.",
            "asansor": "Zemin katta Hasta Kayit bankosunu gecince sol tarafta, 1. katta binanin tam orta kesiminde yer alir.",
            "tuvaletler lavabolar": "Zemin Katta - Ana giristen sonra sola donun. Koridorun sonunda yer alir."
        };

        const esAnlamlilar = {
            "kan": "kan alma birimi", "tahlil": "kan alma birimi", "laboratuvar": "kan alma birimi",
            "wc": "tuvaletler lavabolar", "lavabo": "tuvaletler lavabolar", "tuvalet": "tuvaletler lavabolar",
            "heyet": "saglik kurulu", "rapor": "saglik kurulu",
            "kulak": "heyet kbb poliklinik", "kbb": "heyet kbb poliklinik",
            "goz": "heyet goz poliklinik", "kalp": "heyet kardiyoloji poliklinik", "kardiyoloji": "heyet kardiyoloji poliklinik",
            "cocuk": "heyet cocuk cozger poliklinik", "fizik": "heyet fizik tedavi poliklinik",
            "gogus": "heyet gogus hastaliklari poliklinik", "uroloji": "heyet uroloji poliklinik",
            "cerrahi": "heyet genel cerrahi poliklinik", "rontgen": "rontgen goruntuleme diger bina",
            "film": "rontgen goruntuleme diger bina", "isitme": "isitme testi odio",
            "odio": "isitme testi odio", "dahiliye": "heyet dahiliye poliklinik",
            "noroloji": "heyet noroloji poliklinik", "nöroloji": "heyet noroloji poliklinik",
            "ortopedi": "heyet ortopedi poliklinik",
            "psikiyatri": "heyet psikiyatri poliklinikleri", "cimer": "sabim cimer birimi", "sft": "solunum fonksiyon sft birimi",
            "ekg": "ekg birimi"
        };

        function sesliOkuyucu(metin) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance(metin);
                msg.lang = 'tr-TR';
                msg.rate = 0.95;
                window.speechSynthesis.speak(msg);
            }
        }

        function sesliAramaBaslat() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const statusEl = document.getElementById('mic-status');
            const btnEl = document.getElementById('mic-btn');

            if (!SpeechRecognition) {
                alert("Tarayiciniz sesli aramayi desteklemiyor.");
                return;
            }

            const recognition = new SpeechRecognition();
            recognition.lang = 'tr-TR';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.onstart = function() {
                btnEl.style.backgroundColor = '#28a745';
                btnEl.innerText = " Dinliyor...";
                statusEl.innerText = "Konusun...";
            };

            recognition.onresult = function(event) {
                const speechResult = event.results[0][0].transcript.toLowerCase()
                    .replace(/[.,\\/#!$%\\^&\\*;:{}=\\-_`~()]/g,"").trim();
                statusEl.innerText = "Bulundu: " + speechResult;
                btnEl.style.backgroundColor = '#ff4b4b';
                btnEl.innerText = "🎙️ Konus";
                
                let bulunanBirim = "";
                let tarif = "";

                if (esAnlamlilar[speechResult]) {
                    bulunanBirim = esAnlamlilar[speechResult];
                } else if (tarifVeritabani[speechResult]) {
                    bulunanBirim = speechResult;
                } else {
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
                    tarif = bulunanBirim + " icin yol tarifi. " + tarifVeritabani[bulunanBirim];
                    sesliOkuyucu(tarif);
                } else {
                    sesliOkuyucu("Aradiginiz birim sistemde bulunamadi. Lutfen tekrar deneyin.");
                }

                // Streamlit'e parametre gonder - window.location kullan (iframe icin daha guvenli)
                const url = new URL(window.location.href);
                url.searchParams.set('ses_arama', speechResult);
                window.location.href = url.toString();
            };

            recognition.onerror = function(event) {
                btnEl.style.backgroundColor = '#ff4b4b';
                btnEl.innerText = "🎙️ Konus";
                statusEl.innerText = "Hata: " + event.error;
            };

            recognition.onend = function() {
                btnEl.style.backgroundColor = '#ff4b4b';
                btnEl.innerText = "🎙️ Konus";
            };

            try {
                recognition.start();
            } catch(e) {
                statusEl.innerText = "İzin hatasi.";
            }
        }
    </script>
    """, height=70)

# Sesli arama URL parametresini isle
ses_arama_param = st.query_params.get("ses_arama", "")
if ses_arama_param:
    # Parametreyi temizle
    yeni_params = dict(st.query_params)
    yeni_params.pop("ses_arama", None)
    st.query_params.clear()
    for k, v in yeni_params.items():
        st.query_params[k] = v
    akilli_arama_isle(ses_arama_param)
    st.rerun()

with col_input:
    metin_input = st.text_input(
        "Birim arayın:", 
        placeholder="Örn: Dahiliye, Kan, Röntgen...", 
        key="arama_input", 
        label_visibility="collapsed"
    )

# Text input isleme - callback mantigi ile
if metin_input and metin_input != st.session_state.get("son_metin", ""):
    st.session_state["son_metin"] = metin_input
    akilli_arama_isle(metin_input)
    st.rerun()

# ==============================================================================
# 🗂️ KATEGORİ VE LİSTELEME
# ==============================================================================
st.write("---")

# Radio buton icin index hesaplama
kategori_secenekleri = ["🏥 Resmi Poliklinikler / Odalar", "⚙️ Genel ve İdari Birimler"]
mevcut_kategori = st.session_state.get("kategori_secimi", kategori_secenekleri[0])
try:
    default_index = kategori_secenekleri.index(mevcut_kategori)
except ValueError:
    default_index = 0

kategori = st.radio(
    "Kategori", 
    kategori_secenekleri, 
    index=default_index,
    horizontal=True, 
    label_visibility="collapsed",
    key="kategori_radio"
)

# Kategori degistiyse secimi sifirla
if kategori != st.session_state.get("kategori_secimi"):
    st.session_state["kategori_secimi"] = kategori
    st.session_state["secilen_birim"] = "Seçim Yapınız..."
    st.rerun()

if kategori == "🏥 Resmi Poliklinikler / Odalar":
    liste = ["Seçim Yapınız..."] + list(POLIKLINIKLER.keys())
else:
    liste = ["Seçim Yapınız..."] + list(DIGER_ALANLAR.keys())

secili_val = st.session_state.get("secilen_birim", "Seçim Yapınız...")
try:
    idx = liste.index(secili_val)
except ValueError:
    idx = 0

secim = st.selectbox(
    "BİRİM SEÇİNİZ:", 
    liste, 
    index=idx, 
    key="sb_birim"
)

if secim != st.session_state.get("secilen_birim"):
    st.session_state["secilen_birim"] = secim
    st.rerun()

# ==============================================================================
# 🎯 SONUÇ GÖSTERİMİ & SESLENDİRME
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

st.caption("🤖 Barajyolu Ek Hizmet Binası Mobil Dijital Yönlendirme (Engin PEKDEMİR)")
