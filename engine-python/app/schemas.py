from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CleaningRules(BaseModel):
    customNaValues: List[str] = Field(default=["ERROR", "UNKNOWN", "N/A"])
    dropDuplicates: bool = Field(default=True)
    numericFillStrategy: Optional[str] = Field(default="median")  # "median", "mean", "drop", None
    categoricalFillValue: Optional[str] = Field(default="Unknown")
    stripCurrencySymbols: List[str] = Field(default=[" TL", "$", "€"])
    standardizeDates: bool = Field(default=True)

class ProcessRequest(BaseModel):
    jobId: str
    inputFilePath: str
    outputFilePath: str
    rules: CleaningRules

class CleaningStats(BaseModel):
    rowsBefore: int
    rowsAfter: int
    columnsCount: int
    duplicatesRemoved: int
    missingValuesBefore: int
    missingValuesAfter: int
    processingTimeMs: int

class ProcessResponse(BaseModel):
    success: bool
    outputFilePath: str
    stats: CleaningStats
    previewRows: List[Dict[str, Any]]