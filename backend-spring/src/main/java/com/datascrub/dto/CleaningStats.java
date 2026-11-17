package com.datascrub.backend.dto;

public record CleaningStats(
    int rowsBefore,
    int rowsAfter,
    int columnsCount,
    int duplicatesRemoved,
    int missingValuesBefore,
    int missingValuesAfter,
    long processingTimeMs
) {}