import streamlit as st
import os
from PIL import Image

# Sayfa Ayarları
st.set_page_config(page_title="SDH Navigasyon", page_icon="🏥", layout="centered")

st.title("🏥 SDH Barajyolu Ek Hizmet Binası")
st.subheader("SDH Yapay Zeka Navigasyonu")
st.info("📍 Başlangıç Noktası: Poliklinik Binası Ana Girişi (Zemin Kat)")

# ==============================================================================
# 🚀 OTOMATİK SESLİ TARİF MOTORU
# ==============================================================================
def otomatik_sesli_oku(metin):
    """Tarayıcı üzerinden belirtilen metni otomatik olarak seslendirir."""
    if metin and metin.strip():
        okunacak_metin = metin.replace("1. Kat", "Birinci Kat").replace("1. kat", "Birinci kat")
        temiz_metin = okunacak_metin.replace("'", "\\'").replace('"', '\\"')
        js_kodu = f"""
        <script>
            var msg = new SpeechSynthesisUtterance('{temiz_metin}');
            msg.lang = 'tr-TR';
            msg.rate = 1.0; 
            msg.pitch = 1.0; 
            window.speechSynthesis.cancel(); // Önceki sesleri sustur
            window.speechSynthesis.speak(msg);
        </script>
        """
        st.components.v1.html(js_kodu, height=0)

# İlk açılışta tek seferlik karşılama anonsu
if "karsilandi" not in st.session_state:
    st.session_state["karsilandi"] = True
    otomatik_sesli_oku("Seyhan Devlet Hastanesi navigasyon sistemine hoş geldiniz. Lütfen gitmek istediğiniz birimi seçiniz veya sesle arama butonunu kullanınız.")

# ==============================================================================
# 🎙️ SES TANIMA (MİKROFON) MOTORU
# ==============================================================================
def sesle_arama_motoru():
    """Vatandaşın sesini dinler ve arama kutusuna yazar."""
    js_ses_kodu = """
    <div style="text-align: center; margin-bottom: 15px;">
        <button id="mic-btn" style="background-color: #d9534f; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 25px; cursor: pointer; font-weight: bold; width: 100%;">
            🎙️ Konuşarak Poliklinik Ara (Mikrofona Basın)
        </button>
        <p id="status-text" style="color: gray; font-size: 14px; margin-top: 5px;">Mikrofona basıp gitmek istediğiniz yeri söyleyin.</p>
    </div>
    <script>
        const btn = document.getElementById('mic-btn');
        const status = document.getElementById('status-text');
        
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.lang = 'tr-TR';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            btn.onclick = function() {
                recognition.start();
                btn.style.backgroundColor = '#5cb85c';
                btn.innerText = '🔴 Sizi Dinliyorum...';
                status.innerText = 'Şimdi hastane içindeki birimi söyleyin...';
            };

            recognition.onresult = function(event) {
                const sonucMetni = event.results[0][0].transcript;
                btn.style.backgroundColor = '#d9534f';
                btn.innerText = '🎙️ Konuşarak Poliklinik Ara (Mikrofona Basın)';
                status.innerText = 'Anlaşılan: "' + sonucMetni + '"';
                
                // Streamlit'e veriyi gizli bir input veya URL parametresi üzerinden pasla
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: sonucMetni}, '*');
            };

            recognition.onerror = function(event) {
                btn.style.backgroundColor = '#d9534f';
                btn.innerText = '🎙️ Konuşarak Poliklinik Ara (Mikrofona Basın)';
                status.innerText = 'Ses anlaşılamadı, lütfen tekrar deneyin.';
            };
            
            recognition.onend = function() {
                btn.style.backgroundColor = '#d9534f';
                btn.innerText = '🎙️ Konuşarak Poliklinik Ara (Mikrofona Basın)';
            };
        } else {
            btn.style.display = 'none';
            status.innerText = 'Tarayıcınız ses tanıma özelliğini desteklemiyor.';
        }
    </script>
    """
    # HTML ve JS kodunu Streamlit'e enjekte eder ve dönen sonucu yakalar
    return st.components.v1.html(js_ses_kodu, height=90, scrolling=False)

# 🚀 AKILLI GÖRSEL BULUCU MOTORU
def kroki_goster(kat_adi):
    """Klasörde kat_adi ile başlayan (png, jpg, jpeg vb.) herhangi bir resmi bulur."""
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
        st.warning(f"📸 Klasörde [{hedef_prefix}] ile başlayan bir kroki görseli bulunamadı. Lütfen resim ismini kontrol edin.")

# 1. RESMİ PLAN POLİKLİNİKLER VE TIBBİ ODALAR VERİ TABANI
POLIKLINIKLER = {
    "Seçim Yapınız...": {"fancy": False, "tarif": "", "kat": ""},
    "Görme Alanı Ölçüm Odası": {"fancy": False, "tarif": "1. Kat - Merdivenlerden veya asansörden çıkıp sağa dönün. Koridorun ortasında, sol sıradaki odadır (Heyet Çocuk - ÇÖZGER polikliniğinin hemen yanındadır).", "kat": "1kat"},
    "Çocuk Gelişimi Birimi": {"fancy": False, "tarif": "1. Kat - Arka merdivenlerden çıkınca tam karşınızdadır.", "kat": "1kat"},
    "Göz-OCT / Göz Ölçüm Odası": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkıp sağ koridora yönelin. Koridorun ortasında, sol taraftaki odadır (Fizik Tedavi 2 polikliniğinin hemen yanında).", "kat": "1kat"},
    "Solunum Fonksiyon Testi Odası": {"fancy": False, "tarif": "1. Kat - Arka merdivenlerden çıkınca tam sol koridorun en başında, sağ taraftaki odadır.", "kat": "1kat"},
    "İşitme Testi Odası": {"fancy": False, "tarif": "1. Kat - Merdivenlerden veya asansörden çıkıp sağa dönün. Koridorun ortasında, sağ taraftaki odadır (Emzirme Odası yanı).", "kat": "1kat"},
    "Emzirme Odası": {"fancy": False, "tarif": "1. Kat - Merdivenlerden veya asansörden çıkıp sağa dönün. Koridorun ortasında, sağ taraftaki odadır (İşitme Testi yanı).", "kat": "1kat"},
    "Cildiye Heyet Polikliniği (Oda 1 ve 2)": {"fancy": False, "tarif": "1. Kat - Merdivenlerden sağa dönün, sağğ tarafta yan yanadır veya asansörden çıkınca sol dönün, sol tarafta yan yanadır.", "kat": "1kat"},
    "Çocuk Hastalıkları Polikliniği (DİĞER BİNA GİRİŞİ)": {"fancy": True, "tarif": "🚨 DİĞER BİNA GİRİŞİNDEDİR! Çocuk hastalıkları poliklinik muayeneleri için lütfen diğer bina girişini kullanınız.", "kat": ""},
    "Heyet Çocuk Polk. (Çözger)": {"fancy": False, "tarif": "1. Kat - Merdivenlerden veya asansörden çıkıp sağa dönün. Koridorun ortasında sol taraftadır (Görme Alanı odasının hemen yanındadır).", "kat": "1kat"},
    "Heyet Çocuk Psikiyatri Polk.": {"fancy": False, "tarif": "1. Kat - Arka merdivenlerden çıkınca sol koridorun sonundan 1 önceki soldaki odadır. (Çocuk Evde Sağlık odasının yanı).", "kat": "1kat"},
    "Dahiliye Polikliniği": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkıp sağa dönün. Koridorun sonundaki sağ taraftaki odadır (Fizik Tedavi 2 polikliniğinin yanı).", "kat": "1kat"},
    "Fizik Tedavi Polikliniği 1": {"fancy": False, "tarif": "Zemin Kat - Ana girişten girdikten sonra hemen sol taraftaki koridorda yer alır.", "kat": "zemin"},
    "Fizik Tedavi Polikliniği 2": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkıp sağa dönün. Sağ koridorun sonuna doğru sağ taraftadır (Dahiliye yanındadır).", "kat": "1kat"},
    "Fizik Tedavi Polikliniği 3": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkıp sağa dönün. Koridorun ortasında, sol taraftaki odadır.", "kat": "1kat"},
    "Heyet Genel Cerrahi Polikliniği": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkıp sağ koridora yönelin. Sol sırada Genel Cerrahi Pansuman odasının yanındadır.", "kat": "1kat"},
    "Heyet Göğüs Hastalıkları Polikliniği": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkınca tam karşınızda yer almaktadır.", "kat": "1kat"},
    "Heyet Göz Polikliniği": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkınca sola doğru karşınızda, (Göz Ölçüm odasının yanı).", "kat": "1kat"},
    "Heyet Kardiyoloji Polikliniği": {"fancy": False, "tarif": "1. Kat - Merdivenlerden veya asansörden çıkıp sağa dönün. Koridorun en sonunda sol taraftaki odadır.", "kat": "1kat"},
    "Heyet K.B.B. Polikliniği (Oda 1 ve 2)": {"fancy": False, "tarif": "Zemin Kat - Giriş kapısından girdikten sonra sola dönün. Sağ taraftaki odadır.", "kat": "zemin"},
    "Nöroloji Polikliniği / Heyet Nöroloji": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkıp sağ koridora yönelin. Sol sırada, Göğüs Hastalıkları ile Genel Cerrahi odalarının arasındadır.", "kat": "1kat"},
    "Heyet Ortopedi Polikliniği": {"fancy": False, "tarif": "Zemin Kat - Giriş kapısından girdikten sonra tam sola doğru karşınızda. Koridorun ortasında.", "kat": "zemin"},
    "Heyet Psikiyatri Polikliniği": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkıp sağ koridora yönelin. Sol sırada, Çözger alanının hemen sol tarafında kalan odalardır.", "kat": "1kat"},
    "Heyet Üroloji Polikliniği": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkınca sol koridorda, sol sıradaki ilk odadır (Göz Heyet odasının yanı).", "kat": "1kat"},
    "Diyetisyen (Heyet Diyet)": {"fancy": False, "tarif": "Zemin Kat - Giriş kapısından girdikten sonra tam karşınızda. Ortopedi Heyet odasının yanındadır.", "kat": "zemin"},
    "Heyet Psikolog": {"fancy": False, "tarif": "1. Kat - Merdivenlerden çıkınca sol koridorda, asansörün hemen yanındaki odadır.", "kat": "1kat"},
    "Konuşma Terapisi Birimi": {"fancy": False, "tarif": "1. Kat - Arka merdivenlerden çıkınca sol koridorun en sonundaki odadır (Sabim Cimer odasının yanı).", "kat": "1kat"}
}
# 2. RESMİ PLAN DİĞER BİRİMLER VE GENEL ALANLAR VERİ TABANI
DIGER_ALANLAR = {
    "Seçim Yapınız...": {"fancy": False, "tarif": "", "kat": ""},
    "Tuvaletler / Lavabolar (WC)": {"fancy": False, "tarif": "Zemin Katta: Giriş kapısından sola dönüp ilerleyin koridorun sonunda yer alır.", "kat": "zemin"},
    "Sağlık Kurulu / Heyet Odası": {"fancy": False, "tarif": "Zemin Kat - Giriş kapısından girdiğinizde sağ tarafınızda yer almaktadır.", "kat": "zemin"},
    "Kan Alma": {"fancy": False, "tarif": "Zemin Kat - Giriş kapısından içeri girdiğinizde hemen sağ köşededir.", "kat": "zemin"},
    "Evrak Kayıt / Vezne": {"fancy": False, "tarif": "Zemin Kat - Giriş kapısından içeri girdiğinizde tam karşınızda.", "kat": "zemin"},
    "Evde Sağlık Hizmetleri Birimi": {"fancy": False, "tarif": "Zemin Katta olup girişi binanın kuzey yönündedir .", "kat": "zemin"},
    "Röntgen / Görüntüleme (DİĞER BİNA)": {"fancy": True, "tarif": "🚨 DİĞER BİNADADIR! Röntgen birimi bu binada değildir. Lütfen ana binadan çıkıp diğer binaya geçiş yapınız.", "kat": ""},
    "Asansör": {"fancy": False, "tarif": "Zemin ve 1. Kat - Binanın tam orta kesiminde, bankonun hemen yanında yer alır.", "zelin": "zemin", "kat": "zemin"},
}
# 🎙️ SES TANIMA (MİKROFON) MOTORU FONKSİYONU
# ==============================================================================
def sesle_arama_motoru():
    """Vatandaşın sesini dinler ve arama kutusuna yazar."""
    js_ses_kodu = """
    <div style="text-align: center; margin-bottom: 15px;">
        <button id="mic-btn" style="background-color: #d9534f; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 25px; cursor: pointer; font-weight: bold; width: 100%;">
            🎙️ Konuşarak Poliklinik Ara (Mikrofona Basın)
        </button>
        <p id="status-text" style="color: gray; font-size: 14px; margin-top: 5px;">Mikrofona basıp gitmek istediğiniz yeri söyleyin.</p>
    </div>
    <script>
        const btn = document.getElementById('mic-btn');
        const status = document.getElementById('status-text');
        
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.lang = 'tr-TR';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            btn.onclick = function() {
                recognition.start();
                btn.style.backgroundColor = '#5cb85c';
                btn.innerText = '🔴 Sizi Dinliyorum...';
                status.innerText = 'Şimdi hastane içindeki birimi söyleyin...';
            };

            recognition.onresult = function(event) {
                const sonucMetni = event.results[0][0].transcript;
                btn.style.backgroundColor = '#d9534f';
                btn.innerText = '🎙️ Konuşarak Poliklinik Ara (Mikrofona Basın)';
                status.innerText = 'Anlaşılan: "' + sonucMetni + '"';
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: sonucMetni}, '*');
            };

            recognition.onerror = function(event) {
                btn.style.backgroundColor = '#d9534f';
                btn.innerText = '🎙️ Konuşarak Poliklinik Ara (Mikrofona Basın)';
                status.innerText = 'Ses anlaşılamadı, lütfen tekrar deneyin.';
            };
        } else {
            btn.style.display = 'none';
            status.innerText = 'Tarayıcınız ses tanıma özelliğini desteklemiyor.';
        }
    </script>
    """
    return st.components.v1.html(js_ses_kodu, height=100, scrolling=False)

# ==============================================================================
# MİKROFON BUTONU VE AKILLI EŞLEŞTİRME SİSTEMİ
# ==============================================================================
ses_sonucu = sesle_arama_motoru()
varsayilan_secim = "Seçim Yapınız..."

if ses_sonucu is not None and str(ses_sonucu).strip() != "":
    seslenilen_kelime = str(ses_sonucu).lower()
    tum_birimler = list(POLIKLINIKLER.keys()) + list(DIGER_ALANLAR.keys())
    for birim in tum_birimler:
        if seslenilen_kelime in birim.lower() and birim != "Seçim Yapınız...":
            varsayilan_secim = birim
            break

# ==============================================================================
# ARAYÜZ KATMANI
# ==============================================================================
st.write("### 👇 Lütfen Gitmek İstediğiniz Kategoriyi Seçiniz:")

kategori_varsayilan = 0
if varsayilan_secim in DIGER_ALANLAR:
    kategori_varsayilan = 1

kategori = st.radio("Navigasyon Modu", ["🏥 Resmi Poliklinikler / Odalar", "⚙️ Genel ve İdari Birimler"], index=kategori_varsayilan, horizontal=True, label_visibility="collapsed")
st.write("---")

if "Poliklinikler" in kategori:
    liste = list(POLIKLINIKLER.keys())
    # 📌 Kritik Düzeltme: list.index hatası 'liste.index' olarak düzeltildi
    idx = liste.index(varsayilan_secim) if varsayilan_secim in POLIKLINIKLER else 0
    
    secim = st.selectbox("Gitmek istediğiniz Polikliniği veya Muayene Odasını seçiniz:", liste, index=idx)
    if secim != "Seçim Yapınız...":
        veri = POLIKLINIKLER[secim]
        if veri['fancy']:
            st.error(f"🎯 Hedef Birim: {secim}")
            st.error(f"🚶 Yönlendirme: {veri['tarif']}")
            otomatik_sesli_oku(f"Dikkat. {veri['tarif']}")
        else:
            st.success(f"🎯 Hedef Birim: {secim}")
            st.warning(f"🚶 Resmi Plan Yol Tarifi: {veri['tarif']}")
            otomatik_sesli_oku(f"{secim} için yol tarifi. {veri['tarif']}")
            if veri["kat"]:
                kroki_goster(veri["kat"])

elif "Genel ve İdari" in kategori:
    liste_alan = list(DIGER_ALANLAR.keys())
    idx_alan = liste_alan.index(varsayilan_secim) if varsayilan_secim in DIGER_ALANLAR else 0
    
    secim = st.selectbox("Aradığınız Genel veya İdari Birimi seçiniz:", liste_alan, index=idx_alan)
    if secim != "Seçim Yapınız...":
        veri = DIGER_ALANLAR[secim]
        if veri['fancy']:
            st.error(f"🎯 Hedef Alan: {secim}")
            st.error(f"🚶 Yönlendirme: {veri['tarif']}")
            otomatik_sesli_oku(f"Dikkat. {veri['tarif']}")
        else:
            st.success(f"🎯 Hedef Alan: {secim}")
            st.warning(f"🚶 Resmi Plan Yol Tarifi: {veri['tarif']}")
            otomatik_sesli_oku(f"{secim} için yol tarifi. {veri['tarif']}")
            if veri["kat"]:
                kroki_goster(veri["kat"])

st.caption("🤖 Seyhan Devlet Hastanesi Barajyolu Ek Hizmet Binası Sesli Ditital Yönlendirme Sistemi v1.7")

