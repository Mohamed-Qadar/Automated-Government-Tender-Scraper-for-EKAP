"""Domain constants: tender types, categories, statuses, sources and the
official list of 81 Turkish provinces with plate codes."""

# --- Tender types (İhale Türü) ---
TENDER_TYPE_YAPIM = "YAPIM"
TENDER_TYPE_MAL = "MAL"
TENDER_TYPE_HIZMET = "HIZMET"
TENDER_TYPE_DANISMANLIK = "DANISMANLIK"

TENDER_TYPE_CHOICES = [
    (TENDER_TYPE_YAPIM, "Yapım"),
    (TENDER_TYPE_MAL, "Mal Alımı"),
    (TENDER_TYPE_HIZMET, "Hizmet Alımı"),
    (TENDER_TYPE_DANISMANLIK, "Danışmanlık"),
]

# --- Categories (Kategori) ---
CATEGORY_CHOICES = [
    ("yapim_ihaleleri", "Yapım İhaleleri"),
    ("mal_alimi", "Mal Alımı İhaleleri"),
    ("hizmet_alimi", "Hizmet Alımı İhaleleri"),
    ("danismanlik", "Danışmanlık İhaleleri"),
    ("duzeltme_ilanlari", "Düzeltme İlanları"),
    ("iptal_ilanlari", "İptal İlanları"),
    ("ihale_sonuclari", "İhale Sonuçları"),
    ("kesinlesen_sonuclar", "Kesinleşen Sonuçlar"),
    ("dogrudan_temin", "Doğrudan Temin"),
    ("elektrik_mekanik", "Elektrik ve Mekanik İşler"),
    ("insaat_altyapi", "İnşaat ve Altyapı"),
    ("arac_makine", "Araç ve Makine"),
    ("gida", "Gıda"),
    ("temizlik", "Temizlik"),
    ("guvenlik", "Güvenlik"),
    ("saglik", "Sağlık"),
    ("yazilim_otomasyon", "Yazılım ve Otomasyon"),
    ("egitim", "Eğitim"),
    ("belediye_hizmetleri", "Belediye Hizmetleri"),
    ("ulasim", "Ulaşım"),
    ("enerji", "Enerji"),
    ("diger", "Diğer"),
]

# --- Tender procedure (İhale Usulü) ---
PROCEDURE_CHOICES = [
    ("acik", "Açık İhale Usulü"),
    ("belli_istekliler", "Belli İstekliler Arasında İhale"),
    ("pazarlik", "Pazarlık Usulü"),
    ("dogrudan_temin", "Doğrudan Temin"),
    ("diger", "Diğer"),
]

# --- Status (Durum) ---
STATUS_ACTIVE = "aktif"
STATUS_RESULT = "sonuclandi"
STATUS_FINALIZED = "kesinlesti"
STATUS_CANCELLED = "iptal"
STATUS_CORRECTION = "duzeltme"

STATUS_CHOICES = [
    (STATUS_ACTIVE, "Aktif / Açık"),
    (STATUS_RESULT, "Sonuçlandı"),
    (STATUS_FINALIZED, "Kesinleşti"),
    (STATUS_CANCELLED, "İptal"),
    (STATUS_CORRECTION, "Düzeltme"),
]

# --- Source (Kaynak) ---
SOURCE_EKAP = "EKAP"
SOURCE_RESMI_GAZETE = "RESMI_GAZETE"
SOURCE_MOCK = "MOCK"

SOURCE_CHOICES = [
    (SOURCE_EKAP, "EKAP (Elektronik Kamu Alımları Platformu)"),
    (SOURCE_RESMI_GAZETE, "Resmî Gazete"),
    (SOURCE_MOCK, "Örnek / Demo Veri"),
]

ALL_TURKIYE = "ALL"  # sentinel for "Tüm Türkiye"

# --- 81 provinces with plate codes ---
PROVINCES = [
    (1, "Adana"), (2, "Adıyaman"), (3, "Afyonkarahisar"), (4, "Ağrı"),
    (5, "Amasya"), (6, "Ankara"), (7, "Antalya"), (8, "Artvin"),
    (9, "Aydın"), (10, "Balıkesir"), (11, "Bilecik"), (12, "Bingöl"),
    (13, "Bitlis"), (14, "Bolu"), (15, "Burdur"), (16, "Bursa"),
    (17, "Çanakkale"), (18, "Çankırı"), (19, "Çorum"), (20, "Denizli"),
    (21, "Diyarbakır"), (22, "Edirne"), (23, "Elazığ"), (24, "Erzincan"),
    (25, "Erzurum"), (26, "Eskişehir"), (27, "Gaziantep"), (28, "Giresun"),
    (29, "Gümüşhane"), (30, "Hakkâri"), (31, "Hatay"), (32, "Isparta"),
    (33, "Mersin"), (34, "İstanbul"), (35, "İzmir"), (36, "Kars"),
    (37, "Kastamonu"), (38, "Kayseri"), (39, "Kırklareli"), (40, "Kırşehir"),
    (41, "Kocaeli"), (42, "Konya"), (43, "Kütahya"), (44, "Malatya"),
    (45, "Manisa"), (46, "Kahramanmaraş"), (47, "Mardin"), (48, "Muğla"),
    (49, "Muş"), (50, "Nevşehir"), (51, "Niğde"), (52, "Ordu"),
    (53, "Rize"), (54, "Sakarya"), (55, "Samsun"), (56, "Siirt"),
    (57, "Sinop"), (58, "Sivas"), (59, "Tekirdağ"), (60, "Tokat"),
    (61, "Trabzon"), (62, "Tunceli"), (63, "Şanlıurfa"), (64, "Uşak"),
    (65, "Van"), (66, "Yozgat"), (67, "Zonguldak"), (68, "Aksaray"),
    (69, "Bayburt"), (70, "Karaman"), (71, "Kırıkkale"), (72, "Batman"),
    (73, "Şırnak"), (74, "Bartın"), (75, "Ardahan"), (76, "Iğdır"),
    (77, "Yalova"), (78, "Karabük"), (79, "Kilis"), (80, "Osmaniye"),
    (81, "Düzce"),
]

# A small sample of districts for demo provinces (extend freely in admin/seed).
SAMPLE_DISTRICTS = {
    "Elazığ": ["Merkez", "Kovancılar", "Karakoçan", "Palu", "Baskil", "Maden",
               "Sivrice", "Arıcak", "Keban", "Ağın", "Alacakaya"],
    "İstanbul": ["Kadıköy", "Beşiktaş", "Şişli", "Üsküdar", "Bakırköy",
                 "Beyoğlu", "Fatih", "Maltepe", "Pendik", "Esenyurt"],
    "Ankara": ["Çankaya", "Keçiören", "Yenimahalle", "Mamak", "Etimesgut",
               "Sincan", "Altındağ", "Pursaklar", "Gölbaşı", "Polatlı"],
    "İzmir": ["Konak", "Bornova", "Karşıyaka", "Buca", "Bayraklı",
              "Çiğli", "Gaziemir", "Karabağlar", "Menemen", "Torbalı"],
}
