package com.datascrub.backend.dto;

import java.util.List;

public record CleaningRules(
    List<String> customNaValues,
    boolean dropDuplicates,
    String numericFillStrategy,
    String categoricalFillValue,
    List<String> stripCurrencySymbols,
    boolean standardizeDates
) {
    // Varsayılan kurallar için factory metodu (Frontend kural göndermezse kullanılır)
    public static CleaningRules defaults() {
        return new CleaningRules(
            List.of("ERROR", "UNKNOWN", "N/A"),
            true,
            "median",
            "Unknown",
            List.of(" TL", "$", "€"),
            true
        );
    }
}