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
# 🗄️ MERKEZİ VERİ TABANI (POLİKLİNİKLER VE DİĞER BİRİMLER)
# ==============================================================================
POLIKLINIKLER = {
    "Poliklinik Heyet Fizik Tedavi (Zemin)": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Girişten koridora ilerleyip sol tarafa yönelin. Ön merdivenlerin hemen yanında yer alır.",
        "kroki": "heyet_fizik_zemin_yol_tarifi.png"
    },
    "Poliklinik Heyet KBB": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Ana girişten girdikten sonra sola dönün. Ön merdivenleri geçince sağ taraftadır.",
        "kroki": "heyet_kbb_yol_tarifi.png"
    },
    "Poliklinik Heyet Ortopedi": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Girişten koridora girip sola ilerleyin. KBB odasının yanındaki odadır.",
        "kroki": "heyet_ortopedi_yol_tarifi.png"
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
    "Poliklinik Heyet Genel Cerrahi": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıktıktan sonra koridordan sağa yönelin. Koridorun solunda yer almaktadır.",
        "kroki": "heyet_genel_yol_tarifi.png"
    },
    "Poliklinik Heyet Fizik Tedavi (1. Kat)": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Koridorda sağa doğru ilerleyin, koridorun sonuna doğru sol tarafta kalmaktadır.",
        "kroki": "heyet_fizik_1kat_yol_tarifi.png"
    },
    "Poliklinik Heyet Nöroloji": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Ana koridorda sağa doğru son noktaya kadar ilerleyin, sol taraftaki oda.",
        "kroki": "heyet_noroloji_polk_yol_tarifi.png"
    },
    "Görme Alanı Ölçüm Odası": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Koridorda düz devam edin, sağa dönmeden önceki sol hizada bulunan Alan Görme odasıdır.",
        "kroki": "alan_gorme_yol_tarifi.png"
    },
    "Poliklinik Heyet Dahiliye": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Koridor boyunca sağa doğru ilerleyin. Sağ taraftaki odalardan biridir.",
        "kroki": "heyet_dahiliye_yol_tarifi.png"
    },
    "Olgu Göğüs Hastalıkları": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıktıktan hemen sonra sol çaprazda yer almaktadır.",
        "kroki": "olgu_gogus_yol_tarifi.png"
    },
    "Poliklinik Heyet Göğüs Hastalıkları": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıkınca hemen sol tarafta yer almaktadır.",
        "kroki": "heyet_gogus_yol_tarifi.png"
    },
    "Poliklinik Heyet Göz": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıkıp sola dönün, en uçtaki sol odadır.",
        "kroki": "heyet_goz_yol_tarifi.png"
    },
    "Poliklinik Heyet Çocuk": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıkınca arka merdiven yönüne (sola) dönün, koridorun sonunda sol taraftadır.",
        "kroki": "heyet_cocuk_yol_tarifi.png"
    },
    "Konuşma Terapisti Birimi": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Arka merdiven koridorunu geçip güney koridoru boyunca düz ilerleyin. Koridorun en sonundaki odadır.",
        "kroki": "konusma_terapisi_yol_tarifi.png"
    },
    "Poliklinik Heyet Kardiyoloji": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Ana koridorda sağa doğru sonuna kadar ilerleyin. Sağ taraftaki en son odadır.",
        "kroki": "heyet_kardiyoloji_yol_tarifi.png"
    },
    "Poliklinik Heyet Üroloji": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıkıp sola dönün. Koridorun sonundaki sol oda.",
        "kroki": "heyet_uroloji_yol_tarifi.png"
    },
    "İşitme Testi (ODİO)": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Sağa doğru ilerleyin, test odası koridorun sağ tarafında kalmaktadır.",
        "kroki": "isitme_testi_yol_tarifi.png"
    },
    "Göz OCT Odası": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Koridorda sağa doğru ilerleyin, İşitme Testi odasının hemen yanında sağda yer alır.",
        "kroki": "goz_oct_yol_tarifi.png"
    },
    "Göz Ölçüm Birimi": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıkıp sola yönelin, ilk sol kapıdan girin.",
        "kroki": "goz_olcum_birimi_yol_tarifi.png"
    },
    "Poliklinik Nöroloji": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıktıktan sonra sağa dönün ve koridor boyunca ilerleyin. Sol tarafta kalmaktadır.",
        "kroki": "noroloji_yol_tarifi.png"
    },
    "Poliklinik Psikiyatri": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıkıp sağ koridora ilerleyin, orta hizada yer alan psikiyatri poliklinikleridir.",
        "kroki": "psikiyatri_yol_tarifi.png"
    },
    "Sabim Cimer Birimi": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıktıktan sonra arka merdiven yönüne (sola) dönün, koridoru takip edin.",
        "kroki": "cimer_yol_tarifi.png"
    },
    "Solunum Fonksiyon (SFT) Birimi": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Arka merdiven koridorunu geçip sola doğru ilerlediğinizde sol tarafta yer alır.",
        "kroki": "sft_yol_tarifi.png"
    }
}

DIGER_ALANLAR = {
    "Evrak Kayıt / Vezne": {
        "fancy": False, "kat": "zemin", 
        "tarif": "Zemin Kat - Ana girişten tam karşınızda.", 
        "kroki": "evrak_kayit_yol_tarifi.png"
    },
    "Hasta Kayıt": {
        "fancy": False, "kat": "zemin", 
        "tarif": "Ana girişte sol tarafta yer alır.", 
        "kroki": "hasta_kayit_yol_tarifi.png"
    },
    "Evde Sağlık Hizmetleri Birimi": {
        "fancy": False, "kat": "zemin", 
        "tarif": "Zemin Katta olup girişi binanın kuzey yönündedir.", 
        "kroki": "evde_saglik_yol_tarifi.png"
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
    "Tuvaletler / Lavabolar": {
        "fancy": False, "kat": "zemin", 
        "tarif": "Zemin Katta: Ana girişten sonra sola dönün. Koridorun sonunda yer alır.", 
        "kroki": "tuvalet_yol_tarifi.png"
    }
}


ES_ANLAMLILAR = {
    "kan": "Kan Alma Birimi", "tahlil": "Kan Alma Birimi", "laboratuvar": "Kan Alma Birimi",
    "heyet": "Sağlık Kurulu", "rapor": "Sağlık Kurulu", "kurul": "Sağlık Kurulu",
    "kulak": "Poliklinik Heyet KBB", "kbb": "Poliklinik Heyet KBB",
    "göz": "Poliklinik Heyet Göz", "kalp": "Poliklinik Heyet Kardiyoloji", "kardiyoloji": "Poliklinik Heyet Kardiyoloji",
    "çocuk": "Poliklinik Heyet Çocuk", "fizik": "Poliklinik Heyet Fizik Tedavi (Zemin)",
    "göğüs": "Poliklinik Heyet Göğüs Hastalıkları", "üroloji": "Poliklinik Heyet Üroloji", 
    "cerrahi": "Poliklinik Heyet Genel Cerrahi", "işitme": "İşitme Testi (ODİO)", 
    "odio": "İşitme Testi (ODİO)", "oct": "Göz OCT Odası", "sft": "Solunum Fonksiyon (SFT) Birimi"
}

# Session State Başlatma
if "secilen_birim" not in st.session_state:
    st.session_state["secilen_birim"] = "Seçim Yapınız..."
if "ses_izni" not in st.session_state:
    st.session_state["ses_izni"] = False
if "ses_hizi" not in st.session_state:
    st.session_state["ses_hizi"] = 1.0
if "gecmis_aramalar" not in st.session_state:
    st.session_state["gecmis_aramalar"] = []

# ==============================================================================
# 🚀 SES BİLEŞENİ & AKILLI KROKİ YÜKLEME
# ==============================================================================
def otomatik_sesli_oku(metin):
    if metin and metin.strip():
        okunacak_metin = metin.replace("1. Kat", "Birinci Kat").replace("1. kat", "Birinci kat")
        temiz_metin = okunacak_metin.replace("'", "\\'").replace('"', '\\"')
        hiz = st.session_state.get("ses_hizi", 1.0)
        js_kodu = f"""
        <script>
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance('{temiz_metin}');
                msg.lang = 'tr-TR';
                msg.rate = {hiz}; 
                msg.pitch = 1.0; 
                window.speechSynthesis.speak(msg);
            }}
        </script>
        """
        st.components.v1.html(js_kodu, height=0)

def kroki_goster_dosya(kroki_dosya_yolu):
    """
    Krokiyi hem verilen yoldan hem de alternatif dosya uzantılarından bulup gösterir.
    """
    if not kroki_dosya_yolu:
        st.warning("⚠️ Bu birim için kroki tanımlanmamış.")
        return

    mevcut_klasor = os.path.dirname(os.path.abspath(__file__))
    tam_yol = os.path.join(mevcut_klasor, kroki_dosya_yolu)
    
    bulunan_dosya = None

    # 1. Doğrudan tam yolu kontrol et
    if os.path.exists(tam_yol):
        bulunan_dosya = tam_yol
    else:
        # 2. 'krokiler' klasörünü veya ana klasörü tarayarak eşleşen görseli ara
        dosya_adi = os.path.basename(kroki_dosya_yolu)
        temel_isim = os.path.splitext(dosya_adi)[0].lower()
        
        arama_klasorleri = [
            os.path.join(mevcut_klasor, "krokiler"),
            mevcut_klasor
        ]
        
        for hedef_klasor in arama_klasorleri:
            if os.path.exists(hedef_klasor):
                for dosya in os.listdir(hedef_klasor):
                    dosya_kucuk = dosya.lower()
                    if temel_isim in dosya_kucuk and dosya_kucuk.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        bulunan_dosya = os.path.join(hedef_klasor, dosya)
                        break
            if bulunan_dosya:
                break

    # Ekrana Bas
    if bulunan_dosya:
        try:
            image = Image.open(bulunan_dosya)
            st.image(image, caption=f"🗺️ Konum Krokisi", use_container_width=True)
        except Exception as e:
            st.error(f"🚨 Görsel dosyası bozuk veya açılamadı: {e}")
    else:
        st.error(f"❌ Kroki Dosyası Bulunamadı: **{kroki_dosya_yolu}**")
        st.info(f"💡 Lütfen GitHub deponuzdaki `krokiler` klasöründe `{os.path.basename(kroki_dosya_yolu)}` dosyasının yüklü olduğundan emin olun.")

def birim_sec(birim_adi):
    st.session_state["secilen_birim"] = birim_adi
    if birim_adi not in st.session_state["gecmis_aramalar"] and birim_adi != "Seçim Yapınız...":
        st.session_state["gecmis_aramalar"].insert(0, birim_adi)
        st.session_state["gecmis_aramalar"] = st.session_state["gecmis_aramalar"][:3]

def akilli_arama_isle(gelen_metin):
    if not gelen_metin:
        return
    temiz_metin = gelen_metin.lower()
    temiz_metin = re.sub(r'[^\w\s]', '', temiz_metin)
    kelimeler = temiz_metin.split()

    for kelime in kelimeler:
        if kelime in ES_ANLAMLILAR:
            birim_sec(ES_ANLAMLILAR[kelime])
            return

    for birim in POLIKLINIKLER:
        birim_kucuk = birim.lower()
        if temiz_metin in birim_kucuk or birim_kucuk in temiz_metin:
            birim_sec(birim)
            return

    for kelime in kelimeler:
        if len(kelime) >= 3:
            for birim in POLIKLINIKLER:
                if kelime in birim.lower():
                    birim_sec(birim)
                    return

    otomatik_sesli_oku(f"Üzgünüm, {gelen_metin} anlaşılamadı. Lütfen listeden seçiniz.")

# ==============================================================================
# 📱 BAŞLIK & KARŞILAMA
# ==============================================================================
st.title("🏥 SDH BARAJ YOLU EK BİNASI")
st.caption("📱 Mobil Sesli Dijital Yönlendirme Sistemi")
st.info(f"📍 **Bulunduğunuz Nokta:** {baslangic_noktasi}")

if not st.session_state["ses_izni"]:
    st.markdown("""
        <div class="ses-uyari">
            ⚠️ <b>Sesli anlatımı duymak için:</b> Lütfen telefonunuzun sesini açınız.
        </div>
    """, unsafe_allow_html=True)
    
    col_izni, col_hiz = st.columns([2.5, 1.5])
    with col_izni:
        if st.button("🔊 Sesli Yönlendirmeyi Başlat", use_container_width=True):
            st.session_state["ses_izni"] = True
            otomatik_sesli_oku("Seyhan Devlet Hastanesi sesli dijital yönlendirme sistemine hoş geldiniz. Lütfen gitmek istediğiniz birimi seçiniz.")
            st.rerun()
    with col_hiz:
        hiz_secim = st.selectbox("🔊 Ses Hızı", [0.8, 1.0, 1.2], index=1, format_func=lambda x: f"{x}x Hız")
        st.session_state["ses_hizi"] = hiz_secim

# ==============================================================================
# 🕒 SON ARAMALAR (GEÇMİŞ)
# ==============================================================================
if st.session_state["gecmis_aramalar"]:
    st.write("⏱️ **Son Arananlar:**")
    g_cols = st.columns(len(st.session_state["gecmis_aramalar"]))
    for i, g_birim in enumerate(st.session_state["gecmis_aramalar"]):
        with g_cols[i]:
            if st.button(f"📌 {g_birim[:12]}...", key=f"gecmis_{i}", use_container_width=True):
                birim_sec(g_birim)

# ==============================================================================
# 🚀 HIZLI ERİŞİM BUTONLARI
# ==============================================================================
st.write("### 🚀 Sık Kullanılan Birimler")
m_col1, m_col2 = st.columns(2)

with m_col1:
    if st.button("🩸 KAN ALMA", use_container_width=True):
        birim_sec("Kan Alma Birimi")
    if st.button("📋 S.K. KAYIT", use_container_width=True):
        birim_sec("Sağlık Kurulu Kayıt Birimi")

with m_col2:
    if st.button("🏥 SAĞLIK KURULU", use_container_width=True):
        birim_sec("Sağlık Kurulu")
    if st.button("👁️ GÖZ OCT ODASI", use_container_width=True):
        birim_sec("Göz OCT Odası")

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
        placeholder="Örn: Dahiliye, Kan alma, Göz...",
        key="arama_input"
    )

if ses_metni:
    akilli_arama_isle(ses_metni)
elif metin_girisi and metin_girisi != st.session_state.get("son_metin", ""):
    st.session_state["son_metin"] = metin_girisi
    akilli_arama_isle(metin_girisi)

# ==============================================================================
# 🖥️ ARAYÜZ KATMANI (BİRİM SEÇİMİ)
# ==============================================================================
st.write("---")

liste = ["Seçim Yapınız..."] + list(POLIKLINIKLER.keys())
if st.session_state["secilen_birim"] not in liste:
    st.session_state["secilen_birim"] = "Seçim Yapınız..."
    
secim = st.selectbox(
    "GİTMEK İSTEDİĞİNİZ BİRİM VEYA POLİKLİNİĞİ SEÇİNİZ:", 
    liste, 
    key="secilen_birim"
)

# ==============================================================================
# 📣 YÖNLENDİRME SONUCU VE KROKİ GÖSTERİMİ
# ==============================================================================
if secim != "Seçim Yapınız...":
    veri = POLIKLINIKLER[secim]
    
    st.success(f"🎯 **Hedef Birim:** {secim}")
    st.info(f"📍 **Bulunduğu Kat:** {veri['kat'].upper()}")
    st.warning(f"🚶 **Yol Tarifi:** {veri['tarif']}")
    
    # Sesli Okuma
    otomatik_sesli_oku(f"{secim} için yol tarifi. {veri['tarif']}")
    
    # Birime Özel Kroki Görselini Yükleme
    if "kroki" in veri and veri["kroki"]:
        kroki_goster_dosya(veri["kroki"])
            
    st.write("---")
    if st.button("🔄 Seçimi Sıfırla", use_container_width=True):
        st.session_state["secilen_birim"] = "Seçim Yapınız..."
        st.rerun()

st.caption("🤖 Barajyolu Ek Hizmet Binası Mobil Dijital Yönlendirme Sürümü")
