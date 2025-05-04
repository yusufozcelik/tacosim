# 🧪 TACOSIM - Devre Simülatörü

TACOSIM, Python (PyQt5) ile geliştirilen bir görsel devre simülasyon aracıdır. Sürükle-bırak destekli arayüzü ile elektronik bileşenlerin yerleştirilip, birbirine bağlanmasını sağlar ve simülasyon sırasında voltaj, akım ve direnç değerlerini takip eder.

---

## 🚀 Özellikler

- 🔋 Batarya, direnç ve LED gibi temel bileşenler
- 🧩 Bağlantılar arası kapalı devre kontrolü
- ⚙️ Ayarlanabilir batarya voltajı ve direnç değeri
- 💡 LED parlaklığı akıma göre ayarlanır
- 🧠 Simülasyon motoru kapalı devre takibi yapar
- 📊 Status bar üzerinden V / I / R görüntüleme
- 📁 JSON ile projeyi kaydetme ve yükleme
- 🐛 Geliştirici log sistemi ile hata ayıklama

---

## 🛠️ Kurulum

```bash
git clone https://github.com/yusufozcelik/tacosim.git
cd tacosim
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

---

## 🧑‍💻 Geliştirici Bilgileri

### 📂 Proje Yapısı

- `main.py`: Uygulama giriş noktası
- `gui/`: Tüm arayüz öğeleri ve bağlantı yöneticisi
- `components/`: Devre elemanlarının sınıfları
- `simulation_engine.py`: Akım ve voltaj simülasyonu
- `logger.py`: Geliştirici log kayıt sistemi
- `assets/`: Logo, ikon ve statik görseller

### 💻 Geliştirici Notları

- Her eleman için `to_dict()` / `from_dict()` metodları vardır
- `DynamicWire` kablolar da JSON ile kayıt edilir
- Bağlantılar `connected_pin` ile çift yönlü tutulur
- `MainWindow` içindeki `save_scene_to_json()` / `load_scene_from_json()` işlevseldir

### 🔄 Simülasyon Motoru

TACOSIM, `SimulationEngine` sınıfı üzerinden devre üzerinde tam bir **kapalı devre** olup olmadığını kontrol eder. Devre tamamsa:

- Toplam direnç hesaplanır
- Voltaj akıma dönüştürülür
- LED gibi bileşenlere akım/voltaj uygulanır

Kapalı devre değilse, simülasyon başlatılsa bile etkisiz olur.

---

## 📄 Lisans

MIT Lisansı

---

## 🏫 Geliştirenler

> Bu yazılım, **TACETTİN ASLAN MTAL** öğrencileri tarafından  
> **TEKNOFEST** yarışması için geliştirilmektedir.

📅 Proje Başlangıç: 2025
🧪 Amaç: Eğitimde elektronik devre öğretimini sadeleştirmek

---

## ✨ Katkıda Bulun

Pull Request göndermekten çekinme! Özellikle şu konularda katkılar açığız:

- Yeni bileşenler (potansiyometre, kapasitör vs.)
- Simülasyon optimizasyonları
- UI/UX iyileştirmeleri