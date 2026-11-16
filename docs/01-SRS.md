# Yazılım Gereksinim Spesifikasyonu (SRS)
**Proje Adı:** DataScrub – Otomatik Veri Temizleme ve Analiz Platformu  
**Versiyon:** 1.0 (MVP)  
**Mimari:** Polyglot Mikroservis (React + Java Spring Boot + Python FastAPI + PostgreSQL)

---

## 1. Proje Amacı ve Kapsamı
**DataScrub**, kullanıcıların (veri analistleri, geliştiriciler, işletme sahipleri) kirli, eksik ve tutarsız formatlara sahip `.csv` veri setlerini kod yazmadan web arayüzü üzerinden yükleyebilmelerini, otomatik veri röntgeni çıkarabilmelerini ve seçtikleri kurallara göre veriyi temizleyip raporlayabilmelerini sağlayan uçtan uca bir veri işleme platformudur.

**MVP Kapsam Dışı (Faz 2):**
* Gerçek zamanlı streaming veri akışı ve Kafka/RabbitMQ entegrasyonu.
* `.xlsx` veya veritabanı bağlantısı üzerinden doğrudan veri çekme (MVP'de yalnızca `.csv` desteklenecektir).

---

## 2. Kullanıcı Rolleri (Actors)
* **Kayıtlı Kullanıcı (Standard User):** Sisteme giriş yapabilir, dosya yükleyebilir, temizlik kuralları uygulayabilir, geçmiş işlemlerini görüntüleyebilir ve temizlenmiş dosyaları indirebilir.
* **Sistem Yöneticisi (Admin - Opsiyonel):** Sistemdeki toplam işlem hacmini ve kullanıcı kotalarını görüntüleyebilir.

---

## 3. Fonksiyonel Gereksinimler (Functional Requirements)

### 3.1. Kimlik Doğrulama ve Yetkilendirme (Auth)
* **FR-01:** Kullanıcı e-posta ve şifre ile sisteme kayıt olabilmelidir.
* **FR-02:** Kullanıcı sisteme giriş yaptığında Spring Security üzerinden JWT (JSON Web Token) almalıdır.
* **FR-03:** Her kullanıcı yalnızca kendi yüklediği dosyaları ve temizlik geçmişini görebilmelidir.

### 3.2. Dosya Yükleme ve Veri Röntgeni (Data Profiling)
* **FR-04:** Kullanıcı arayüz üzerinden maksimum 50 MB boyutunda `.csv` dosyası yükleyebilmelidir.
* **FR-05:** Dosya yüklendiğinde sistem otomatik olarak ilk 10 satırlık önizlemeyi ve **Veri Röntgenini** (toplam satır/sütun sayısı, her sütundaki eksik veri oranı, veri tipleri) kullanıcıya sunmalıdır.

### 3.3. Veri Temizleme Motoru (Data Cleaning Engine)
Kullanıcı aşağıdaki kuralları bağımsız olarak seçip uygulayabilmelidir:
* **FR-06 (Sahte Hata Temizliği):** Kullanıcı tarafından tanımlanan hatalı metinler (örn: `"ERROR"`, `"UNKNOWN"`, `"N/A"`) otomatik olarak standart boş değere (`NaN`) dönüştürülmelidir.
* **FR-07 (Tekrar Eden Kayıtlar):** Birebir aynı olan kopya satırlar (`duplicates`) tespit edilip silinebilmelidir.
* **FR-08 (Eksik Veri Yönetimi):** Eksik sayısal veriler kullanıcının seçimine göre; silinebilmeli (`drop`), ortalama (`mean`) veya medyan (`median`) ile doldurulabilmelidir. Eksik metinsel veriler sabit bir etiketle (örn: `"Unknown"`) doldurulabilmelidir.
* **FR-09 (Format Standardizasyonu):** Sayısal sütunlardaki birim/para metinleri (örn: `" TL"`, `"$"`) temizlenip sayısal tipe dönüştürülebilmeli; tarih sütunları standart `YYYY-MM-DD` formatına çevrilebilmelidir.

### 3.4. Raporlama, Dışa Aktarma ve Geçmiş
* **FR-10:** Temizlik işlemi tamamlandığında kullanıcıya **"Öncesi vs Sonrası" (Before/After)** karşılaştırma özeti (silinen satır sayısı, kurtarılan hücre sayısı) gösterilmelidir.
* **FR-11:** Kullanıcı temizlenmiş veri setini `.csv` formatında bilgisayarına indirebilmelidir.
* **FR-12:** Yapılan her temizlik işlemi, uygulanan kurallar ve özet istatistiklerle birlikte PostgreSQL veritabanında geçmiş olarak saklanmalıdır.

---

## 4. Fonksiyonel Olmayan Gereksinimler (Non-Functional Requirements)

* **NFR-01 (Performans):** 100.000 satır ve 20 sütuna kadar olan bir `.csv` dosyasının temizleme ve analiz süresi 5 saniyenin altında olmalıdır.
* **NFR-02 (Güvenlik & İzolasyon):** Veri işleme motoru (Python FastAPI) dış ağa (internete) kapalı olmalı, yalnızca dahili ağ üzerinden Java Spring Boot servisinden gelen istekleri kabul etmelidir. Kullanıcı şifreleri BCrypt ile hash'lenerek saklanmalıdır.
* **NFR-03 (Taşınabilirlik):** Tüm mikroservisler (React, Spring Boot, FastAPI, PostgreSQL) Docker konteynerleri halinde paketlenmeli ve tek bir `docker-compose.yml` dosyası ile ayağa kalkabilmelidir.
* **NFR-04 (Hata Yönetimi):** Bozuk veya okunamayan bir CSV dosyası yüklendiğinde sistem çökmemeli, kullanıcıya anlaşılır bir HTTP 400 (Bad Request) hata mesajı dönmelidir.
* **NFR-05 (Test Kapsamı):** Python veri temizleme çekirdeği için `pytest` ile, Java servis katmanı için `JUnit 5` ile temel birim (unit) testleri yazılmış olmalıdır.
