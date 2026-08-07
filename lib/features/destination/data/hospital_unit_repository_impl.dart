import '../domain/models/hospital_unit.dart';
import '../domain/repositories/hospital_unit_repository.dart';

class HospitalUnitRepositoryImpl implements HospitalUnitRepository {
  const HospitalUnitRepositoryImpl();

  static const _units = <HospitalUnit>[
    HospitalUnit(id: 'unit-1', name: 'Heyet Çocuk (Çözger) Poliklinik', floor: 'Zemin Kat', directions: 'Zemin Kat - Girişten koridora girip sola ilerleyin. KBB odasının yanındaki odadır.', mapAsset: 'cozger_polk_yol_tarifi.png'),
    HospitalUnit(id: 'unit-2', name: 'Heyet Fizik Tedavi Poliklinik', floor: 'Zemin Kat', directions: 'Zemin Kat - Girişten koridora ilerleyip sol tarafa yönelin. Ön merdivenlerin hemen yanında yer alır.', mapAsset: 'heyet_fizik_tedavi_polk_yol_tarifi.png'),
    HospitalUnit(id: 'unit-3', name: 'Heyet KBB Poliklinik', floor: 'Zemin Kat', directions: 'Zemin Kat - Ana girişten girdikten sonra sola dönün. Ön merdivenleri geçince sağ taraftadır.', mapAsset: 'heyet_kbb_polk_yol_tarifi.png'),
    HospitalUnit(id: 'unit-4', name: 'Heyet Ortopedi Poliklinik', floor: 'Zemin Kat', directions: 'Zemin Kat - Girişten koridora girip sola ilerleyin. KBB odasının yanındaki odadır.', mapAsset: 'heyet_ortopedi_polk_yol_tarifi.png'),
    HospitalUnit(id: 'unit-5', name: 'Heyet Çocuk Psikiyatri Poliklinik', floor: 'Zemin Kat', directions: 'Zemin Kat - Girişten koridora girip sola ilerleyin. KBB odasının yanındaki odadır.', mapAsset: 'heyet_cocuk_psikiyatri_polk_yol_tarifi.png'),
    HospitalUnit(id: 'unit-6', name: 'Kan Alma Birimi', floor: 'Zemin Kat', directions: 'Zemin Kat - Poliklinik binası girişinden girdikten sonra düz ilerleyip sağ taraftaki Kan Alma odasına geçebilirsiniz.', mapAsset: 'kan_alma_yol_tarifi.png'),
    HospitalUnit(id: 'unit-7', name: 'Sağlık Kurulu', floor: 'Zemin Kat', directions: 'Zemin Kat - Ana girişten girdikten sonra sağa doğru ilerleyin. Koridorun sonundaki geniş alanda yer almaktadır.', mapAsset: 'saglık_kurulu_yol_tarifi.png'),
    HospitalUnit(id: 'unit-8', name: 'Sağlık Kurulu Kayıt Birimi', floor: 'Zemin Kat', directions: 'Zemin Kat - Girişten hemen sonra düz devam edin, sol taraftaki bankoda yer almaktadır.', mapAsset: 'saglık_kurulu_kayıt_yol_tarifi.png'),
    HospitalUnit(id: 'unit-9', name: 'Ön Merdivenler', floor: 'Zemin Kat', directions: 'Zemin Kat - Girişten girdikten sonra sola yönelin, koridor boyunca düz ilerleyerek ön merdivenlere ulaşabilirsiniz.', mapAsset: 'on_merdivenler_yol_tarifi.png'),
    HospitalUnit(id: 'unit-10', name: 'Arka Çıkış', floor: 'Zemin Kat', directions: 'Zemin Kat - Koridordan sola ilerleyin, ön merdivenleri geçip sola dönerek arka çıkış kapısına ulaşabilirsiniz.', mapAsset: 'arka_cıkıs_yol_tarifi.png'),
    HospitalUnit(id: 'unit-11', name: 'Heyet Genel Cerrahi Poliklinik', floor: '1. Kat', directions: '1. Kat - Merdivenlerden çıktıktan sonra koridordan sağa yönelin. Koridorun solunda yer almaktadır.', mapAsset: 'heyet_genel_cerrahi_polk_yol_tarifi.png'),
    HospitalUnit(id: 'unit-12', name: 'Fizik Tedavi 2 Poliklinik', floor: '1. Kat', directions: '1. Kat - Koridorda sağa doğru ilerleyin, koridorun sonuna doğru sağ tarafta kalmaktadır.', mapAsset: 'fizik_tedavi_polk2_yol_tarifi.png'),
    HospitalUnit(id: 'unit-13', name: 'Heyet Nöroloji Poliklinik', floor: '1. Kat', directions: '1. Kat - Ana koridorda sağa doğru son noktaya kadar ilerleyin, sol taraftaki oda.', mapAsset: 'heyet_noroloji_polk_yol_tarifi.png'),
    HospitalUnit(id: 'unit-14', name: 'Görme Alanı Ölçüm Odası', floor: '1. Kat', directions: '1. Kat - Koridorda düz devam edin, sağa dönmeden önceki sol hizada bulunan Alan Görme odasıdır.', mapAsset: 'gorme_alanı_yol_tarifi.png'),
    HospitalUnit(id: 'unit-15', name: 'Heyet Dahiliye Poliklinik', floor: '1. Kat', directions: '1. Kat - Koridor boyunca sağa doğru ilerleyin. Sağ taraftaki odalardan biridir.', mapAsset: 'heyet_dahiliye_polk_yol_tarifi.png'),
    HospitalUnit(id: 'unit-16', name: 'Heyet Göğüs Hastalıkları Poliklinik', floor: '1. Kat', directions: '1. Kat - Merdivenlerden çıktıktan hemen sonra sol çaprazda yer almaktadır.', mapAsset: 'heyet_gogus_hastalıkları_polk_yol_tarifi.png'),
    HospitalUnit(id: 'unit-17', name: 'Heyet Göz Poliklinik', floor: '1. Kat', directions: '1. Kat - Merdivenlerden çıkıp sola dönün, en uçtaki sol odadır.', mapAsset: 'heyet_goz_polk_yol_tarifi.png'),
    HospitalUnit(id: 'unit-18', name: 'Konuşma Terapisti', floor: '1. Kat', directions: '1. Kat - Merdivenlerden çıkınca arka merdiven yönüne (sola) dönün, koridorun sonunda sol taraftadır.', mapAsset: 'konusma_terapisti_yol_tarifi.png'),
    HospitalUnit(id: 'unit-19', name: 'Heyet Kardiyoloji Poliklinik', floor: '1. Kat', directions: '1. Kat - Ana koridorda sağa doğru sonuna kadar ilerleyin. Sağ taraftaki en son odadır.', mapAsset: 'heyet_kardiyoloji_polk_yol_tarifi.png'),
    HospitalUnit(id: 'unit-20', name: 'Heyet Üroloji Poliklinik', floor: '1. Kat', directions: '1. Kat - Merdivenlerden çıkıp sola dönün. Koridorun sonundaki sol oda.', mapAsset: 'heyet_uroloji_polk_yol_tarifi.png'),
    HospitalUnit(id: 'unit-21', name: 'İşitme Testi (Odio)', floor: '1. Kat', directions: '1. Kat - Sağa doğru ilerleyin, test odası koridorun sağ tarafında kalmaktadır.', mapAsset: 'isitme_testi_birimi_yol_tarifi.png'),
    HospitalUnit(id: 'unit-22', name: 'Göz OCT Odası', floor: '1. Kat', directions: '1. Kat - Koridorda sağa doğru ilerleyin, İşitme Testi odasının hemen yanında sağda yer alır.', mapAsset: 'goz_oct_yol_tarifi.png'),
    HospitalUnit(id: 'unit-23', name: 'Göz Ölçüm', floor: '1. Kat', directions: '1. Kat - Merdivenlerden çıkıp sola yönelin, ilk sol kapıdan girin.', mapAsset: 'goz_olcum_yol_tarifi.png'),
    HospitalUnit(id: 'unit-24', name: 'Nöroloji Poliklinik', floor: '1. Kat', directions: '1. Kat - Merdivenlerden çıktıktan sonra sağa dönün ve koridor boyunca ilerleyin. Sol tarafta kalmaktadır.', mapAsset: 'noroloji_polk_yol_tarifi.png'),
    HospitalUnit(id: 'unit-25', name: 'Heyet Psikiyatri Poliklinik', floor: '1. Kat', directions: '1. Kat - Merdivenlerden çıkıp sağ koridora ilerleyin, orta hizada yer alan psikiyatri poliklinikleridir.', mapAsset: 'heyet_psikiyatri_polk_yol_tarifi.png'),
    HospitalUnit(id: 'unit-26', name: 'Sabim Cimer Birimi', floor: '1. Kat', directions: '1. Kat - Merdivenlerden çıktıktan sonra arka merdiven yönüne (sola) dönün, koridoru takip edin.', mapAsset: 'sabim_cimer_yol_tarifi.png'),
    HospitalUnit(id: 'unit-27', name: 'Solunum Fonksiyon (SFT) Birimi', floor: '1. Kat', directions: '1. Kat - Arka merdiven koridorunu geçip sola doğru ilerlediğinizde sol tarafta yer alır.', mapAsset: 'solunum_fonksiyon_yol_tarifi..png'),
    HospitalUnit(id: 'unit-28', name: 'Evrak Kayıt / Vezne', floor: 'Zemin Kat', directions: 'Zemin Kat - Ana girişten tam karşınızda.', mapAsset: 'evrak_kayıt_vezne_yol_tarifi.png'),
    HospitalUnit(id: 'unit-29', name: 'Hasta Kayıt', floor: 'Zemin Kat', directions: 'Ana girişte sol tarafta yer alır.', mapAsset: 'hasta_kayıt_yol_tarifi.png'),
    HospitalUnit(id: 'unit-30', name: 'Evde Sağlık Hizmetleri Birimi', floor: 'Zemin Kat', directions: 'Zemin Katta olup girişi binanın kuzey yönündedir.', mapAsset: 'evde_saglık_hizmetleri_yol_tarifi.png'),
    HospitalUnit(id: 'unit-31', name: 'Röntgen / Görüntüleme (DİĞER BİNA)', floor: 'Diğer Bina', directions: 'Diğer binadadır! Röntgen birimi bu binada değildir. Arka kapıdan çıkınca sola dönün, ardından sağa, ileride sağ tarafta yer alır.', mapAsset: 'arka_cıkıs_yol_tarifi.png'),
    HospitalUnit(id: 'unit-32', name: 'Asansör', floor: 'Zemin Kat', directions: '1. katta binanın tam orta kesiminde, zemin katta Hasta Kayıt bankosunun geçince sol tarafta yer alır.', mapAsset: 'asansor_yol_tarifi.png'),
    HospitalUnit(id: 'unit-33', name: 'Emzirme Odası', floor: '1. Kat', directions: '1. Kat - Koridor boyunca sağa doğru ilerleyin. Sağ taraftaki odalardan biridir.', mapAsset: 'emzirme_odası_yol_tarifi.png'),
    HospitalUnit(id: 'unit-34', name: 'Tuvaletler / Lavabolar', floor: 'Zemin Kat', directions: 'Zemin Katta: Ana girişten sonra sola dönün. Koridorun sonunda yer alır.', mapAsset: 'tuvaletler_yol_tarifi.png'),
  ];

  @override
  Future<List<HospitalUnit>> getAll() async => _units;
}
