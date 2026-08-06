function sesliAramaBaslat() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const statusEl = document.getElementById('mic-status');
            const btnEl = document.getElementById('mic-btn');

            if (!SpeechRecognition) {
                alert("Tarayıcınız sesli aramayı desteklemiyor.");
                return;
            }

            // Eğer halihazırda çalışan bir oturum varsa önce kapat
            if (recognition) {
                try { recognition.stop(); } catch(e) {}
            }

            recognition = new SpeechRecognition();
            recognition.lang = 'tr-TR';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;
            recognition.continuous = false; // iOS'te sürekli dinlemeyi engeller

            recognition.onstart = function() {
                btnEl.style.backgroundColor = '#28a745';
                btnEl.innerText = " Dinliyor...";
                statusEl.innerText = "Konuşun...";
            };

            recognition.onresult = function(event) {
                const speechResult = event.results[0][0].transcript.toLowerCase().replace(/[.,\\/#!$%\\^&\\*;:{}=\\-_`~()]/g,"").trim();
                statusEl.innerText = "Bulundu: " + speechResult;
                btnEl.style.backgroundColor = '#ff4b4b';
                btnEl.innerText = "🎙️ Konuş";

                try { recognition.stop(); } catch(e) {}

                const url = new URL(window.parent.location.href);
                url.searchParams.set('ses_arama', speechResult);
                window.parent.location.href = url.toString();
            };

            recognition.onerror = function(event) {
                btnEl.style.backgroundColor = '#ff4b4b';
                btnEl.innerText = "🎙️ Konuş";
                statusEl.innerText = "Hata: " + event.error;
                try { recognition.stop(); } catch(e) {}
            };

            recognition.onend = function() {
                btnEl.style.backgroundColor = '#ff4b4b';
                btnEl.innerText = "🎙️ Konuş";
                statusEl.innerText = "";
            };

            try {
                recognition.start();
            } catch(e) {
                statusEl.innerText = "İzin hatası.";
                btnEl.style.backgroundColor = '#ff4b4b';
                btnEl.innerText = "🎙️ Konuş";
            }
        }
    </script>
    """, height=70)
