package com.datascrub.backend.service;

import com.datascrub.backend.dto.CleaningRules;
import com.datascrub.backend.dto.ProcessRequest;
import com.datascrub.backend.dto.ProcessResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.UUID;

@Service
public class ScrubService {

    private final RestClient pythonEngineRestClient;
    private final Path rawStorageDir;
    private final Path cleanedStorageDir;

    public ScrubService(
            RestClient pythonEngineRestClient,
            @Value("${datascrub.storage.base-dir}") String baseDir) throws IOException {
        this.pythonEngineRestClient = pythonEngineRestClient;
        Path basePath = Paths.get(baseDir).toAbsolutePath().normalize();
        this.rawStorageDir = basePath.resolve("raw");
        this.cleanedStorageDir = basePath.resolve("cleaned");

        // Uygulama kalkarken klasörleri otomatik oluştur
        Files.createDirectories(this.rawStorageDir);
        Files.createDirectories(this.cleanedStorageDir);
    }

    public ProcessResponse processCsv(MultipartFile file, CleaningRules rules) {
        validateCsvFile(file);

        String jobId = UUID.randomUUID().toString();
        String fileName = jobId + ".csv";

        Path inputPath = rawStorageDir.resolve(fileName);
        Path outputPath = cleanedStorageDir.resolve(fileName);

        try {
            // 1. Ham dosyayı paylaşımlı diske kaydet
            Files.copy(file.getInputStream(), inputPath, StandardCopyOption.REPLACE_EXISTING);
        } catch (IOException e) {
            throw new RuntimeException("Dosya diske kaydedilemedi: " + e.getMessage(), e);
        }

        // 2. Python FastAPI motoruna gönderilecek isteği hazırla
        CleaningRules activeRules = (rules != null) ? rules : CleaningRules.defaults();
        ProcessRequest engineRequest = new ProcessRequest(
                jobId,
                inputPath.toString(),
                outputPath.toString(),
                activeRules
        );

        // 3. Python servisini senkron çağır
        ProcessResponse engineResponse = pythonEngineRestClient.post()
                .uri("/internal/v1/process")
                .contentType(MediaType.APPLICATION_JSON)
                .body(engineRequest)
                .retrieve()
                .body(ProcessResponse.class);

        if (engineResponse == null || !engineResponse.success()) {
            throw new IllegalStateException("Python veri işleme motorundan geçersiz yanıt döndü.");
        }

        return engineResponse.withJobId(jobId);
    }

    public Resource getCleanedFile(String jobId) {
        // Path traversal güvenliği: Sadece geçerli UUID kabul et
        UUID validUuid = UUID.fromString(jobId);
        Path filePath = cleanedStorageDir.resolve(validUuid + ".csv").normalize();

        if (!Files.exists(filePath)) {
            throw new IllegalArgumentException("Temizlenmiş dosya bulunamadı: " + jobId);
        }
        return new FileSystemResource(filePath);
    }

    private void validateCsvFile(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("Yüklenen dosya boş olamaz.");
        }
        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null || !originalFilename.toLowerCase().endsWith(".csv")) {
            throw new IllegalArgumentException("Sadece .csv uzantılı dosyalar desteklenmektedir.");
        }
    }
}