package com.datascrub.backend.dto;

import java.util.List;
import java.util.Map;

public record ProcessResponse(
    boolean success,
    String jobId, // Frontend'in indirme linki oluşturması için ekledik
    String outputFilePath,
    CleaningStats stats,
    List<Map<String, Object>> previewRows
) {
    // Python yanıtına jobId ekleyerek yeni immutable instance döndürür
    public ProcessResponse withJobId(String jobId) {
        return new ProcessResponse(success, jobId, outputFilePath, stats, previewRows);
    }
}
