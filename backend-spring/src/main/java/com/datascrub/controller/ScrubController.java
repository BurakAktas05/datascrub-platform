package com.datascrub.backend.controller;

import com.datascrub.backend.dto.CleaningRules;
import com.datascrub.backend.dto.ProcessResponse;
import com.datascrub.backend.service.ScrubService;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/v1/scrub")
public class ScrubController {

    private final ScrubService scrubService;

    public ScrubController(ScrubService scrubService) {
        this.scrubService = scrubService;
    }

    @PostMapping(value = "/process", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<ProcessResponse> uploadAndProcess(
            @RequestPart("file") MultipartFile file,
            @RequestPart(value = "rules", required = false) CleaningRules rules) {

        ProcessResponse response = scrubService.processCsv(file, rules);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/download/{jobId}")
    public ResponseEntity<Resource> downloadCleanedCsv(@PathVariable String jobId) {
        Resource resource = scrubService.getCleanedFile(jobId);

        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType("text/csv"))
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"cleaned_" + jobId + ".csv\"")
                .body(resource);
    }
}