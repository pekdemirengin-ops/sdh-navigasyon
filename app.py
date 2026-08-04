import streamlit as st
import os
import re
from PIL import Image
from streamlit_mic_recorder import speech_to_text

# ==============================================================================
# ⚙️ SAYFA & MOBİL VIEWPORT AYARLARI
# ==============================================================================
st.set_page_config(
    page_title="SDH Mobil Navigasyon", 
    page_icon="🏥", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 📱 MOBİL ÖZEL CSS İYİLEŞTİRMELERİ
# ==============================================================================
st.markdown("""
    <style>
    .block-container {
        padding-top: 1.5rem !important;
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
    input, select, textarea {
        font-size: 16px !important;
    }
    div[role="radiogroup"] {
        gap: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 📌 DİNAMİK QR KOD KONUM ALGILAMA
# ==============================================================================
query_params = st.query_params
baslangic_noktasi = query_params.get("konum", "Poliklinik Binası Ana Girişi (Zemin Kat)")

# ==============================================================================
# 🗄️ VERİ TABANI
# ==============================================================================
POLIKLINIKLER = {
    "Görme Alanı Ölçüm Odası": {"fancy": False, "tarif": "1. Kat - Merdivenlerden veya asansörden çıkınca sağa dönün. Koridorun ilerisinde, sol tarafta yer alır. (Heyet Çocuk - ÇÖZGER polikliniğinin hemen yanındadır).", "kat": "1kat"},
    "Çocuk Gelişimi Birimi": {"fancy": False, "tarif": "1. Kat - Arka merdivenlerden çıkınca tam karşınızdadır.", "kat": "1kat"},
    "Göz-OCT / Göz Ölçüm Odası": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkınca sağa dönün. Koridorun ilerisinde, sol tarafta yer alır. (Fizik Tedavi 2 polikliniğinin hemen yanında).", "kat": "1kat"},
    "Solunum Fonksiyon Testi Odası": {"fancy": False, "tarif": "1. Kat - Arka merdivenlerden çıkınca tam sola dönün, hemen sağ tarafta yer alır.", "kat": "1kat"},
    "ODİO-İşitme Testi Odası": {"fancy": False, "tarif": "1. Kat - Merdivenlerden veya asansörden çıkınca sağa dönün. Koridorun ilerisinde, sağ tarafta yer alır. (Emzirme Odası yanı).", "kat": "1kat"},
    "Emzirme Odası": {"fancy": False, "tarif": "1. Kat - Merdivenlerden veya asansörden çıkınca sağa dönün. Koridorun ilerisinde, sağ tarafta yer alır. (İşitme Testi yanı).", "kat": "1kat"},
    "Heyet Cildiye Polikliniği (Oda 1 ve 2)": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkınca sağa dönün, sağ tarafta yer alır veya asansörden çıkınca sola dönün, sol tarafta yer alır..", "kat": "1kat"},
    "Çocuk Hastalıkları Polikliniği (DİĞER BİNA GİRİŞİ)": {"fancy": True, "tarif": "🚨 DİĞER BİNA GİRİŞİNDEDİR! Çocuk hastalıkları poliklinik muayeneleri için lütfen diğer bina girişini kullanınız.", "kat": ""},
    "Heyet Çocuk Polk. (Çözger)": {"fancy": False, "tarif": "1. Kat - Merdivenlerden veya asansörden çıkınca sağa dönün. Koridorun ilerisinde sol tarafta yer alır. (Görme Alanı odasının hemen yanındadır).", "kat": "1kat"},
    "Heyet Çocuk Psikiyatri Polk.": {"fancy": False, "tarif": "1. Kat - Arka merdivenlerden çıkınca sola dönün. Koridorun ilerisinde, sol tarafta yer alır. (Çocuk Evde Sağlık odasının yanı).", "kat": "1kat"},
    "Dahiliye Polikliniği": {"fancy": False, "tarif": "1. Kat - Merdivenlerden ve asansörden çıkınca sağa dönün. Koridorun sonundaki sağ tarafta yer alır. (Fizik Tedavi 2 polikliniğinin yanı).", "kat": "1kat"},
    "Fizik Tedavi Polikliniği 1": {"fancy": False, "tarif": "Zemin Kat - Ana girişten girdikten sonra sola dönün. Koridorda sol tarafta yer alır.", "kat": "zemin"},
    "Fizik Tedavi Polikliniği 2": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkınca sağa dönün. Koridorun sonuna doğru sağ tarafta yer alır. (Dahiliye yanındadır).", "kat": "1kat"},
    "Fizik Tedavi Polikliniği 3": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkınca sağa dönün. Koridorun ilerisinde sol tarafta yer alır.", "kat": "1kat"},
    "Heyet Genel Cerrahi Polikliniği": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkınca sağa dönün. Koridorun solunda yer alır. Genel Cerrahi Pansuman odasının yanındadır.", "kat": "1kat"},
    "Heyet Göğüs Hastalıkları Polikliniği": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkınca tam karşınızda yer almaktadır.", "kat": "1kat"},
    "Heyet Göz Polikliniği": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkınca sola dönün. Sağ taraftanızda yer alır. (Göz Ölçüm odasının yanı).", "kat": "1kat"},
    "Heyet Kardiyoloji Polikliniği": {"fancy": False, "tarif": "1. Kat - Merdivenlerden veya asansörden çıkınca sağa dönün. Koridorun sonunda sol tarafta yer alır.", "kat": "1kat"},
    "Heyet K.B.B. Polikliniği (Oda 1 ve 2)": {"fancy": False, "tarif": "Zemin Kat - Ana girişten girdikten sonra sola dönün. Sağ tarafta yer alır.", "kat": "zemin"},
    "Nöroloji Polikliniği / Heyet Nöroloji": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkıp sağ koridora yönelin. Sol sırada, Heyet Göğüs Hastalıkları ile Genel Cerrahi odalarının arasındadır.", "kat": "1kat"},
    "Heyet Ortopedi Polikliniği": {"fancy": False, "tarif": "Zemin Kat - Ana girişten girdikten sonra tam sola doğru karşınızda yer alır. ", "kat": "zemin"},
    "Heyet Psikiyatri Polikliniği": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkınca sağ dönün. koridorun ortasında, Heyet Genel Cerrahi Polikliniği yanında yer alır. .", "kat": "1kat"},
    "Heyet Üroloji Polikliniği": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkınca sola dönün, sol sıradaki ilk odadır. (Göz Heyet Polikliniğinin karşısı).", "kat": "1kat"},
    "Diyetisyen (Heyet Diyet)": {"fancy": False, "tarif": "Zemin Kat - Ana girişten girdikten sonra tam karşınızda. Ortopedi Heyet odasının yanında yer alır.", "kat": "zemin"},
    "Heyet Psikolog": {"fancy": False, "tarif": "1. Kat - Arka merdivenlerden çıkınca sola dönün. Sol tarafta yer alır.", "kat": "1kat"},
    "Konuşma Terapisi Birimi": {"fancy": False, "tarif": "1. Kat - Arka merdivenlerden çıkınca sol koridorun en sonundaki odadır (Sabim Cimer odasının yanı).", "kat": "1kat"}
}

DIGER_ALANLAR = {
    "Sağlık Kurulu / Heyet Odası": {"fancy": False, "tarif": "Zemin Kat - Ana girişten sonra sağa dönün. Koridorun sonunda yer almaktadır.", "kat": "zemin"},
    "Sağlık Kurulu Kayıt": {"fancy": False, "tarif": "Ana girişte sola dönün. Sol taraftaki ilk odadır.", "kat": "zemin"},
    "Evrak Kayıt / Vezne": {"fancy": False, "tarif": "Zemin Kat - Ana girişten tam karşınızda.", "kat": "zemin"},
    "Hasta Kayıt": {"fancy": False, "tarif": "Ana girişte sol tarafta yer alır. .", "kat": "zemin"},
    "Kan Alma": {"fancy": False, "tarif": "Zemin Kat - Ana girişten sonra sağa dönün. Sağ tarafta ilk odadır.", "kat": "zemin"},
    "Evde Sağlık Hizmetleri Birimi": {"fancy": False, "tarif": "Zemin Katta olup girişi binanın kuzey yönündedir.", "kat": "zemin"},
    "Röntgen / Görüntüleme (DİĞER BİNA)": {"fancy": True, "tarif": "🚨 DİĞER BİNADADIR! Röntgen birimi bu binada değildir. Arka kapıdan çıkınca sola dönün, ardından sağa, ileride sağ tarafta yer alır. ", "kat": ""},
    "Asansör": {"fancy": False, "tarif": " 1. katta binanın tam orta kesiminde, zemin katta Hasta Kayıt bankosunun geçince sol tarafta yer alır.", "kat": "zemin"},
    "Tuvaletler / Lavabolar (WC)": {"fancy": False, "tarif": "Zemin Katta: Ana girişten sonra sola dönün. Koridorun sonunda yer alır.", "kat": "zemin"},
}

# 🔤 EŞ ANLAMLI VE ARAMA KOLAYLAŞTIRICI SÖZLÜK
ES_ANLAMLILAR = {
    "kan": "Kan Alma",
    "tahlil": "Kan Alma",
    "laboratuvar": "Kan Alma",
    "tahlili": "Kan Alma",
    "wc": "Tuvaletler / Lavabolar (WC)",
    "lavabo": "Tuvaletler / Lavabolar (WC)",
    "tuvalet": "Tuvaletler / Lavabolar (WC)",
    "w.c": "Tuvaletler / Lavabolar (WC)",
    "heyet": "Sağlık Kurulu / Heyet Odası",
    "rapor": "Sağlık Kurulu / Heyet Odası",
    "kulak": "Heyet K.B.B. Polikliniği (Oda 1 ve 2)",
    "kbb": "Heyet K.B.B. Polikliniği (Oda 1 ve 2)",
    "göz": "Heyet Göz Polikliniği",
    "kalp": "Heyet Kardiyoloji Polikliniği",
    "kardiyoloji": "Heyet Kardiyoloji Polikliniği",
    "cilt": "Heyet Cildiye Polikliniği (Oda 1 ve 2)",
    "cildiye": "Heyet Cildiye Polikliniği (Oda 1 ve 2)",
    "deri": "Heyet Cildiye Polikliniği (Oda 1 ve 2)",
    "çocuk": "Heyet Çocuk Polk. (Çözger)",
    "fizik": "Fizik Tedavi Polikliniği 1",
    "akciğer": "Heyet Göğüs Hastalıkları Polikliniği",
    "göğüs": "Heyet Göğüs Hastalıkları Polikliniği",
    "beslenme": "Diyetisyen (Heyet Diyet)",
    "diyet": "Diyetisyen (Heyet Diyet)",
    "diyetisyen": "Diyetisyen (Heyet Diyet)",
    "üroloji": "Heyet Üroloji Polikliniği",
    "beze": "Heyet Üroloji Polikliniği",
    "kanser": "Heyet Genel Cerrahi Polikliniği",
    "cerrahi": "Heyet Genel Cerrahi Polikliniği",
    "röntgen": "Röntgen / Görüntüleme (DİĞER BİNA)",
    "filim": "Röntgen / Görüntüleme (DİĞER BİNA)",
    "film": "Röntgen / Görüntüleme (DİĞER BİNA)",
    "işitme": "ODİO-İşitme Testi Odası",
    "udio": "ODİO-İşitme Testi Odası",
    "odio": "ODİO-İşitme Testi Odası"
}

# Session State Başlatma
if "secilen_birim" not in st.session_state:
    st.session_state["secilen_birim"] = "Seçim Yapınız..."
if "kategori" not in st.session_state:
    st.session_state["kategori"] = "🏥 Resmi Poliklinikler / Odalar"

# ==============================================================================
# 🚀 SES BİLEŞENİ & KROKİ
# ==============================================================================
def otomatik_sesli_oku(metin):
    if metin and metin.strip():
        okunacak_metin = metin.replace("1. Kat", "Birinci Kat").replace("1. kat", "Birinci kat")
        temiz_metin = okunacak_metin.replace("'", "\\'").replace('"', '\\"')
        js_kodu = f"""
        <script>
            var msg = new SpeechSynthesisUtterance('{temiz_metin}');
            msg.lang = 'tr-TR';
            msg.rate = 1.0; 
            msg.pitch = 1.0; 
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(msg);
        </script>
        """
        st.components.v1.html(js_kodu, height=0)

def kroki_goster(kat_adi):
    hedef_prefix = "zemin_kat" if kat_adi == "zemin" else "birinci_kat"
    bulunan_dosya = None
    if os.path.exists("."):
        for dosya in os.listdir("."):
            if dosya.lower().startswith(hedef_prefix):
                bulunan_dosya = dosya
                break
    if bulunan_dosya:
        try:
            image = Image.open(bulunan_dosya)
            st.image(image, caption=f"🗺️ Resmi {kat_adi.upper()} Krokisi", use_container_width=True)
        except Exception as e:
            st.error(f"🚨 Görsel açılırken hata oluştu: {e}")
    else:
        st.warning(f"📸 Klasörde [{hedef_prefix}] ile başlayan bir kroki görseli bulunamadı.")

def birim_sec(birim_adi):
    st.session_state["secilen_birim"] = birim_adi
    if birim_adi in DIGER_ALANLAR:
        st.session_state["kategori"] = "⚙️ Genel ve İdari Birimler"
    elif birim_adi in POLIKLINIKLER:
        st.session_state["kategori"] = "🏥 Resmi Poliklinikler / Odalar"

# 🧠 AKILLI SES ALMA VE KELİME YAKALAMA MOTORU
def akilli_arama_isle(gelen_metin):
    if not gelen_metin:
        return
    
    # Metni küçük harfe çevir ve noktalama işaretlerini sil
    temiz_metin = gelen_metin.lower()
    temiz_metin = re.sub(r'[^\w\s]', '', temiz_metin)
    kelimeler = temiz_metin.split()

    tum_birimler = {**POLIKLINIKLER, **DIGER_ALANLAR}

    # 1. Aşama: Eş Anlamlı / Anahtar Kelime Yakalama
    for kelime in kelimeler:
        if kelime in ES_ANLAMLILAR:
            birim_sec(ES_ANLAMLILAR[kelime])
            return

    # 2. Aşama: Cümle İçi Alt Metin Arama
    for birim in tum_birimler:
        birim_kucuk = birim.lower()
        if temiz_metin in birim_kucuk or birim_kucuk in temiz_metin:
            birim_sec(birim)
            return

    # 3. Aşama: Kelime Kelime Arama (En az 3 harfli kelimeler)
    for kelime in kelimeler:
        if len(kelime) >= 3:
            for birim in tum_birimler:
                if kelime in birim.lower():
                    birim_sec(birim)
                    return

    # Bulunamadıysa Anons Et
    otomatik_sesli_oku(f"Üzgünüm, {gelen_metin} anlaşılamadı. Lütfen listeden seçiniz.")

# ==============================================================================
# 📱 BAŞLIK & KARŞILAMA
# ==============================================================================
st.title("🏥 SDH BARAJ YOLU EK BİNASI")
st.caption("📱 Mobil Sesli Dijital Yönlendirme Sistemi")
st.info(f"📍 **Bulunduğunuz Nokta:** {baslangic_noktasi}")

if "karsilandi" not in st.session_state:
    st.session_state["karsilandi"] = True
    otomatik_sesli_oku("Seyhan Devlet Hastanesi Baraj Yolu Ek Hizmet Binası sesli dijital yönlendirme sistemine hoş geldiniz. Lütfen gitmek istediğiniz birimi seçiniz veya mikrofon butonuna basarak konuşunuz.")

# ==============================================================================
# 🚀 MOBİL UYUMLU HIZLI ERİŞİM BUTONLARI
# ==============================================================================
st.write("### 🚀 Sık Kullanılan Birimler")
m_col1, m_col2 = st.columns(2)

with m_col1:
    if st.button("🩸 KAN ALMA", use_container_width=True):
        birim_sec("Kan Alma")
    if st.button("📋 EVRAK KAYIT", use_container_width=True):
        birim_sec("Evrak Kayıt / Vezne")
    if st.button("🚻 WC / LAVABO", use_container_width=True):
        birim_sec("Tuvaletler / Lavabolar (WC)")
    if st.button("🗂️ HASTA KAYIT", use_container_width=True):
        birim_sec("Hasta Kayıt")

with m_col2:
    if st.button("🏥 SAĞLIK KURULU", use_container_width=True):
        birim_sec("Sağlık Kurulu / Heyet Odası")
    if st.button("🛗 ASANSÖR", use_container_width=True):
        birim_sec("Asansör")
    if st.button("📝 S.K. KAYIT", use_container_width=True):
        birim_sec("Sağlık Kurulu Kayıt")

# ==============================================================================
# 🎙️ SESLİ ARAMA VE ARAMA MOTORU
# ==============================================================================
st.write("---")
st.write("### 🔍 Birim Arama / Sesle Ara")

col_input, col_mic = st.columns([2.5, 1.2])

with col_mic:
    st.write("🎙️ **Sesle Ara:**")
    ses_metni = speech_to_text(
        language='tr', 
        start_prompt="🔴 Konuş", 
        stop_prompt="⏹️ Bitti", 
        key='speech_search'
    )

with col_input:
    metin_girisi = st.text_input(
        "Aramak istediğiniz birim:",
        value=ses_metni if ses_metni else "",
        placeholder="Örn: Dahiliye, Kan tahlili...",
        key="arama_input"
    )

# Sesli Komut Geldiğinde Çalıştır
if ses_metni:
    akilli_arama_isle(ses_metni)
elif metin_girisi and metin_girisi != st.session_state.get("son_metin", ""):
    st.session_state["son_metin"] = metin_girisi
    akilli_arama_isle(metin_girisi)

# ==============================================================================
# 🖥️ ARAYÜZ KATMANI (DİNAMİK KATEGORİ VE LİSTE)
# ==============================================================================
st.write("---")

kategori = st.radio(
    "Navigasyon Modu", 
    ["🏥 Resmi Poliklinikler / Odalar", "⚙️ Genel ve İdari Birimler"], 
    key="kategori",
    horizontal=True, 
    label_visibility="collapsed"
)

if "Poliklinikler" in kategori:
    liste = ["Seçim Yapınız..."] + list(POLIKLINIKLER.keys())
    if st.session_state["secilen_birim"] not in liste:
        st.session_state["secilen_birim"] = "Seçim Yapınız..."
        
    secim = st.selectbox(
        "GİTMEK İSTEDİĞİNİZ POLİKLİNİĞİ SEÇİNİZ:", 
        liste, 
        key="secilen_birim"
    )

else:
    liste_alan = ["Seçim Yapınız..."] + list(DIGER_ALANLAR.keys())
    if st.session_state["secilen_birim"] not in liste_alan:
        st.session_state["secilen_birim"] = "Seçim Yapınız..."
        
    secim = st.selectbox(
        "ARADIĞINIZ DİĞER BİRİMLERİ SEÇİNİZ:", 
        liste_alan, 
        key="secilen_birim"
    )

# ==============================================================================
# 📣 YÖNLENDİRME SONUCU VE SESLENDİRME
# ==============================================================================
if secim != "Seçim Yapınız...":
    tum_birimler = {**POLIKLINIKLER, **DIGER_ALANLAR}
    veri = tum_birimler[secim]
    
    if veri['fancy']:
        st.error(f"🎯 **Hedef Birim:** {secim}")
        st.error(f"🚶 **Yönlendirme:** {veri['tarif']}")
        otomatik_sesli_oku(f"Dikkat. {veri['tarif']}")
    else:
        st.success(f"🎯 **Hedef Birim:** {secim}")
        st.warning(f"🚶 **Resmi Plan Yol Tarifi:** {veri['tarif']}")
        otomatik_sesli_oku(f"{secim} için yol tarifi. {veri['tarif']}")
        if veri['kat']:
            kroki_goster(veri['kat'])
            
    # 🔄 MOBİL SIFIRLAMA BUTONU
    st.write("---")
    if st.button("🔄 Yeni Aramaya Geç / Seçimi Sıfırla", use_container_width=True):
        st.session_state["secilen_birim"] = "Seçim Yapınız..."
        st.rerun()

st.caption("🤖 Barajyolu Ek Hizmet Binası Mobil Dijital Yönlendirme (Engin PEKDEMİR)")
