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
    .ses-uyari {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 8px;
        font-size: 13px;
        text-align: center;
        margin-bottom: 10px;
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
    # ==================== ZEMİN KAT BİRİMLERİ ====================
    "Poliklinik Heyet Fizik Tedavi (Zemin)": {
        "fancy": False,
        "kat": "zemin",
        "tarif": "Zemin Kat - Girişten koridora ilerleyip sol tarafa yönelin. Ön merdivenlerin hemen yanında yer alır.",
        "kroki": "krokiler/kroki_heyet_fizik_zemin.png"
    },
    "Poliklinik Heyet KBB": {
        "fancy": False,
        "kat": "zemin",
        "tarif": "Zemin Kat - Ana girişten girdikten sonra sola dönün. Ön merdivenleri geçince sağ taraftadır.",
        "kroki": "krokiler/kroki_heyet_kbb.png"
    },
    "Poliklinik Heyet Ortopedi": {
        "fancy": False,
        "kat": "zemin",
        "tarif": "Zemin Kat - Girişten koridora girip sola ilerleyin. KBB odasının yanındaki odadır.",
        "kroki": "krokiler/kroki_heyet_ortopedi.png"
    },
    "Kan Alma Birimi": {
        "fancy": False,
        "kat": "zemin",
        "tarif": "Zemin Kat - Poliklinik binası girişinden girdikten sonra düz ilerleyip sağ taraftaki Kan Alma odasına geçebilirsiniz.",
        "kroki": "krokiler/kroki_kan_alma.png"
    },
    "Sağlık Kurulu": {
        "fancy": False,
        "kat": "zemin",
        "tarif": "Zemin Kat - Ana girişten girdikten sonra sağa doğru ilerleyin. Koridorun sonundaki geniş alanda yer almaktadır.",
        "kroki": "krokiler/kroki_saglik_kurulu.png"
    },
    "Sağlık Kurulu Kayıt Birimi": {
        "fancy": False,
        "kat": "zemin",
        "tarif": "Zemin Kat - Girişten hemen sonra düz devam edin, sol taraftaki bankoda yer almaktadır.",
        "kroki": "krokiler/kroki_saglik_kurulu_kayit.png"
    },
    "Ön Merdivenler": {
        "fancy": False,
        "kat": "zemin",
        "tarif": "Zemin Kat - Girişten girdikten sonra sola yönelin, koridor boyunca düz ilerleyerek ön merdivenlere ulaşabilirsiniz.",
        "kroki": "krokiler/kroki_on_merdivenler.png"
    },
    "Arka Çıkış": {
        "fancy": False,
        "kat": "zemin",
        "tarif": "Zemin Kat - Koridordan sola ilerleyin, ön merdivenleri geçip sola dönerek arka çıkış kapısına ulaşabilirsiniz.",
        "kroki": "krokiler/kroki_arka_cikis.png"
    },

    # ==================== 1. KAT BİRİMLERİ ====================
    "Poliklinik Heyet Genel Cerrahi": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıktıktan sonra koridordan sağa yönelin. Koridorun solunda yer almaktadır.",
        "kroki": "krokiler/kroki_heyet_genel.png"
    },
    "Poliklinik Heyet Fizik Tedavi (1. Kat)": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Koridorda sağa doğru ilerleyin, koridorun sonuna doğru sol tarafta kalmaktadır.",
        "kroki": "krokiler/kroki_heyet_fizik_1kat.png"
    },
    "Poliklinik Heyet Nöroloji": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Ana koridorda sağa doğru son noktaya kadar ilerleyin, sol taraftaki oda.",
        "kroki": "krokiler/kroki_heyet_noroloji.png"
    },
    "Görme Alanı Ölçüm Odası": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Koridorda düz devam edin, sağa dönmeden önceki sol hizada bulunan Alan Görme odasıdır.",
        "kroki": "krokiler/kroki_alan_gorme.png"
    },
    "Poliklinik Heyet Dahiliye": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Koridor boyunca sağa doğru ilerleyin. Sağ taraftaki odalardan biridir.",
        "kroki": "krokiler/kroki_heyet_dahiliye.png"
    },
    "Olgu Göğüs Hastalıkları": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıktıktan hemen sonra sol çaprazda yer almaktadır.",
        "kroki": "krokiler/kroki_olgu_gogus.png"
    },
    "Poliklinik Heyet Göğüs Hastalıkları": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıkınca hemen sol tarafta yer almaktadır.",
        "kroki": "krokiler/kroki_heyet_gogus.png"
    },
    "Poliklinik Heyet Göz": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıkıp sola dönün, en uçtaki sol odadır.",
        "kroki": "krokiler/kroki_heyet_goz.png"
    },
    "Poliklinik Heyet Çocuk": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıkınca arka merdiven yönüne (sola) dönün, koridorun sonunda sol taraftadır.",
        "kroki": "krokiler/kroki_heyet_cocuk.png"
    },
    "Konuşma Terapisti Birimi": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Arka merdiven koridorunu geçip güney koridoru boyunca düz ilerleyin. Koridorun en sonundaki odadır.",
        "kroki": "krokiler/kroki_konusma_terapisi.png"
    },
    "Poliklinik Heyet Kardiyoloji": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Ana koridorda sağa doğru sonuna kadar ilerleyin. Sağ taraftaki en son odadır.",
        "kroki": "krokiler/kroki_heyet_kardiyoloji.png"
    },
    "Poliklinik Heyet Üroloji": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıkıp sola dönün. Koridorun sonundaki sol oda.",
        "kroki": "krokiler/kroki_heyet_uroloji.png"
    },
    "İşitme Testi (ODİO)": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Sağa doğru ilerleyin, test odası koridorun sağ tarafında kalmaktadır.",
        "kroki": "krokiler/kroki_isitme_testi.png"
    },
    "Göz OCT Odası": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Koridorda sağa doğru ilerleyin, İşitme Testi odasının hemen yanında sağda yer alır.",
        "kroki": "krokiler/goz_oct_yol_tarifi.png"
    },
    "Göz Ölçüm Birimi": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıkıp sola yönelin, ilk sol kapıdan girin.",
        "kroki": "krokiler/goz_olcum_birimi_yol_tarifi.png"
    },
    "Poliklinik Nöroloji": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıktıktan sonra sağa dönün ve koridor boyunca ilerleyin. Sol tarafta kalmaktadır.",
        "kroki": "krokiler/kroki_noroloji.png"
    },
    "Poliklinik Psikiyatri": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıkıp sağ koridora ilerleyin, orta hizada yer alan psikiyatri poliklinikleridir.",
        "kroki": "krokiler/kroki_psikiyatri.png"
    },
    "Sabim Cimer Birimi": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıktıktan sonra arka merdiven yönüne (sola) dönün, koridoru takip edin.",
        "kroki": "krokiler/kroki_cimer.png"
    },
    "Solunum Fonksiyon (SFT) Birimi": {
        "fancy": False,
        "kat": "1kat",
        "tarif": "1. Kat - Arka merdiven koridorunu geçip sola doğru ilerlediğinizde sol tarafta yer alır.",
        "kroki": "krokiler/kroki_sft.png"
    }
}

ES_ANLAMLILAR = {
    "kan": "Kan Alma", "tahlil": "Kan Alma", "laboratuvar": "Kan Alma", "tahlili": "Kan Alma",
    "wc": "Tuvaletler / Lavabolar", "lavabo": "Tuvaletler / Lavabolar", "tuvalet": "Tuvaletler / Lavabolar",
    "heyet": "Sağlık Kurulu / Heyet Odası", "rapor": "Sağlık Kurulu / Heyet Odası",
    "kulak": "Heyet K.B.B. Polikliniği (Oda 1 ve 2)", "kbb": "Heyet K.B.B. Polikliniği (Oda 1 ve 2)",
    "göz": "Heyet Göz Polikliniği", "kalp": "Heyet Kardiyoloji Polikliniği", "kardiyoloji": "Heyet Kardiyoloji Polikliniği",
    "cilt": "Heyet Cildiye Polikliniği (Oda 1 ve 2)", "cildiye": "Heyet Cildiye Polikliniği (Oda 1 ve 2)",
    "çocuk": "Heyet Çocuk Polk. (Çözger)", "fizik": "Fizik Tedavi Polikliniği 1",
    "göğüs": "Heyet Göğüs Hastalıkları Polikliniği", "diyet": "Diyetisyen (Heyet Diyet)",
    "üroloji": "Heyet Üroloji Polikliniği", "cerrahi": "Heyet Genel Cerrahi Polikliniği",
    "röntgen": "Röntgen / Görüntüleme (DİĞER BİNA)", "film": "Röntgen / Görüntüleme (DİĞER BİNA)",
    "işitme": "ODİO-İşitme Testi Odası", "odio": "ODİO-İşitme Testi Odası"
}

# Session State Başlatma
if "secilen_birim" not in st.session_state:
    st.session_state["secilen_birim"] = "Seçim Yapınız..."
if "kategori" not in st.session_state:
    st.session_state["kategori"] = "🏥 Resmi Poliklinikler / Odalar"
if "ses_izni" not in st.session_state:
    st.session_state["ses_izni"] = False

# ==============================================================================
# 🚀 SES BİLEŞENİ & KROKİ
# ==============================================================================
def otomatik_sesli_oku(metin):
    if metin and metin.strip():
        okunacak_metin = metin.replace("1. Kat", "Birinci Kat").replace("1. kat", "Birinci kat")
        temiz_metin = okunacak_metin.replace("'", "\\'").replace('"', '\\"')
        js_kodu = f"""
        <script>
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance('{temiz_metin}');
                msg.lang = 'tr-TR';
                msg.rate = 1.0; 
                msg.pitch = 1.0; 
                window.speechSynthesis.speak(msg);
            }}
        </script>
        """
        st.components.v1.html(js_kodu, height=0)

def kroki_goster(kat_adi):
    """
    GitHub üzerindeki krokiler/ klasöründen zemin_kat.png veya birinci_kat.png
    görsellerini dinamik ve güvenli bir şekilde arayıp gösterir.
    """
    hedef_prefix = "zemin_kat" if kat_adi == "zemin" else "birinci_kat"
    bulunan_dosya = None
    
    # 1. Öncelik: 'krokiler/' klasörü içi
    klasor_yolu = "krokiler"
    
    if os.path.exists(klasor_yolu):
        for dosya in os.listdir(klasor_yolu):
            if dosya.lower().startswith(hedef_prefix) and dosya.lower().endswith(".png"):
                bulunan_dosya = os.path.join(klasor_yolu, dosya)
                break
                
    # 2. Öncelik: Ana dizin (eğer krokiler klasörü açılmadıysa esneklik sağlar)
    if not bulunan_dosya:
        for dosya in os.listdir("."):
            if dosya.lower().startswith(hedef_prefix) and dosya.lower().endswith(".png"):
                bulunan_dosya = dosya
                break

    if bulunan_dosya:
        try:
            image = Image.open(bulunan_dosya)
            st.image(image, caption=f"🗺️ Resmi {kat_adi.upper()} Krokisi", use_container_width=True)
        except Exception as e:
            st.error(f"🚨 Görsel yüklenirken hata oluştu: {e}")
    else:
        st.warning(f"📸 `krokiler/` klasöründe `{hedef_prefix}.png` dosyası bulunamadı. Lütfen GitHub deponuzdaki dosya adını kontrol edin.")

def birim_sec(birim_adi):
    st.session_state["secilen_birim"] = birim_adi
    if birim_adi in DIGER_ALANLAR:
        st.session_state["kategori"] = "⚙️ Genel ve İdari Birimler"
    elif birim_adi in POLIKLINIKLER:
        st.session_state["kategori"] = "🏥 Resmi Poliklinikler / Odalar"

def akilli_arama_isle(gelen_metin):
    if not gelen_metin:
        return
    temiz_metin = gelen_metin.lower()
    temiz_metin = re.sub(r'[^\w\s]', '', temiz_metin)
    kelimeler = temiz_metin.split()
    tum_birimler = {**POLIKLINIKLER, **DIGER_ALANLAR}

    for kelime in kelimeler:
        if kelime in ES_ANLAMLILAR:
            birim_sec(ES_ANLAMLILAR[kelime])
            return

    for birim in tum_birimler:
        birim_kucuk = birim.lower()
        if temiz_metin in birim_kucuk or birim_kucuk in temiz_metin:
            birim_sec(birim)
            return

    for kelime in kelimeler:
        if len(kelime) >= 3:
            for birim in tum_birimler:
                if kelime in birim.lower():
                    birim_sec(birim)
                    return

    otomatik_sesli_oku(f"Üzgünüm, {gelen_metin} anlaşılamadı. Lütfen listeden seçiniz.")

# ==============================================================================
# 📱 BAŞLIK & KARŞILAMA Mimarisi
# ==============================================================================
st.title("🏥 SDH BARAJ YOLU EK BİNASI")
st.caption("📱 Mobil Sesli Dijital Yönlendirme Sistemi")
st.info(f"📍 **Bulunduğunuz Nokta:** {baslangic_noktasi}")

# 🔔 DOKUNMA İZNİ BİLEŞENİ
if not st.session_state["ses_izni"]:
    st.markdown("""
        <div class="ses-uyari">
            ⚠️ <b>Sesli anlatımı duymak için:</b> Lütfen telefonunuzun sessiz anahtarını (Ringer Switch) kapatın ve sesini açın.
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔊 Sesli Yönlendirmeyi Başlat (Tıklayınız)", use_container_width=True):
        st.session_state["ses_izni"] = True
        otomatik_sesli_oku("Seyhan Devlet Hastanesi Baraj Yolu Ek Hizmet Binası sesli dijital yönlendirme sistemine hoş geldiniz. Lütfen gitmek istediğiniz birimi seçiniz veya mikrofon butonuna basarak konuşunuz.")
        st.rerun()

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
        birim_sec("Tuvaletler / Lavabolar")
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
    secili = st.session_state.get("secilen_birim", "Seçim Yapınız...")
    idx = liste.index(secili) if secili in liste else 0
    
    secim = st.selectbox(
        "GİTMEK İSTEDİĞİNİZ POLİKLİNİĞİ SEÇİNİZ:", 
        liste, 
        index=idx,
        key="sb_poliklinik"
    )
    st.session_state["secilen_birim"] = secim

else:
    liste_alan = ["Seçim Yapınız..."] + list(DIGER_ALANLAR.keys())
    secili = st.session_state.get("secilen_birim", "Seçim Yapınız...")
    idx = liste_alan.index(secili) if secili in liste_alan else 0
    
    secim = st.selectbox(
        "ARADIĞINIZ DİĞER BİRİMLERİ SEÇİNİZ:", 
        liste_alan, 
        index=idx,
        key="sb_diger"
    )
    st.session_state["secilen_birim"] = secim

# ==============================================================================
# 📣 YÖNLENDİRME SONUCU VE SESLENDİRME
# ==============================================================================
secim = st.session_state["secilen_birim"]

if secim != "Seçim Yapınız...":
    tum_birimler = {**POLIKLINIKLER, **DIGER_ALANLAR}
    if secim in tum_birimler:
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
                
        st.write("---")
        if st.button("🔄 Yeni Aramaya Geç / Seçimi Sıfırla", use_container_width=True):
            st.session_state["secilen_birim"] = "Seçim Yapınız..."
            st.rerun()

st.caption("🤖 Barajyolu Ek Hizmet Binası Mobil Dijital Yönlendirme (Engin PEKDEMİR)")
