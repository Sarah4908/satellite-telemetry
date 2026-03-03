package com.sarah.secure_dashboard.model;

import jakarta.persistence.*;
import lombok.Data;

import java.time.LocalDateTime;

@Entity
@Data
public class TelemetryData {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String satelliteId;
    private double temperature;
    private double voltage;
    private double altitude;

    // fields produced by the ML service
    @com.fasterxml.jackson.annotation.JsonProperty("temp_delta")
    private double tempDelta;
    @com.fasterxml.jackson.annotation.JsonProperty("volt_delta")
    private double voltDelta;
    @com.fasterxml.jackson.annotation.JsonProperty("rolling_temp_mean")
    private double rollingTempMean;
    @com.fasterxml.jackson.annotation.JsonProperty("isAnomaly")
    private boolean anomaly;
    @com.fasterxml.jackson.annotation.JsonProperty("anomalyScore")
    private Double anomalyScore;

    private String explanation;

    private LocalDateTime timestamp;
}