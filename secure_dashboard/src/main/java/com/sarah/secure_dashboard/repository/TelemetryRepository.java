package com.sarah.secure_dashboard.repository;

import com.sarah.secure_dashboard.model.TelemetryData;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TelemetryRepository extends JpaRepository<TelemetryData, Long> {
}