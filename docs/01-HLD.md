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
