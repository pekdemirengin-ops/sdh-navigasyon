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
    "Poliklinik Heyet Fizik Tedavi": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Girişten koridora ilerleyip sol tarafa yönelin. Ön merdivenlerin hemen yanında yer alır.",
        "kroki": "heyet_fizik_tedavi_polk_yol_tarifi.png"
    },
    "Poliklinik Heyet KBB": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Ana girişten girdikten sonra sola dönün. Ön merdivenleri geçince sağ taraftadır.",
        "kroki": "heyet_kbb_polk_yol_tarifi.png"
    },
    "Poliklinik Heyet Ortopedi": {
        "fancy": False, "kat": "zemin",
        "tarif": "Zemin Kat - Girişten koridora girip sola ilerleyin. KBB odasının yanındaki odadır.",
        "kroki": "heyet_ortopedi_polk_yol_tarifi.png"
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
    "Poliklinik Heyet Genel Cerrahi": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Merdivenlerden çıktıktan sonra koridordan sağa yönelin. Koridorun solunda yer almaktadır.",
        "kroki": "heyet_genel_cerrahi_polk_yol_tarifi.png"
    },
    "Poliklinik Heyet Fizik Tedavi (1. Kat)": {
        "fancy": False, "kat": "1kat",
        "tarif": "1. Kat - Koridorda sağa doğru ilerleyin, koridorun sonuna doğru sol tarafta kalmaktadır.",
        "kroki": "heyet_fizik_tedavi_polk_yol_tarifi.png"
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
    "wc": "Tuvaletler / Lavabolar", "lavabo": "Tuvaletler / Lavabolar", "tuvalet": "Tuvaletler / Lavabolar",
    "heyet": "Sağlık Kurulu", "rapor": "Sağlık Kurulu",
    "kulak": "Poliklinik Heyet KBB", "kbb": "Poliklinik Heyet KBB",
    "göz": "Poliklinik Heyet Göz", "kalp": "Poliklinik Heyet Kardiyoloji", "kardiyoloji": "Poliklinik Heyet Kardiyoloji",
    "çocuk": "Poliklinik Heyet Çocuk", "fizik": "Poliklinik Heyet Fizik Tedavi (Zemin)",
    "göğüs": "Poliklinik Heyet Göğüs Hastalıkları", "üroloji": "Poliklinik Heyet Üroloji",
    "cerrahi": "Poliklinik Heyet Genel Cerrahi", "röntgen": "Röntgen / Görüntüleme (DİĞER BİNA)",
    "film": "Röntgen / Görüntüleme (DİĞER BİNA)", "işitme": "İşitme Testi (ODİO)",
    "odio": "İşitme Testi (ODİO)", "dahiliye": "Poliklinik Heyet Dahiliye",
    "nöroloji": "Poliklinik Heyet Nöroloji", "ortopedi": "Poliklinik Heyet Ortopedi",
    "psikiyatri": "Poliklinik Psikiyatri", "cimer": "Sabim Cimer Birimi", "sft": "Solunum Fonksiyon (SFT) Birimi"
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
# 🛠️ YARDIMCI FONKSİYONLAR (ÇOK ESNEK KROKİ BULUCU)
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
    aranan_govde = Path(aranan_tam).stem.lower() # Uzantısız hali (örn: heyet_ortopedi_yol_tarifi)
    
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

    # Tüm olası dizinleri ve alt klasörleri tara
    for dizin in arama_dizinleri:
        if dizin.exists():
            try:
                for dosya in dizin.rglob("*"):
                    if dosya.is_file() and dosya.suffix.lower() in gecerli_uzantilar:
                        dosya_adi_lower = dosya.name.lower()
                        dosya_govde_lower = dosya.stem.lower()
                        
                        # 1. Tam ad eşleşmesi veya gövde eşleşmesi
                        if dosya_adi_lower == aranan_tam or dosya_govde_lower == aranan_govde:
                            bulunan_dosya = dosya
                            break
                        
                        # 2. İçerik esnek eşleşmesi (örn: dosya adında 'ortopedi' geçiyorsa)
                        if aranan_govde in dosya_govde_lower or dosya_govde_lower in aranan_govde:
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
        st.warning(f"⚠️ Kroki Bulunamadı: `{kroki_dosya_adi}` dosyası proje dizininde veya alt klasörlerde okunamadı. Lütfen dosyanın `app.py` ile aynı klasörde veya alt klasörde olduğundan emin olun.")

def birim_sec(birim_adi):
    st.session_state["secilen_birim"] = birim_adi
    if birim_adi in DIGER_ALANLAR:
        st.session_state["kategori"] = "⚙️ Genel ve İdari Birimler"
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
# 🎙️ SESLİ ARAMA (WEB SPEECH API ENTEGRASYONU)
# ==============================================================================
st.write("---")
st.write("### 🔍 Birim Arama / Sesle Konuş")

if "ses_arama" in st.query_params:
    gelen_ses = st.query_params["ses_arama"]
    del st.query_params["ses_arama"]
    if gelen_ses:
        akilli_arama_isle(gelen_ses)

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
                const speechResult = event.results[0][0].transcript;
                statusEl.innerText = "Bulundu: " + speechResult;
                btnEl.style.backgroundColor = '#ff4b4b';
                btnEl.innerText = "🎙️ Konuş";
                
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
                
      
st.caption("🤖 Barajyolu Ek Hizmet Binası Mobil Dijital Yönlendirme (Engin PEKDEMİR)")
