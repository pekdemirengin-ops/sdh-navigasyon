import streamlit as st
import os
from PIL import Image

# ==============================================================================
# ⚙️ SAYFA AYARLARI
# ==============================================================================
st.set_page_config(page_title="SDH Navigasyon", page_icon="🏥", layout="centered")

# ==============================================================================
# 🗄️ VERİ TABANI
# ==============================================================================
POLIKLINIKLER = {
    "Seçim Yapınız...": {"fancy": False, "tarif": "", "kat": ""},
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
    "Nöroloji Polikliniği / Heyet Nöroloji": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkıp sağ koridora yönelin. Sol sırada, Göğüs Hastalıkları ile Genel Cerrahi odalarının arasındadır.", "kat": "1kat"},
    "Heyet Ortopedi Polikliniği": {"fancy": False, "tarif": "Zemin Kat - Ana girişten girdikten sonra tam sola doğru karşınızda yer alır. ", "kat": "zemin"},
    "Heyet Psikiyatri Polikliniği": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkınca sağ dönün. koridorun ortasında, Heyet Genel Cerrahi Polikliniği yanında yer alır. .", "kat": "1kat"},
    "Heyet Üroloji Polikliniği": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkınca sola dönün, sol sıradaki ilk odadır. (Göz Heyet Polikliniğinin karşısı).", "kat": "1kat"},
    "Diyetisyen (Heyet Diyet)": {"fancy": False, "tarif": "Zemin Kat - Ana girişten girdikten sonra tam karşınızda. Ortopedi Heyet odasının yanında yer alır.", "kat": "zemin"},
    "Heyet Psikolog": {"fancy": False, "tarif": "1. Kat - Arka merdivenlerden çıkınca sola dönün. Sol tarafta yer alır.", "kat": "1kat"},
    "Konuşma Terapisi Birimi": {"fancy": False, "tarif": "1. Kat - Arka merdivenlerden çıkınca sol koridorun en sonundaki odadır (Sabim Cimer odasının yanı).", "kat": "1kat"}
    }

DIGER_ALANLAR = {
    "Seçim Yapınız...": {"fancy": False, "tarif": "", "kat": ""},
    "Tuvaletler / Lavabolar (WC)": {"fancy": False, "tarif": "Zemin Katta: Giriş kapısından sola dönüp ilerleyin koridorun sonunda yer alır.", "kat": "zemin"},
    "Sağlık Kurulu / Heyet Odası": {"fancy": False, "tarif": "Zemin Kat - Giriş kapısından girdiğinizde sağ tarafınızda yer almaktadır.", "kat": "zemin"},
    "Kan Alma": {"fancy": False, "tarif": "Zemin Kat - Giriş kapısından içeri girdiğinizde hemen sağ köşededir.", "kat": "zemin"},
    "Evrak Kayıt / Vezne": {"fancy": False, "tarif": "Zemin Kat - Giriş kapısından içeri girdiğinizde tam karşınızda.", "kat": "zemin"},
    "Evde Sağlık Hizmetleri Birimi": {"fancy": False, "tarif": "Zemin Katta olup girişi binanın kuzey yönündedir.", "kat": "zemin"},
    "Röntgen / Görüntüleme (DİĞER BİNA)": {"fancy": True, "tarif": "🚨 DİĞER BİNADADIR! Röntgen birimi bu binada değildir. Lütfen ana binadan çıkıp diğer binaya geçiş yapınız.", "kat": ""},
    "Asansör": {"fancy": False, "tarif": "Zemin ve 1. Kat - Binanın tam orta kesiminde, bankonun hemen yanında yer alır.", "kat": "zemin"}
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

# ==============================================================================
# 📱 BAŞLIK & KARŞILAMA
# ==============================================================================
st.title("🏥 SDH BARAJ YOLU EK HİZMET BİNASI")
st.subheader("SDH SESLİ DİJİTAL YÖNLENDİRME")
st.info("📍 Başlangıç Noktası: Poliklinik Binası Ana Girişi (Zemin Kat)")

if "karsilandi" not in st.session_state:
    st.session_state["karsilandi"] = True
    otomatik_sesli_oku("Seyhan Devlet Hastanesi Baraj Yolu Ek Hizmet Binası sesli dijital yönlendirme sistemine hoş geldiniz. Lütfen gitmek istediğiniz birimi seçiniz.")

# ==============================================================================
# 🚀 HIZLI ERİŞİM BUTONLARI
# ==============================================================================
st.write("### 🚀 Sık Kullanılan Birimler")
col1, col2, col3, col4, col5, = st.columns(5)

def birim_sec(birim_adi):
    st.session_state["secilen_birim"] = birim_adi
    if birim_adi in DIGER_ALANLAR:
        st.session_state["kategori"] = "⚙️ Genel ve İdari Birimler"
    else:
        st.session_state["kategori"] = "🏥 Resmi Poliklinikler / Odalar"

with col1:
    if st.button("🩸 KAN ALMA", use_container_width=True):
        birim_sec("Kan Alma")
with col2:
    if st.button("🏥 SAĞLIK KURULU", use_container_width=True):
        birim_sec("Sağlık Kurulu / Heyet Odası")
with col3:
    if st.button("📋 EVRAK KAYIT/VEZNE", use_container_width=True):
        birim_sec("Evrak Kayıt / Vezne")
with col4:
    if st.button("🛗 ASANSÖR", use_container_width=True):
        birim_sec("Asansör")
with col5:
    if st.button("🚻 WC", use_container_width=True):
        birim_sec("Tuvaletler / Lavabolar (WC)")

# ==============================================================================
# 🖥️ ARAYÜZ KATMANI (KATEGORİ VEYA LİSTE SEÇİMİ)
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
    liste = list(POLIKLINIKLER.keys())
    
    # Seçilen birim geçerli listede yoksa sıfırla
    if st.session_state["secilen_birim"] not in liste:
        st.session_state["secilen_birim"] = "Seçim Yapınız..."
        
    secim = st.selectbox(
        "GİTMEK İSTEDİĞİNİZ POLİKLİNİĞİ SEÇİNİZ:", 
        liste, 
        key="secilen_birim"
    )

else:
    liste_alan = list(DIGER_ALANLAR.keys())
    
    # Seçilen birim geçerli listede yoksa sıfırla
    if st.session_state["secilen_birim"] not in liste_alan:
        st.session_state["secilen_birim"] = "Seçim Yapınız..."
        
    secim = st.selectbox(
        "Aradığınız Genel veya İdari Birimi seçiniz:", 
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

st.caption("🤖 Barajyolu Ek Hizmet Binası Sesli Dijital Yönlendirme Sistemi (Engin PEKDEMİR)")
