import pandas as pd
import numpy as np
from fastapi.testclient import TestClient
from app.main import app
from app.cleaner import clean_dataframe
from app.schemas import CleaningRules

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP", "service": "engine-python"}

def test_clean_dataframe_logic():
    # Bilerek kirli bir mini tablo oluşturuyoruz
    dirty_data = pd.DataFrame({
        "Item": ["Coffee", "Tea", "Coffee", "ERROR", None],
        "Price": ["100 TL", "200 TL", "100 TL", "UNKNOWN", "300 TL"],
        "Order_Date": ["2023-09-08", "2023/09/09", "2023-09-08", "invalid", "2023-09-10"]
    })

    rules = CleaningRules(
        customNaValues=["ERROR", "UNKNOWN"],
        dropDuplicates=True,
        numericFillStrategy="median",
        categoricalFillValue="Unknown",
        stripCurrencySymbols=[" TL"],
        standardizeDates=True
    )

    cleaned_df, stats = clean_dataframe(dirty_data, rules)

    # Beklentilerimizi doğruluyoruz (Assertions)
    assert stats.rowsBefore == 5
    assert stats.duplicatesRemoved == 1          # 2 tane Coffee satırından 1'i silinmeli
    assert stats.rowsAfter == 4
    assert stats.missingValuesAfter == 0         # Hiç boşluk kalmamalı
    assert cleaned_df["Price"].median() == 200.0 # Medyan doğru hesaplanmalı
    assert "Unknown" in cleaned_df["Item"].values