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

    @PostMapping("/ml/result")
    public ResponseEntity<TelemetryData> receiveMlResult(@RequestBody TelemetryData result) {
        TelemetryData saved = telemetryService.save(result);
        return ResponseEntity.ok(saved);
    }

    @PostMapping("/telemetry")
    public ResponseEntity<TelemetryData> ingest(@RequestBody TelemetryData data) {
        TelemetryData saved = telemetryService.save(data);
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