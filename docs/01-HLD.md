# Üst Düzey Sistem Tasarımı (HLD - High-Level Design)
**Proje:** DataScrub Platformu  
**Mimari Stil:** Polyglot Mikroservis Mimarisi (REST & Dahili Ağ İzolasyonu)

---

## 1. Sistem Mimarisi (Kuş Bakışı Görünüm)

Sistem, sorumlulukların ayrılması (Separation of Concerns) prensibine göre 4 ana bileşenden oluşur:

1. **Client Layer (React + TypeScript):** Kullanıcının dosya yüklediği, temizlik kurallarını seçtiği ve raporları görüntülediği tek sayfa uygulaması (SPA).
2. **Core Backend & API Gateway (Java Spring Boot):** Sistemin orkestratörüdür. Kimlik doğrulama (JWT), dosya saklama, veritabanı yönetimi ve iş akışı kontrolünden sorumludur.
3. **Data Processing Worker (Python FastAPI + Pandas/NumPy):** Dış ağa kapalı çalışan izole veri işleme motorudur. Yüksek performanslı vektörel veri temizleme ve istatistiksel profilleme yapar.
4. **Persistence & Storage Layer (PostgreSQL + Local/S3 Volume):** Kullanıcı bilgileri, işlem geçmişi ve uygulanan kurallar PostgreSQL'de; ham ve temizlenmiş `.csv` dosyaları paylaşımlı dosya depolama alanında (Shared Volume) tutulur.

```mermaid
graph TD
    User((Kullanıcı)) -->|HTTPS / JSON & Multipart| React[React Frontend :3000]
    React -->|REST API + JWT| Spring[Java Spring Boot Core :8080]
    
    subgraph Internal Docker Network [Dahili İzole Ağ]
        Spring -->|JPA / JDBC| Postgres[(PostgreSQL DB :5432)]
        Spring -->|Internal REST HTTP| FastAPI[Python FastAPI Engine :8000]
        Spring <-->|Dosya Okuma/Yazma| Storage[(Shared File Storage)]
        FastAPI <-->|Dosya Okuma/Yazma| Storage
    end
```

---

## 2. Veri Akışı ve Sıralama Diyagramı (Sequence Diagram)

Bir kullanıcının kirli bir `.csv` dosyasını yükleyip temizletme sürecindeki adım adım servisler arası iletişim:

```mermaid
sequenceDiagram
    autonumber
    actor U as Kullanıcı (React)
    participant S as Spring Boot (Core)
    participant DB as PostgreSQL
    participant FS as Shared Storage
    participant P as Python FastAPI (Engine)

    U->>S: POST /api/v1/jobs/clean (CSV Dosyası + Kurallar JSON)
    S->>FS: Ham dosyayı kaydet (/raw/job_123.csv)
    S->>DB: İş kaydı oluştur (Status: PROCESSING)
    S->>P: POST /internal/v1/process (Dosya Yolu + Kurallar JSON)
    
    activate P
    P->>FS: Ham dosyayı oku (Pandas DataFrame)
    P->>P: Temizlik kurallarını uygula (NumPy & Pandas)
    P->>FS: Temiz dosyayı yaz (/cleaned/job_123_clean.csv)
    P-->>S: 200 OK (Öncesi/Sonrası İstatistik Raporu JSON)
    deactivate P

    S->>DB: Kaydı güncelle (Status: COMPLETED, Stats JSON)
    S-->>U: 200 OK (Job ID + Rapor Özeti)
    U->>S: GET /api/v1/jobs/{jobId}/download
    S->>FS: Temiz dosyayı oku
    S-->>U: temiz_veri.csv İndirme Akışı
```

---

## 3. Mimari Kararlar ve Gerekçeler (ADR - Architecture Decision Records)

* **Neden Dosyanın Kendisi Yerine Dosya Yolu (File Path) Gönderiliyor?**  
  Spring Boot ve FastAPI aynı Docker ağı üzerinde ortak bir disk alanını (`Shared Volume`) paylaşır. 50 MB'lık bir dosyayı servisler arasında HTTP üzerinden tekrar tekrar transfer etmek yerine sadece dosya yolunu (`/storage/raw/dosya.csv`) JSON içinde göndermek ağ gecikmesini (latency) ve RAM tüketimini minimuma indirir.
* **Neden İlk Fazda Senkron REST Tercih Edildi?**  
  MVP aşamasında sistem karmaşıklığını (overengineering) önlemek için Spring Boot ve FastAPI arasında doğrudan senkron HTTP iletişimi kurulmuştur. Büyük ölçekli dosyalarda (100 MB+) darboğaz oluşması durumunda Faz 2'de araya RabbitMQ/Kafka mesaj kuyruğu eklenecektir.
* **Neden Python FastAPI Dış Dünyaya Kapalı?**  
  Tüm güvenlik, rate-limiting ve yetkilendirme kontrolleri tek bir merkezden (Spring Security) yönetilmektedir. FastAPI yalnızca iş mantığına ve veri hesaplamasına odaklanır.
