import time
import pandas as pd
import numpy as np
from app.schemas import CleaningRules, CleaningStats

def clean_dataframe(df: pd.DataFrame, rules: CleaningRules) -> tuple[pd.DataFrame, CleaningStats]:
    start_time = time.time()

    rows_before = len(df)
    columns_count = len(df.columns)
    
    # 1. Sahte hata metinlerini ("ERROR", "UNKNOWN" vb.) gerçek NaN yap
    if rules.customNaValues:
        df = df.replace(rules.customNaValues, np.nan)

    missing_before = int(df.isnull().sum().sum())

    # 2. Tekrar eden (Duplicate) satırları sil
    duplicates_removed = 0
    if rules.dropDuplicates:
        dup_count = int(df.duplicated().sum())
        df = df.drop_duplicates()
        duplicates_removed = dup_count

    # 3. Para birimi/metin sembollerini temizle ve sayıya çevirmeyi dene
    if rules.stripCurrencySymbols:
        for col in df.select_dtypes(include=['object']).columns:
            # Sütundaki değerlerin içinde para birimi geçiyorsa temizle
            for symbol in rules.stripCurrencySymbols:
                if df[col].astype(str).str.contains(symbol, regex=False).any():
                    df[col] = df[col].astype(str).str.replace(symbol, '', regex=False)
                    df[col] = pd.to_numeric(df[col], errors='coerce')

    # 4. Tarih sütunlarını standartlaştır (İsminde 'date' veya 'tarih' geçen sütunlar)
    if rules.standardizeDates:
        for col in df.columns:
            if 'date' in col.lower() or 'tarih' in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')

    # 5. Sayısal sütunlardaki eksikleri yönet (median / mean / drop)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if rules.numericFillStrategy == "median":
        for col in numeric_cols:
            df[col] = df[col].fillna(df[col].median())
    elif rules.numericFillStrategy == "mean":
        for col in numeric_cols:
            df[col] = df[col].fillna(df[col].mean())
    elif rules.numericFillStrategy == "drop":
        df = df.dropna(subset=numeric_cols)

    # 6. Metinsel (Kategorik) sütunlardaki eksikleri doldur
    categorical_cols = df.select_dtypes(include=['object']).columns
    if rules.categoricalFillValue is not None:
        for col in categorical_cols:
            df[col] = df[col].fillna(rules.categoricalFillValue)

    rows_after = len(df)
    missing_after = int(df.isnull().sum().sum())
    processing_time_ms = int((time.time() - start_time) * 1000)

    stats = CleaningStats(
        rowsBefore=rows_before,
        rowsAfter=rows_after,
        columnsCount=columns_count,
        duplicatesRemoved=duplicates_removed,
        missingValuesBefore=missing_before,
        missingValuesAfter=missing_after,
        processingTimeMs=processing_time_ms
    )

    return df, stats