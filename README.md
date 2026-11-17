# DataScrub Platform

DataScrub, CSV dosyalarını temizlemek için React arayüzü, Spring Boot API'si ve Python veri motorundan oluşan küçük bir uygulamadır.

## Gereksinimler

- Java 21 ve Maven
- Python 3
- Node.js ve npm

## Yerel çalıştırma

Üç servisi ayrı terminallerde başlatın.

### 1. Python veri motoru

```powershell
cd engine-python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Spring Boot API

```powershell
cd backend-spring
mvn spring-boot:run
```

### 3. React arayüzü

```powershell
cd frontend-react
npm install
npm run dev
```

Arayüzü [http://localhost:5173](http://localhost:5173) adresinden açın. API `8080`, Python motoru `8000` portunda çalışır.

## Kullanım

Arayüzden bir `.csv` dosyası seçin, temizlik seçeneklerini belirleyip **Veriyi temizle** düğmesine basın. İşlem tamamlanınca özet ve önizleme görüntülenir; temizlenmiş CSV indirilebilir.

## API uçları

- `POST /api/v1/scrub/process` — CSV dosyasını temizler.
- `GET /api/v1/scrub/download/{jobId}` — temizlenmiş CSV'yi indirir.
- `GET /health` — Python motorunun durumunu gösterir.
