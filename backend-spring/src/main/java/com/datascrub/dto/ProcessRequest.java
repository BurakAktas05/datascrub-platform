package com.datascrub.backend.dto;

public record ProcessRequest(
    String jobId,
    String inputFilePath,
    String outputFilePath,
    CleaningRules rules
) {}