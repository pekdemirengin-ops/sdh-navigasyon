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
    .ses-uyari {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 8px;
        font-size: 13px;
        text-align: center;
        margin-bottom: 10px;
        border: 1px solid #ffeeba;
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
        "kroki": "saglik_kurulu_yol_tarifi.png"
    },
    "Sağlık Kurulu Kayıt Birimi": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Girişten hemen sonra düz devam edin, sol taraftaki bankoda yer almaktadır.",
        "kroki": "saglik_kurulu_kayit_yol_tarifi.png"
    },
    "Ön Merdivenler": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Girişten girdikten sonra sola yönelin, koridor boyunca düz ilerleyerek ön merdivenlere ulaşabilirsiniz.",
        "kroki": "on_merdivenler_yol_tarifi.png"
    },
    "Arka Çıkış": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Koridordan sola ilerleyin, ön merdivenleri geçip sola dönerek arka çıkış kapısına ulaşabilirsiniz.",
        "kroki": "arka_cikis_yol_tarifi.png"
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
        "kroki": "gorme_alani_yol_tarifi.png"
    },
    "Heyet Dahiliye Poliklinik": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Koridor boyunca sağa doğru ilerleyin. Sağ taraftaki odalardan biridir.",
        "kroki": "heyet_dahiliye_polk_yol_tarifi.png"
    },
    "Heyet Göğüs Hastalıkları Poliklinik": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıktıktan hemen sonra sol çaprazda yer almaktadır.",
        "kroki": "heyet_gogus_hastaliklari_polk_yol_tarifi.png"
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
        "kroki": "evrak_kayit_vezne_yol_tarifi.png"
    },
    "Hasta Kayıt": {
        "fancy": False, "kat": "zemin", 
        "tarif": "Ana girişte sol tarafta yer alır.", 
        "kroki": "hasta_kayit_yol_tarifi.png"
    },
    "Evde Sağlık Hizmetleri Birimi": {
        "fancy": False, "kat": "zemin", 
        "tarif": "Zemin Katta olup girişi binanın kuzey yönündedir.", 
        "kroki": "evde_saglik_hizmetleri_yol_tarifi.png"
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
        "kroki": "emzirme odasi_yol_tarifi.png"
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
    "kulak": "Heyet KBB Poliklinik", "kbb": "Heyet KBB Poliklinik",
    "göz": "Heyet Göz Poliklinik", "kalp": "Heyet Kardiyoloji Poliklinik", "kardiyoloji": "Heyet Kardiyoloji Poliklinik",
    "çocuk": "Heyet Çocuk (Çözger) Poliklinik", "fizik": "Heyet Fizik Tedavi Poliklinik",
    "göğüs": "Heyet Göğüs Hastalıkları Poliklinik", "üroloji": "Heyet Üroloji Poliklinik",
    "cerrahi": "Heyet Genel Cerrahi Poliklinik", "röntgen": "Röntgen / Görüntüleme (DİĞER BİNA)",
    "film": "Röntgen / Görüntüleme (DİĞER BİNA)", "işitme": "İşitme Testi (Odio)",
    "odio": "İşitme Testi (Odio)", "dahiliye": "Heyet Dahiliye Poliklinik",
    "nöroloji": "Heyet Nöroloji Poliklinik", "ortopedi": "Heyet Ortopedi Poliklinik",
    "psikiyatri": "Heyet Psikiyatri Poliklinik", "cimer": "Sabim Cimer Birimi", "sft": "Solunum Fonksiyon (SFT) Birimi"
}

# ==============================================================================
# 🧩 OTURUM DURUMU (SESSION STATE) BAŞLATMA
# ==============================================================================
if "secilen_birim" not in st.session_state:
    st.session_state["secilen_birim"] = "Seçim Yapınız..."
if "kategori" not in st.session_state:
    st.session_state["kategori"] = "🏥 Resmi Poliklinikler / Odalar"
if "ses_izni" not in st.session_state:
    st.session_state["ses_izni"] = False

# ==============================================================================
# 🛠️ YARDIMCI FONKSİYONLAR
# ==============================================================================
def otomatik_sesli_oku(metin):
    if metin and metin.strip():
        temiz_metin = metin.replace("1. Kat", "Birinci Kat").replace("'", "\\'").replace('"', '\\"')
        js_kodu = f"""
        <script>
            try {{
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    var msg = new SpeechSynthesisUtterance('{temiz_metin}');
                    msg.lang = 'tr-TR';
                    msg.rate = 1.0;
                    window.speechSynthesis.speak(msg);
                }}
            }} catch(e) {{}}
        </script>
        """
        st.components.v1.html(js_kodu, height=0)

def kroki_goster(kroki_dosya_adi):
    if not kroki_dosya_adi:
        return

    aranan_tam = kroki_dosya_adi.strip().lower()
    aranan_govde = Path(aranan_tam).stem.lower()
    
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
                        d_ad = dosya.name.lower()
                        d_govde = dosya.stem.lower()
                        
                        if d_ad == aranan_tam or d_govde == aranan_govde:
                            bulunan_dosya = dosya
                            break
                        
                        clean_aranan = aranan_govde.replace('ç','c').replace('ğ','g').replace('ı','i').replace('ö','o').replace('ş','s').replace('ü','u').replace('_','')
                        clean_dosya = d_govde.replace('ç','c').replace('ğ','g').replace('ı','i').replace('ö','o').replace('ş','s').replace('ü','u').replace('_','')
                        
                        if clean_aranan in clean_dosya or clean_dosya in clean_aranan:
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
        st.warning(f"⚠️ Kroki Bulunamadı: `{kroki_dosya_adi}` dosyası sistemde bulunamadı.")

def birim_sec(birim_adi):
    st.session_state["secilen_birim"] = birim_adi
    if birim_adi in DIGER_ALANLAR:
        st.session_state["kategori"] = "⚙️ Genel dan İdari Birimler"
    elif birim_adi in POLIKLINIKLER:
        st.session_state["kategori"] = "🏥 Resmi Poliklinikler / Odalar"

def akilli_arama_isle(gelen_metin):
    if not gelen_metin:
        return
    temiz = re.sub(r'[^\w\s]', '', gelen_metin.lower())
    kelimeler = temiz.split()
    tum_birimler = {**POLIKLINIKLER, **DIGER_ALANLAR}

    for k in kelimeler:
        if k in ES_ANLAMLILAR:
            birim_sec(ES_ANLAMLILAR[k])
            return

    for birim in tum_birimler:
        if temiz in birim.lower() or birim.lower() in temiz:
            birim_sec(birim)
            return

    for k in kelimeler:
        if len(k) >= 3:
            for birim in tum_birimler:
                if k in birim.lower():
                    birim_sec(birim)
                    return

# ==============================================================================
# 🖥️ ARAYÜZ BAŞLIK VE KARŞILAMA
# ==============================================================================
st.title("🏥 SDH BARAJ YOLU EK BİNASI")
st.caption("📱 Mobil Sesli Dijital Yönlendirme Sistemi")
st.info(f"📍 **Bulunduğunuz Konum:** {baslangic_noktasi}")

if not st.session_state["ses_izni"]:
    st.markdown("""
        <div class="ses-uyari">
            ⚠️ <b>Sesli anlatımı aktifleştirmek için:</b> Lütfen aşağıdaki butona dokunarak ses motorunu başlatın.
        </div>
    """, unsafe_allow_html=True)
    if st.button("🔊 Sesli Yönlendirmeyi Başlat", use_container_width=True):
        st.session_state["ses_izni"] = True
        otomatik_sesli_oku("Seyhan Devlet Hastanesi Baraj Yolu Ek Hizmet Binası navigasyon sistemine hoş geldiniz.")
        st.rerun()

# ==============================================================================
# 🚀 HIZLI ERİŞİM BUTONLARI
# ==============================================================================
st.write("### 🚀 Sık Kullanılan Birimler")
col1, col2 = st.columns(2)

with col1:
    if st.button("🩸 KAN ALMA", use_container_width=True):
        birim_sec("Kan Alma Birimi")
    if st.button("📋 EVRAK KAYIT", use_container_width=True):
        birim_sec("Evrak Kayıt / Vezne")
    if st.button("🚻 WC / LAVABO", use_container_width=True):
        birim_sec("Tuvaletler / Lavabolar")
    if st.button("🗂️ HASTA KAYIT", use_container_width=True):
        birim_sec("Hasta Kayıt")

with col2:
    if st.button("🏥 SAĞLIK KURULU", use_container_width=True):
        birim_sec("Sağlık Kurulu")
    if st.button("🛗 ASANSÖR", use_container_width=True):
        birim_sec("Asansör")
    if st.button("📝 S.K. KAYIT", use_container_width=True):
        birim_sec("Sağlık Kurulu Kayıt Birimi")

# ==============================================================================
# 🎙️ YEREL SESLİ ARAMA (STREAMLIT YENİ NESİL MİKROFON GİRİŞİ)
# ==============================================================================
st.write("---")
st.write("### 🎙️ Sesle Arama Yapın")
st.caption("Mikrofon simgesine basıp gitmek istediğiniz yeri söyleyebilirsiniz (Örn: Dahiliye, Röntgen, Kan Alma...)")

# Streamlit'in yerleşik ve mobilde en kararlı çalışan ses kaydı bileşeni
ses_dosyasi = st.audio_input("Gitmek istediğiniz yeri sesli söyleyin")

if ses_dosyasi is not None:
    # Not: Gerçek ses çözümleme için OpenAI Whisper veya benzeri bir API entegre edilebilir. 
    # Alternatif olarak pratik bir sesli arama alternatifi için akıllı arama çubuğunu da kullanabilirsiniz.
    st.success("Ses kaydı alındı! (Sesinizi metne dönüştürmek için projenize OpenAI Whisper API ekleyebilir veya aşağıdaki arama çubuğunu kullanabilirsiniz.)")

# ==============================================================================
# 🔍 AKILLI METİN ARAMA ÇUBUĞU
# ==============================================================================
metin_input = st.text_input("Veya birim yazarak arayın:", placeholder="Örn: Dahiliye, Kan, Röntgen, Ortopedi...", key="arama_input")

if metin_input and metin_input != st.session_state.get("son_metin", ""):
    st.session_state["son_metin"] = metin_input
    akilli_arama_isle(metin_input)

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
    st.session_state["secilen_birim"] = secim
else:
    liste = ["Seçim Yapınız..."] + list(DIGER_ALANLAR.keys())
    secili_val = st.session_state.get("secilen_birim", "Seçim Yapınız...")
    idx = liste.index(secili_val) if secili_val in liste else 0
    
    secim = st.selectbox("DİĞER BİRİMLERİ SEÇİNİZ:", liste, index=idx, key="sb_diger")
    st.session_state["secilen_birim"] = secim

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
                
        st.write("---")
        if st.button("🔄 Yeni Arama / Seçimi Sıfırla", use_container_width=True):
            st.session_state["secilen_birim"] = "Seçim Yapınız..."
            st.rerun()

st.caption("🤖 Barajyolu Ek Hizmet Binası Mobil Dijital Yönlendirme (Engin PEKDEMİR)")
