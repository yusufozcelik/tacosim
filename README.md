# 🔌 tacosim – Devre Simülasyon Yazılımı

**tacosim**, Pardus (ve diğer Linux/MacOS sistemleri) üzerinde çalışan, PyQt5 tabanlı bir **etkileşimli devre simülasyon yazılımıdır**.  
Kullanıcılar sürükle-bırak yöntemiyle devre elemanlarını yerleştirip, bunlar arasında bağlantılar kurarak çalışabilir ve simülasyonları görsel olarak izleyebilir.

---

## 🎯 Amaç

- Öğrencilerin elektronik devreleri sanal ortamda kurarak öğrenmelerini sağlamak
- Gerçek dünya ile yazılım arasında bir köprü kurmak
- Mikrodenetleyicilerle haberleşen sistemleri görselleştirmek
- Seri port üzerinden veri alıp buna göre devre davranışını gösterebilmek (ileri aşama)

---

## 🧱 Mevcut Devre Elemanları

| Eleman     | Açıklama                                      | Pin Sayısı |
|------------|-----------------------------------------------|------------|
| 🔋 Batarya  | VCC ve GND çıkışı sağlar                      | 2          |
| 💡 LED      | VCC ve GND doğru bağlanırsa yanar             | 2          |
| 🔸 Direnç   | Değeri ayarlanabilir (Ω, kΩ, MΩ)               | 2          |

---

## ⚙️ Özellikler

✅ Sürükle-bırak ile sahneye eleman ekleme  
✅ Pinleri tıklayarak kablo ile bağlama  
✅ Bağlantı noktalarını dinamik takip eden kablolar  
✅ Sağ tıklayarak eleman/kablo silme veya özelliğini değiştirme  
✅ Simülasyon başlatıldığında LED gibi elemanlar otomatik olarak tepki verir  
✅ Direnç üzerine tıklayarak değerini değiştirme (örn. 220Ω, 1kΩ)  
✅ Dinamik pin yapısı: tüm elemanlar `self.pins` üzerinden işlenir  
✅ Simülasyon başladığında bağlantı yolu analiz edilir (örn. Batarya ↔ Direnç ↔ LED)

---

## 🔍 Simülasyon Davranışı

| Durum                                    | LED Durumu        |
|------------------------------------------|-------------------|
| VCC ↔ LED.VCC, GND ↔ LED.GND             | 🔴 Yanıyor        |
| VCC ↔ Direnç ↔ LED.VCC, GND ↔ LED.GND    | 🔴 Yanıyor        |
| Ters bağlantı (GND ↔ VCC)                | 🟤 Ters bağlı      |
| Bağlantı eksik                           | ⚫ Sönük (boşta)   |

---

## ⌨️ Kısayollar

- `Delete` tuşu → Seçili kablo/eleman silinir  
- Sağ tık kabloda → Rengini değiştir / Sil  
- Sağ tık dirençte → Değer ayarla  
- “Simülasyonu Başlat” butonu → Başlat/Durdur arasında geçiş yapar

---

## 🚀 Kurulum

1. Gerekli paketleri yükle:

```bash
pip install -r requirements.txt