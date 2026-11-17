import os
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from app.schemas import ProcessRequest, ProcessResponse
from app.cleaner import clean_dataframe

app = FastAPI(
    title="DataScrub Python Data Engine",
    description="Pandas & NumPy tabanlı yüksek performanslı veri temizleme mikroservisi",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    """Servisin ayakta olup olmadığını kontrol etmek için (Docker & Spring Boot kullanır)"""
    return {"status": "UP", "service": "engine-python"}

@app.post("/internal/v1/process", response_model=ProcessResponse)
def process_csv_file(request: ProcessRequest):
    # 1. Ham dosya gerçekten diskte var mı kontrol et
    if not os.path.exists(request.inputFilePath):
        raise HTTPException(
            status_code=404, 
            detail=f"Girdi dosyası bulunamadı: {request.inputFilePath}"
        )

    try:
        # 2. CSV dosyasını oku
        df = pd.read_csv(request.inputFilePath)

        # 3. Temizlik motorunu çalıştır
        cleaned_df, stats = clean_dataframe(df, request.rules)

        # 4. Çıktı klasörü yoksa oluştur ve temiz CSV'yi kaydet
        os.makedirs(os.path.dirname(request.outputFilePath), exist_ok=True)
        cleaned_df.to_csv(request.outputFilePath, index=False)

        # 5. İlk 5 satırlık önizlemeyi JSON uyumlu sözlük listesine çevir
        # (JSON içinde NaN bulunamayacağı için kalan olası NaN'ları None/null yapıyoruz)
        preview_df = cleaned_df.head(5).replace({np.nan: None})
        preview_rows = preview_df.to_dict(orient="records")

        return ProcessResponse(
            success=True,
            outputFilePath=request.outputFilePath,
            stats=stats,
            previewRows=preview_rows
        )

    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Veri işleme sırasında hata oluştu: {str(e)}"
        )