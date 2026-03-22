package com.sarah.secure_dashboard.controller;

import com.sarah.secure_dashboard.model.TelemetryData;
import com.sarah.secure_dashboard.service.TelemetryService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
public class TelemetryController {

    private final TelemetryService telemetryService;

    public TelemetryController(TelemetryService telemetryService) {
        this.telemetryService = telemetryService;
    }

    // Main entry point — frontend calls this, Spring Boot calls FastAPI internally
    @PostMapping("/telemetry")
    public ResponseEntity<TelemetryData> ingest(@RequestBody TelemetryData data) {
        TelemetryData saved = telemetryService.ingestAndScore(data);
        return ResponseEntity.ok(saved);
    }

    @GetMapping("/telemetry")
    public List<TelemetryData> all(@RequestParam(required = false) String satelliteId) {
        List<TelemetryData> list = telemetryService.getAll();
        if (satelliteId != null) {
            list.removeIf(d -> !satelliteId.equals(d.getSatelliteId()));
        }
        return list;
    }
}