package com.sarah.secure_dashboard.service;

import com.sarah.secure_dashboard.model.TelemetryData;
import com.sarah.secure_dashboard.repository.TelemetryRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Service
public class TelemetryService {

    private final TelemetryRepository repository;
    private final WebClient webClient;

    @Value("${ml.service.url:http://localhost:8000}")
    private String mlServiceUrl;

    public TelemetryService(TelemetryRepository repository,
                            WebClient.Builder webClientBuilder) {
        this.repository = repository;
        this.webClient = webClientBuilder.build();
    }

    public TelemetryData ingestAndScore(TelemetryData input) {

        Map<String, Object> mlPayload = Map.of(
            "satelliteId", input.getSatelliteId(),
            "temperature", input.getTemperature(),
            "voltage", input.getVoltage(),
            "altitude", input.getAltitude()
        );

        TelemetryData scored;

        try {
            scored = webClient.post()
                .uri(mlServiceUrl + "/predict")
                .bodyValue(mlPayload)
                .retrieve()
                .bodyToMono(TelemetryData.class)
                .block();

            if (scored == null) {
                throw new RuntimeException("ML service returned empty response");
            }
        } catch (WebClientResponseException e) {
            System.err.println("[ERROR] ML service returned error: " + e.getMessage());
            scored = input;
        } catch (Exception e) {
            System.err.println("[ERROR] ML service unreachable: " + e.getMessage());
            scored = input;
        }

        return save(scored);
    }

    public TelemetryData save(TelemetryData data) {
        data.setTimestamp(LocalDateTime.now());
        return repository.save(data);
    }

    public List<TelemetryData> getAll() {
        return repository.findAll();
    }
}